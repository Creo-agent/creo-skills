#!/usr/bin/env python3
"""
Localization Dispatcher — Lightweight board poller.
Called by cron every 5 minutes.

Outputs JSON to stdout with work items found.
Does NOT claim items or process them — that's the worker's job.

Worker compliance rules (enforced at spawn):
- Workers MUST follow pipeline steps in EXACT order
- Workers MUST verify output after each step before proceeding
- Workers MUST clear screenshot columns before uploading (no stacking)
- Workers MUST verify loc page belongs to correct parent asset
- Workers MUST escalate failures to WhatsApp group 120363410139911795@g.us
- Workers MUST NOT silently continue with partial/wrong data
"""

import json
import sys
import os
import time
import urllib.request

STATE_FILE = os.path.join(os.path.dirname(__file__), "localization-state.json")
PARENT_BOARD = 18412118203
SUBITEM_BOARD = 18412118857
ALLOWED_GROUPS = ["group_mm522wkt", "group_mm5150b6", "group_mm46vmq2"]

def get_token():
    token_path = os.path.expanduser("~/.openclaw/workspace/.secrets/monday-main-account-token.md")
    with open(token_path) as f:
        for line in f:
            if line.startswith("Token: "):
                return line.split("Token: ")[1].strip()
    raise RuntimeError("Token not found")

def monday_query(token, query):
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        "https://api.monday.com/v2",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": token}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"version": 1, "queue": [], "active": [], "completed": [], "failed": [], "maxConcurrent": 3}

def save_state(state):
    state["updatedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def poll_board(token):
    """Poll for Idle and Re-run Requested items across allowed groups."""
    query = """
    { boards(ids: [%d]) {
        items_page(limit: 100, query_params: {rules: [{column_id: "group", compare_value: %s}]}) {
          cursor items {
            id name group { id title }
            column_values(ids: ["text_mm3ng2f6", "text_mm3nbpfm", "link_mm3npjax", "color_mm3nw9me"]) { id text value }
            subitems {
              id name
              column_values(ids: ["color_mm3nfga0", "color_mm3nzc1r"]) { id text }
            }
          }
        }
      }
    }""" % (PARENT_BOARD, json.dumps(ALLOWED_GROUPS))

    result = monday_query(token, query)
    items = result.get("data", {}).get("boards", [{}])[0].get("items_page", {}).get("items", [])

    work_items = []
    for item in items:
        parent_id = item["id"]
        parent_name = item["name"]
        # Extract parent columns
        figma_key = ""
        frame_name = ""
        figma_url = ""
        asset_type = ""
        for col in item.get("column_values", []):
            if col["id"] == "text_mm3ng2f6": figma_key = col.get("text", "")
            elif col["id"] == "text_mm3nbpfm": frame_name = col.get("text", "")
            elif col["id"] == "link_mm3npjax":
                val = json.loads(col.get("value", "{}") or "{}")
                figma_url = val.get("url", "")
            elif col["id"] == "color_mm3nw9me": asset_type = col.get("text", "")

        for sub in item.get("subitems", []):
            sys_status = ""
            review_status = ""
            for col in sub.get("column_values", []):
                if col["id"] == "color_mm3nfga0": sys_status = col.get("text", "")
                elif col["id"] == "color_mm3nzc1r": review_status = col.get("text", "")

            trigger = None
            if sys_status == "Idle":
                trigger = "new_run"
            elif review_status == "Re-run Requested":
                trigger = "re_run"

            if trigger:
                work_items.append({
                    "subitem_id": sub["id"],
                    "locale": sub["name"],
                    "parent_id": parent_id,
                    "parent_name": parent_name,
                    "figma_key": figma_key,
                    "frame_name": frame_name,
                    "figma_url": figma_url,
                    "asset_type": asset_type,
                    "trigger": trigger,
                    "group": item.get("group", {}).get("title", ""),
                })

    return work_items

def detect_and_reset_orphans(token, state):
    """Find items Running on the board but NOT tracked in state file.
    Reset them to Idle automatically."""
    query = """
    { boards(ids: [%d]) {
        items_page(limit: 100, query_params: {rules: [{column_id: "group", compare_value: %s}]}) {
          items {
            id name
            subitems {
              id name
              column_values(ids: ["color_mm3nfga0"]) { id text }
            }
          }
        }
      }
    }""" % (PARENT_BOARD, json.dumps(ALLOWED_GROUPS))

    result = monday_query(token, query)
    items = result.get("data", {}).get("boards", [{}])[0].get("items_page", {}).get("items", [])
    active_ids = {a["subitem_id"] for a in state.get("active", [])}

    orphans = []
    for item in items:
        for sub in item.get("subitems", []):
            status = ""
            for col in sub.get("column_values", []):
                if col["id"] == "color_mm3nfga0":
                    status = col.get("text", "")
            if status == "Running" and sub["id"] not in active_ids:
                orphans.append({
                    "subitem_id": sub["id"],
                    "locale": sub["name"],
                    "parent_id": item["id"],
                    "parent_name": item["name"],
                })

    # Auto-reset orphans to Idle
    reset_count = 0
    for orphan in orphans:
        try:
            mutation = 'mutation { change_column_value(item_id: %s, board_id: %d, column_id: "color_mm3nfga0", value: "{\\"index\\": 17}") { id } }' % (orphan["subitem_id"], SUBITEM_BOARD)
            monday_query(token, mutation)
            reset_count += 1
        except Exception as e:
            orphan["reset_error"] = str(e)

    return orphans, reset_count

def main():
    token = get_token()
    state = load_state()

    # Check for stale active workers (>35 min)
    stale = []
    now = time.time()
    for active in state.get("active", []):
        started = active.get("started_at", 0)
        if now - started > 35 * 60:
            stale.append(active)

    # Detect and auto-reset orphaned Running items
    orphans, orphans_reset = detect_and_reset_orphans(token, state)

    # Also handle stale active workers — reset on board and remove from state
    for s in stale:
        try:
            mutation = 'mutation { change_column_value(item_id: %s, board_id: %d, column_id: "color_mm3nfga0", value: "{\\"index\\": 17}") { id } }' % (s["subitem_id"], SUBITEM_BOARD)
            monday_query(token, mutation)
        except:
            pass
    if stale:
        state["active"] = [a for a in state.get("active", []) if a["subitem_id"] not in {s["subitem_id"] for s in stale}]
        save_state(state)

    # Poll board for new work (re-poll after resets)
    work_items = poll_board(token)

    # Filter out items already in active/queue
    active_ids = {a["subitem_id"] for a in state.get("active", [])}
    queue_ids = {q["subitem_id"] for q in state.get("queue", [])}
    new_items = [w for w in work_items if w["subitem_id"] not in active_ids and w["subitem_id"] not in queue_ids]

    # Group by parent to enforce same-asset sequential processing
    active_parents = {a["parent_id"] for a in state.get("active", [])}

    output = {
        "new_items": new_items,
        "total_pending": len(work_items),
        "active_count": len(state.get("active", [])),
        "stale_workers_reset": len(stale),
        "orphans_found": len(orphans),
        "orphans_reset": orphans_reset,
        "active_parents": list(active_parents),
        "can_spawn": max(0, state.get("maxConcurrent", 3) - len(state.get("active", []))),
    }

    print(json.dumps(output, indent=2))

def claim_items(token, items, state):
    """Claim items on the board (set Running + Run Started) and update state file."""
    today = time.strftime("%Y-%m-%d")
    claimed = []
    for item in items:
        sid = item["subitem_id"]
        mutation = '''mutation { change_multiple_column_values(
            item_id: %s, board_id: %d,
            column_values: "{\\"color_mm3nfga0\\":{\\"label\\":\\"Running\\"},\\"date_mm3n2gvy\\":{\\"date\\":\\"%s\\"}}",
            create_labels_if_missing: true) { id } }''' % (sid, SUBITEM_BOARD, today)
        try:
            result = monday_query(token, mutation)
            if "data" in result:
                state.setdefault("active", []).append({
                    "subitem_id": sid,
                    "parent_id": item["parent_id"],
                    "locale": item["locale"],
                    "parent_name": item["parent_name"],
                    "started_at": int(time.time()),
                })
                claimed.append(item)
        except Exception as e:
            print(json.dumps({"error": f"Failed to claim {sid}: {e}"}), file=sys.stderr)
    save_state(state)
    return claimed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", type=int, default=0, help="Auto-claim up to N items")
    args = parser.parse_args()

    if args.claim > 0:
        token = get_token()
        state = load_state()
        detect_and_reset_orphans(token, state)
        work_items = poll_board(token)
        # Filter already active
        active_ids = {a["subitem_id"] for a in state.get("active", [])}
        new_items = [w for w in work_items if w["subitem_id"] not in active_ids]
        # Pick from different parents first
        active_parents = {a["parent_id"] for a in state.get("active", [])}
        selected = []
        seen_parents = set()
        # First pass: one per parent
        for item in new_items:
            if len(selected) >= args.claim:
                break
            if item["parent_id"] not in active_parents and item["parent_id"] not in seen_parents:
                selected.append(item)
                seen_parents.add(item["parent_id"])
        # Second pass: fill remaining slots
        for item in new_items:
            if len(selected) >= args.claim:
                break
            if item not in selected and item["parent_id"] not in active_parents:
                selected.append(item)

        claimed = claim_items(token, selected, state)
        print(json.dumps({"claimed": claimed, "remaining": len(new_items) - len(claimed)}, indent=2))
    else:
        main()
