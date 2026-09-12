# Webflow Data API — envelope, tools, action shapes

The Data API MCP tools are how you build headlessly (no Designer canvas). They
all share one envelope shape and a small set of quirks. Read this before your
first call.

## Contents
- [The envelope](#the-envelope)
- [Tool cheat sheet](#tool-cheat-sheet)
- [Action shapes that trip people up](#action-shapes-that-trip-people-up)
- [First call of the session](#first-call-of-the-session)

## The envelope

Most write tools take an envelope with `siteId`, `pageId`, and an `actions`
array. Each action is an object with a `label` plus one action-name key holding
its parameters:

```json
{
  "siteId": "6a0183bc6fe692c9451f0726",
  "pageId": "6a0183c26fe692c9451f07d0",
  "actions": [
    { "label": "create heading style", "create_style": { "...": "..." } }
  ]
}
```

Keep batches small (2–4 actions). Large batches occasionally drop the socket
mid-call; if that happens, retry the actions one at a time.

## Tool cheat sheet

| Tool | Use it for | Phase |
|---|---|---|
| `webflow_guide_tool` | List MCP capabilities. Call **once** per session, first. | 0 |
| `data_sites_tool` | Get site info; `publish_site`. | 1, 8 |
| `data_pages_tool` | Get/list pages, find the page id. | 1 |
| `data_element_tool` | `get_all_elements`, `set_text`, `set_style`, `set_image_asset`, `set_attributes`, `remove_element`. | 1, 5 |
| `data_element_builder` | Insert a new element subtree. Uses **`build_label`** (not `label`); fields are flat in the action — see action shapes below. | 5 |
| `data_style_tool` | `create_style`, `update_style`, `query_styles`, `get_styles`. Base breakpoint only — see gotchas. | 4 |
| `data_assets_tool` | `create_asset` (two-step upload). | 3 |
| `data_scripts_tool` | `set_page_freeform_code` — the path for responsive CSS + JS. | 6 |
| `data_whtml_builder` | `insert_whtml`. Heavily CSS-restricted — avoid for responsive; see gotchas. | rare |

`create_element` type enum includes: Container, Section, DivBlock, Heading,
TextBlock, Paragraph, Button, TextLink, LinkBlock, Image, HtmlEmbed. There is
**no native Navbar type** — build navs from DivBlock/LinkBlock + freeform CSS.

## Action shapes that trip people up

**`publish_site`** needs `site_id` *inside* the action object, not only at the
envelope level:

```json
{ "siteId": "...", "actions": [
  { "label": "publish", "publish_site": { "site_id": "6a0183bc6fe692c9451f0726" } }
] }
```

**`set_page_freeform_code`** takes a raw string and injects it into the page
**head**. Use it for CSS only — `@keyframes`, responsive rules, hover/focus
styles. **Do not put interactive JS here**: head scripts are skipped by Webflow
preview entirely (see gotchas §9). Put JS in a body-level `HtmlEmbed` instead.

**`data_element_builder`** uses **`build_label`** (not `label`) and has a
**flat** action structure — `parent_element_id`, `creation_position`, and
`element_schema` sit at the same level as `build_label`, not nested under any
`create_element` key:

```json
{
  "siteId": "...", "pageId": "...",
  "actions": [{
    "build_label": "Add hero section",
    "parent_element_id": {"component": "<pageId>", "element": "<parentId>"},
    "creation_position": "append",
    "element_schema": {
      "type": "Section",
      "styleNames": ["section_hero"],
      "children": [...]
    }
  }]
}
```

Nest child elements inside `element_schema.children`. One deep nested call is
better than many shallow calls — fewer roundtrips and it lands atomically.

## First call of the session

Call `webflow_guide_tool` once at the very start to load current MCP
capabilities, then never again this session. After that, work from this file.
