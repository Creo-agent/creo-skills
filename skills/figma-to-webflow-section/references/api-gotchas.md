# Webflow Data API — gotchas and workarounds

These are the silent failures. Each one below was discovered by watching a tool
report success while doing the wrong thing (or nothing). Read this before your
first API call — it will save you many wasted round-trips.

## 1. `update_style` silently ignores the `breakpoint` parameter

You can pass `breakpoint: "medium"` (or small/tiny/xxl) to `update_style` and it
returns success — but the property lands on the **base** breakpoint. There is no
error. This means you **cannot write responsive styles through the style tools
at all.**

**Workaround:** put every responsive rule in the freeform code block via
`data_scripts_tool → set_page_freeform_code`, using real `@media` queries. See
`responsive-patterns.md`.

## 2. `data_whtml_builder` CSS is heavily restricted

`insert_whtml` accepts `html` + `css`, but the CSS parser rejects:
- `!important` ("not allowed")
- descendant / nested selectors ("nested selectors not allowed")
- anything but single-class selectors
- media queries not in the exact form `screen and (max-width: N)`

And even valid CSS only styles the inserted fragment, not the page globally.

**Workaround:** don't use this for responsive or global styling. Use
`set_page_freeform_code`, which accepts full CSS including `!important`,
descendant selectors, and any media query syntax.

## 3. `set_text` fails on DivBlock / Block

Returns "This element doesn't support text." Blocks are containers, not text
nodes.

**Workarounds:**
- Create text-bearing elements as **`TextLink`** — it accepts text natively.
- Or, if a DivBlock already exists, get its child `String` node id from
  `get_all_elements` and `set_text` on that id.

## 4. `set_attributes` for `alt` text returns an internal error

Setting image `alt` via the Data API is unreliable — it has returned "An
internal error occurred." Don't assume alt text got set.

**Workaround:** set alt via the `use_figma` plugin path, or explicitly flag to
the user that alt text still needs to be added, rather than silently shipping an
inaccessible image.

## 5. Positioning: an element with both `left` and `right` set is pinned

If a decorative/absolute element has both `left` and `right` (or both `top` and
`bottom`) defined, it stretches/pins across that axis — often landing on top of
your text. Release the side you don't want by setting it to `auto` (e.g.
`left: auto` so only `right` anchors it).

## 6. Large `create_element` / style batches can drop the socket

A multi-action batch occasionally fails with a closed socket and no result.

**Workaround:** retry the actions one at a time. Keep batches to 2–4 actions.

## 7. Leftover embed/placeholder elements

If you insert a placeholder DivBlock or whtml embed during construction, it can
linger in the DOM after you're done. Clean up with
`data_element_tool → remove_element` before publishing.

## 8. `publish_site` needs `site_id` inside the action

Envelope-level `siteId` is not enough — the `publish_site` action object also
needs its own `site_id`. Omit it and publish fails.

## 9. Head freeform code `<script>` does NOT execute in Webflow preview

`set_page_freeform_code` with `location: "head"` only runs on the **published**
page. Webflow's preview mode skips head-injected scripts entirely. This means any
click handler, tab switcher, or other JS interaction you put in the head block
will be completely dead in preview, and only come alive after publishing.

**Workaround:** put interactive JavaScript inside a body-level **`HtmlEmbed`**
element appended as the last child of the section. Inline scripts execute in
document order — the section's elements are already in the DOM above the script,
so no `DOMContentLoaded` is needed. Use an IIFE to avoid polluting global scope:

```html
<script>
(function(){
  var tabs = document.querySelectorAll('.section_tab');
  tabs.forEach(function(t){ t.addEventListener('click', function(){ ... }); });
})();
</script>
```

Create it via `data_element_builder`:
```json
{
  "type": "HtmlEmbed",
  "custom_code": "<script>(function(){ ... })();<\/script>"
}
```

**CSS always stays in the head.** Freeform `<style>` blocks render correctly in
the Designer canvas, preview, and published. Only `<script>` needs to move to
the body. The split is: `set_page_freeform_code` (head) for CSS, `HtmlEmbed`
child of the section for JS.

## 10. When building similar elements, inspect first — don't guess attributes

When a section has repeated elements (tabs, pills, cards) that need `data-*`
attributes, class combos, or `aria-*` roles, **don't guess the attribute names
or values**. Call `get_all_elements` (depth ≥ 4) on the page first to inspect an
existing element of the same type, then replicate its full attribute set exactly.

This matters because:
- `data-tab`, `data-w-id`, `role`, `aria-controls` must match what the JS or
  Webflow's own runtime expects — a typo silently breaks the interaction.
- Style-name combos on sibling elements (e.g. `["nav_tab", "nav_tab-active"]` on
  the first item) are invisible from the design but critical for the initial state.

Pattern: `get_all_elements` → find the reference element → copy its `attributes`
and `styleNames` exactly into each new sibling element.

## 11. `w-embed` auto-class inflates inline elements nested inside buttons

Webflow automatically adds `w-embed` to every `HtmlEmbed` element, setting
`width: 100%; display: block`. If you nest an HtmlEmbed inside an `inline-flex`
button (e.g. an inline SVG icon arrow), the `w-embed` rule expands it to full
width and collapses the button into a tall oval.

**Preferred fix:** don't use an HtmlEmbed child inside a button. Build icons
programmatically in JS using `createElementNS` and inject them from the
section's body-level script, so the button's DOM contains a plain `<span>` or
`<div>`, not an HtmlEmbed:

```js
var wrap = document.createElement('span');
var svg  = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
// … setAttribute calls …
wrap.appendChild(svg); btn.appendChild(wrap);
```

**CSS safety net** for any button with children — add this to the head freeform block:
```css
.section_name .m_button { display: inline-flex !important; width: auto !important }
```

## 12. `w--current` on static Link elements triggers Webflow's default styling

Webflow uses `w--current` as an internal system class for active nav links.
Applying it to any `<a>` element — via `style_names` in the Data API — causes
Webflow to inject **bold font + underline** on that element regardless of your
own CSS. There is no reliable way to override this from freeform code.

**Rule:** never use `w--current` for custom active states. Create a named
Webflow class via `create_style` instead (e.g. `.x_tab-active`), apply it to
the initially-active element in `style_names` at build time, and toggle it in
the body-level script at runtime. See `webflow-active-states.md`.

---

**Meta-rule:** when a Webflow write tool reports success but you can't see the
effect, suspect a silent no-op (especially anything breakpoint- or
attribute-related) and reach for the freeform-code path instead.
