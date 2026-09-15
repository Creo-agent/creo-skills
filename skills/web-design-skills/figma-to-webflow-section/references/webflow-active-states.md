# Active state management in Webflow

Managing "selected", "active", or "current" state on elements (tabs, pills, nav
links, cards) is one of the most common interactive requirements. There are three
distinct cases — know which one applies before reaching for a solution.

---

## The three cases

### Case 1 — CSS-only hover / focus state

When the active appearance is triggered by the user interacting with *that
specific element* (hover, keyboard focus), CSS pseudo-classes are enough. Write
these in the head freeform block; no JS and no Webflow class needed:

```css
.x_tab:hover       { background-color: rgba(0,0,0,.04) }
.x_input:focus-within { border-color: var(--accent) }
```

### Case 2 — Single-select active (click one, deactivate the rest)

This is the tabs/pills pattern: exactly one item is active at a time. This needs
a real Webflow class and a body-level script.

**Step 1 — Create the active class in Phase 4 via `create_style`:**

```
selector:   .x_tab-active
properties: background-color, color, box-shadow (whatever the design specifies)
```

Creating it as a real Webflow class (not just a freeform CSS selector) means:
- It is **visible in the Designer canvas** — future sessions can see which
  element holds the active state at a glance.
- It appears in `styleNames` when `get_all_elements` is called — so the
  element's initial state is self-documenting.

**Step 2 — Apply it to the initially-active element in Phase 5 (`style_names`):**

```json
{ "type": "Link", "styleNames": ["x_tab", "x_tab-active"], "attributes": {"data-tab": "Marketing"} }
```

**Step 3 — Toggle it at runtime (body HtmlEmbed, Phase 6):**

```html
<script>
(function(){
  var items = document.querySelectorAll('.x_tab');
  items.forEach(function(item){
    item.addEventListener('click', function(e){
      e.preventDefault();
      items.forEach(function(x){ x.classList.remove('x_tab-active') });
      this.classList.add('x_tab-active');
    });
  });
})();
</script>
```

### Case 3 — Multi-select toggle (each item toggles independently)

Same pattern as Case 2, but the click handler only toggles `this`:

```js
item.addEventListener('click', function(e){
  e.preventDefault();
  this.classList.toggle('x_item-active');
});
```

---

## Why `w--current` is wrong for custom active states

`w--current` is Webflow's internal system class for the currently-active nav
link. Applying it to any `<a>` element — via `style_names` in the Data API, or
directly in the Designer — causes Webflow's runtime to inject **bold font +
underline** on that element, regardless of what your freeform CSS says.

There is no reliable way to override this from freeform code. The behaviour
comes from Webflow's own stylesheet, which loads after yours and wins specificity.

**Rule: never use `w--current` for custom active states. Always use `create_style`.**

This is documented as gotcha §12 in `api-gotchas.md`.

---

## The three-surface test

The correct active-state setup should behave correctly in all three surfaces:

| Surface | What you see |
|---|---|
| Designer canvas | Initial active element shows the active class (real Webflow class → visible) |
| Preview | Clicking tabs/pills works (body embed script executes in preview) |
| Published | Everything works |

If interactions work on published but not preview → JS is in the head freeform
block. Move it to a body HtmlEmbed (see `api-gotchas.md` §9).

If the active element shows bold+underline instead of your design → you used
`w--current`. Replace it with a custom class via `create_style`.

If the Designer shows no active state at all → the active class is only in the
freeform `<style>` block, not a real Webflow class. Create it with `create_style`
and apply via `style_names`.
