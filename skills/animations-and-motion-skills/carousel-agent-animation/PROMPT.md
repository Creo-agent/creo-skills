# Carousel Agent Animation — Run Procedure

## 1 · Collect inputs

Ask for anything not already in the prompt:

| Input | Notes |
|---|---|
| **Figma file URL** | Full URL, e.g. `https://www.figma.com/design/XXXX/...?node-id=123-456` |
| **Agent labels** | One title per card. Typically 5 for carousel, 3 for floating. |
| **Animation style** | `carousel` or `floating`. Default: carousel. |
| **Output folder** | Where to write files. Default: current working directory. |
| **Figma token** | Only if Figma MCP is not connected. Generate at figma.com → Settings → Personal Access Tokens (starts with `figd_`). |
| **Images** | If the user already has images (PNG or SVG), copy them to `{output}/images/` and skip Steps 2–3. |

---

## 2 · Parse the Figma URL

```
https://www.figma.com/design/{FILE_KEY}/Title?node-id={NODE_ID_DASHED}
```

- `FILE_KEY` — segment after `/design/` or `/file/`
- `NODE_ID` — `node-id` query param; convert `-` → `:` for API calls (e.g. `223-3789` → `223:3789`)

---

## 3 · Read design values from Figma

**If Figma MCP is connected** — load the `figma-use` skill, then inspect the node tree with a `use_figma` script.

**Otherwise** — REST API:

```bash
curl -s -H "X-Figma-Token: {TOKEN}" \
  "https://api.figma.com/v1/files/{FILE_KEY}/nodes?ids={NODE_ID}" \
  | python3 -m json.tool > /tmp/figma_nodes.json
```

Extract per card: bounding box (all three states), corner radius, fill, border, shadow, font family/size/weight/letter-spacing.

**Derive carousel values:**

| Variable | Formula |
|---|---|
| `SCALE_FACTOR` | `260 / figma_center_card_width` |
| `CARD_H` | `figma_center_card_height × SCALE_FACTOR` |
| `BORDER_RADIUS` | `figma_corner_radius × SCALE_FACTOR` |
| `NEAR_SCALE` | `figma_near_width / figma_center_width` |
| `FAR_SCALE` | `figma_far_width / figma_center_width` |
| `NEAR_TX` | `figma_near_center_offset × SCALE_FACTOR` |
| `FAR_TX` | `figma_far_center_offset × SCALE_FACTOR` |

**Proven defaults** (use when Figma values are unavailable):

```
CARD_W=260  CARD_H=297  BORDER_RADIUS=14px
IMAGE_AREA: 246×231px, border-radius 9px, bg #F3F4F5
LABEL: Poppins 500/700, 18px, letter-spacing -0.18px
NEAR_SCALE=0.9  FAR_SCALE=0.826  NEAR_TX=206px  FAR_TX=401px
BORDER: 1px solid rgba(124,123,123,1.0)
SHADOW (center): 0 8px 32px rgba(0,0,0,0.14), 0 2px 8px rgba(0,0,0,0.07)
```

---

## 4 · Download images

```bash
# Get export URLs (node IDs comma-separated, using : separator)
curl -s -H "X-Figma-Token: {TOKEN}" \
  "https://api.figma.com/v1/images/{FILE_KEY}?ids={NODE_IDS}&format=png&scale=2" \
  | python3 -m json.tool > /tmp/figma_images.json

# Download each
curl -sL "{URL}" -o "{output}/images/{slug}.png"
```

Slugify labels for filenames: "Lead Qualifier" → `lead-qualifier.png`.
Verify each file is non-zero. If the user provides SVG files, copy them directly — they work fine in `<img>` tags.

---

## 5A · Generate — Carousel style

Produces `{name}.html`, `{name}.css`, `{name}.js`.

### {name}.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{name}.css">
</head>
<body>
  <div class="carousel-wrapper">
    <div class="carousel" id="carousel">
      <!-- repeat for each agent, data-index 0…N-1 -->
      <div class="card" data-index="0">
        <div class="card__image"><img src="images/{slug-0}.{ext}" alt="{Label 0}"></div>
        <div class="card__footer"><span class="card__label">{Label 0}</span></div>
      </div>
    </div>
  </div>
  <script src="{name}.js"></script>
</body>
</html>
```

### {name}.css
```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: #ffffff;
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh;
  font-family: 'Poppins', sans-serif;
  overflow-x: hidden; /* clips off-screen far cards without clipping shadows */
}

.carousel-wrapper { width: 1000px; }

.carousel {
  position: relative;
  height: 400px;  /* CARD_H + ~100px shadow room */
  overflow: visible; /* NEVER hidden — clips the center shadow */
}

.card {
  position: absolute;
  left: calc(50% - 130px); /* 50% - CARD_W/2 */
  top:  calc(50% - 148.5px); /* 50% - CARD_H/2 */
  width: 260px; height: 297px;
  padding: 7px 7px 18px; gap: 14px;
  display: flex; flex-direction: column;
  border-radius: 14px;
  background: #ffffff;
  border: 1px solid rgba(124, 123, 123, 1.0);
  overflow: hidden;
  will-change: transform, box-shadow;
  transition:
    transform        0.95s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow       0.95s cubic-bezier(0.4, 0, 0.2, 1),
    background-color 0.95s cubic-bezier(0.4, 0, 0.2, 1);
}
.card.no-transition { transition: none !important; }

.card__image {
  width: 246px; height: 231px;
  border-radius: 9px; background: #F3F4F5;
  overflow: hidden; flex-shrink: 0;
}
.card__image img { width: 100%; height: 100%; object-fit: cover; object-position: top center; display: block; }

.card__footer { height: 27px; display: flex; align-items: center; padding: 0 7px; flex-shrink: 0; }
.card__label {
  font-family: 'Poppins', sans-serif;
  font-size: 18px; font-weight: 500; line-height: 1.5; letter-spacing: -0.18px; color: #000;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Slot states — pure scale + translate; NO opacity changes */
.card[data-slot="-2"] { transform: translateX(-401px) scale(0.826); z-index: 1; box-shadow: none; }
.card[data-slot="-1"] { transform: translateX(-206px) scale(0.9);   z-index: 3; box-shadow: none; }
.card[data-slot="0"]  {
  transform: translateX(0) scale(1.0); z-index: 5;
  box-shadow: 0 8px 32px rgba(0,0,0,0.14), 0 2px 8px rgba(0,0,0,0.07);
}
.card[data-slot="0"] .card__label { font-weight: 700; }
.card[data-slot="1"]  { transform: translateX(206px)  scale(0.9);   z-index: 3; box-shadow: none; }
.card[data-slot="2"]  { transform: translateX(401px)  scale(0.826); z-index: 1; box-shadow: none; }
```

### {name}.js
```js
const SLIDE_MS  = 950;   // match CSS transition duration
const HOLD_MS   = 2200;  // time each card holds at center
const NUM_CARDS = 5;     // update to card count

let activeIndex = 0;
const cards = Array.from(document.querySelectorAll('.card'));

function slotOf(i) { return ((i - activeIndex + NUM_CARDS + 2) % NUM_CARDS) - 2; }
function applySlots() { cards.forEach((c, i) => c.dataset.slot = slotOf(i)); }

function advance() {
  const ti = cards.findIndex((_, i) => slotOf(i) === -2);
  activeIndex = (activeIndex + 1) % NUM_CARDS;
  if (ti !== -1) {
    cards[ti].classList.add('no-transition');
    cards[ti].getBoundingClientRect(); // force reflow before slot change
    cards[ti].dataset.slot = '2';
  }
  applySlots();
  if (ti !== -1) requestAnimationFrame(() => requestAnimationFrame(() => cards[ti].classList.remove('no-transition')));
}

// Snap initial positions with no animation (prevents entrance flash)
cards.forEach(c => c.classList.add('no-transition'));
applySlots();
document.body.getBoundingClientRect();
requestAnimationFrame(() => requestAnimationFrame(() => {
  cards.forEach(c => c.classList.remove('no-transition'));
  setInterval(advance, HOLD_MS + SLIDE_MS);
}));
```

**Why this works:** slots ±2 are both off-screen. The teleporting card gets `no-transition`, jumps from slot −2 to slot +2 (both invisible), then transitions re-enable after a double-rAF — making the loop truly seamless with zero flash.

---

## 5B · Generate — Floating agents style

Produces `{name}.html`, `{name}.css`, `{name}.js`. Standard setup: 3 agents, 1 background photo, 1 frosted-glass chat bar.

### {name}.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{name}.css">
</head>
<body>
  <div class="scene-wrapper">
    <div class="scene" id="scene">
      <img class="woman" src="images/woman.png" alt="">
      <div class="agent-card card-a" id="card-a">
        <div class="card-avatar" style="background:{COLOR_A}"><img src="images/{avatar-a}.{ext}" alt=""></div>
        <div class="card-body">
          <p class="card-name">{Agent A, Role}</p>
          <p class="card-sub" id="sub-a">{Agent A status}</p>
        </div>
      </div>
      <div class="agent-card card-b" id="card-b">
        <div class="card-avatar" style="background:{COLOR_B}"><img src="images/{avatar-b}.{ext}" alt=""></div>
        <div class="card-body">
          <p class="card-name">{Agent B, Role}</p>
          <p class="card-sub" id="sub-b">{Agent B status}</p>
        </div>
      </div>
      <div class="agent-card card-c" id="card-c">
        <div class="card-avatar" style="background:{COLOR_C}"><img src="images/{avatar-c}.{ext}" alt=""></div>
        <div class="card-body">
          <p class="card-name">{Agent C, Role}</p>
          <p class="card-sub" id="sub-c">{Agent C status}</p>
        </div>
      </div>
      <div class="chat-bar" id="chat-bar">
        <img class="chat-avatar" src="images/avatar-circle.png" alt="">
        <div class="chat-field">
          <span class="chat-text" id="chat-text"></span>
          <span class="chat-cursor" id="chat-cursor"></span>
        </div>
        <div class="chat-bottom">
          <span class="chat-icon"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="1.5" y="1.5" width="5" height="5" rx="1.2" stroke="#676879" stroke-width="1.4"/><rect x="13.5" y="1.5" width="5" height="5" rx="1.2" stroke="#676879" stroke-width="1.4"/><rect x="1.5" y="13.5" width="5" height="5" rx="1.2" stroke="#676879" stroke-width="1.4"/><rect x="13.5" y="13.5" width="5" height="5" rx="1.2" stroke="#676879" stroke-width="1.4"/><line x1="6.5" y1="4" x2="13.5" y2="4" stroke="#676879" stroke-width="1.4"/><line x1="6.5" y1="16" x2="13.5" y2="16" stroke="#676879" stroke-width="1.4"/><line x1="4" y1="6.5" x2="4" y2="13.5" stroke="#676879" stroke-width="1.4"/><line x1="16" y1="6.5" x2="16" y2="13.5" stroke="#676879" stroke-width="1.4"/></svg></span>
          <span class="chat-icon"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M16 9.5L9.2 16.3C7.76 17.74 5.44 17.74 4 16.3C2.56 14.86 2.56 12.54 4 11.1L11.5 3.6C12.44 2.66 13.96 2.66 14.9 3.6C15.84 4.54 15.84 6.06 14.9 7L7.9 14C7.46 14.44 6.74 14.44 6.3 14C5.86 13.56 5.86 12.84 6.3 12.4L13 5.7" stroke="#676879" stroke-width="1.45" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
          <div class="chat-spacer"></div>
          <button class="send-btn" id="send-btn" aria-label="Send"><svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 17V5M11 5L5 11M11 5L17 11" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        </div>
      </div>
    </div>
  </div>
  <script src="{name}.js"></script>
</body>
</html>
```

### {name}.css
```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; height: 100%; background: #1a1a1a; overflow: hidden; font-family: 'Figtree', sans-serif; }
.scene-wrapper { position: fixed; inset: 0; overflow: hidden; background: #1a1a1a; }
.scene { position: absolute; width: 1280px; height: 734px; background: #ecdfce; border-radius: 32px; overflow: hidden; transform-origin: top left; }
.woman { position: absolute; left: 342px; top: 17px; width: 542px; height: 808px; object-fit: cover; pointer-events: none; z-index: 1; }
.agent-card { position: absolute; background: #fff; border-radius: 17px; display: flex; align-items: center; gap: 18px; padding: 10px 14px 10px 10px; box-shadow: 0 8px 48px rgba(0,0,0,0.15); z-index: 3; opacity: 0; will-change: transform, opacity; }
.card-avatar { border-radius: 14px; overflow: hidden; flex-shrink: 0; }
.card-avatar img { width: 100%; height: 100%; object-fit: cover; object-position: center top; display: block; }
.card-body { display: flex; flex-direction: column; }
.card-name { font-weight: 600; color: #323338; letter-spacing: -0.02em; white-space: nowrap; }
.card-sub  { font-weight: 400; color: #676879; letter-spacing: -0.01em; white-space: nowrap; }
/* Card positions — adjust to match your design */
.card-a { top:  54px; left: 805px; width: 362px; gap: 17px; padding: 9px 10px; }
.card-b { top: 244px; left:  29px; width: 482px; gap: 30px; padding: 10px 12px; }
.card-c { top: 360px; left: 794px; width: 373px; gap: 30px; padding: 10px 12px; }
.card-a .card-avatar { width: 82px; height: 82px; border-radius: 12px; }
.card-b .card-avatar, .card-c .card-avatar { width: 95px; height: 95px; border-radius: 14px; }
.card-a .card-body { gap: 5px; } .card-a .card-name { font-size: 21px; } .card-a .card-sub { font-size: 17px; }
.card-b .card-body, .card-c .card-body { gap: 7px; }
.card-b .card-name, .card-c .card-name { font-size: 24px; }
.card-b .card-sub,  .card-c .card-sub  { font-size: 20px; }
@keyframes floatA { 0%,100%{transform:translateY(0)}  50%{transform:translateY(-7px)} }
@keyframes floatB { 0%,100%{transform:translateY(0)}  50%{transform:translateY(-9px)} }
@keyframes floatC { 0%,100%{transform:translateY(0)}  50%{transform:translateY(-6px)} }
.card-a.floating { animation: floatA 3.2s ease-in-out infinite; }
.card-b.floating { animation: floatB 3.8s ease-in-out infinite; }
.card-c.floating { animation: floatC 3.5s ease-in-out infinite; }
.chat-bar { position: absolute; left: 239px; top: 528px; width: 776px; height: 186px; background: rgba(255,255,255,0.42); backdrop-filter: blur(35px); -webkit-backdrop-filter: blur(35px); border: 1.8px solid rgba(255,255,255,0.9); border-radius: 14px; z-index: 4; overflow: hidden; }
.chat-avatar { position: absolute; left: 18px; top: 22px; width: 73px; height: 73px; border-radius: 50%; object-fit: cover; }
.chat-field { position: absolute; left: 108px; top: 18px; right: 24px; height: 86px; display: flex; align-items: center; font-size: 27px; font-weight: 400; color: #323338; letter-spacing: -0.02em; overflow: hidden; }
.chat-text { white-space: nowrap; }
.chat-cursor { display: inline-block; width: 2px; height: 30px; background: #323338; margin-left: 2px; vertical-align: middle; border-radius: 1px; }
.chat-cursor.blinking { animation: blink 1s step-end infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
.chat-bottom { position: absolute; left: 0; bottom: 14px; right: 0; height: 55px; display: flex; align-items: center; padding: 0 24px; gap: 14px; }
.chat-icon { color: #676879; opacity: 0.7; cursor: default; user-select: none; }
.chat-spacer { flex: 1; }
.send-btn { width: 52px; height: 52px; border-radius: 50%; background: #0b6e6e; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 12px rgba(11,110,110,0.3); flex-shrink: 0; }
.send-btn.pulse { animation: sendPulse 0.45s cubic-bezier(0.36,0.07,0.19,0.97) forwards; }
@keyframes sendPulse { 0%{transform:scale(1)} 30%{transform:scale(0.86)} 65%{transform:scale(1.14)} 100%{transform:scale(1)} }
.card-sub .dot { display: inline-block; opacity: 0; animation: dotAppear 1.5s ease-in-out infinite; }
.card-sub .dot:nth-child(1){animation-delay:0s} .card-sub .dot:nth-child(2){animation-delay:.25s} .card-sub .dot:nth-child(3){animation-delay:.5s}
@keyframes dotAppear { 0%,100%{opacity:0} 40%,70%{opacity:1} }
.card-sub.shimmer { background: linear-gradient(90deg,#676879 0%,#676879 30%,#a8aabc 50%,#676879 70%,#676879 100%); background-size: 250% 100%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; animation: textShimmer 2.8s ease-in-out infinite; }
@keyframes textShimmer { 0%{background-position:200% center} 100%{background-position:-200% center} }
```

### {name}.js
```js
const MESSAGE       = "{typewriter prompt text}";
const TYPE_SPEED_MS = 55;
const HOLD_MS       = 3000;

const chatText = document.getElementById('chat-text');
const cursor   = document.getElementById('chat-cursor');
const sendBtn  = document.getElementById('send-btn');
const cardA = document.getElementById('card-a');
const cardB = document.getElementById('card-b');
const cardC = document.getElementById('card-c');
const subA  = document.getElementById('sub-a');
const subB  = document.getElementById('sub-b');
const subC  = document.getElementById('sub-c');

function makeDots(el, base) {
  el.innerHTML = base + '<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>';
}
function startThinking() { makeDots(subA, '{Agent A status}'); makeDots(subB, '{Agent B status}'); subC.classList.add('shimmer'); }
function stopThinking()  { subA.innerHTML = '{Agent A status}'; subB.innerHTML = '{Agent B status}'; subC.classList.remove('shimmer'); }

const scene = document.getElementById('scene');
const W = 1280, H = 734;
function scaleScene() {
  const s = Math.min(window.innerWidth / W, window.innerHeight / H) * 0.94;
  scene.style.transform = `scale(${s})`;
  scene.style.left = (window.innerWidth  - W * s) / 2 + 'px';
  scene.style.top  = (window.innerHeight - H * s) / 2 + 'px';
}
scaleScene();
window.addEventListener('resize', scaleScene);

const wait = ms => new Promise(r => setTimeout(r, ms));

function springIn(el, from) {
  el.style.transition = 'none'; el.style.transform = from; el.style.opacity = '0'; el.classList.remove('floating');
  el.getBoundingClientRect();
  el.style.transition = 'transform 0.65s cubic-bezier(0.34,1.56,0.64,1), opacity 0.4s ease';
  el.style.transform  = 'translateX(0) translateY(0)'; el.style.opacity = '1';
}
function springOut(el, to) {
  el.classList.remove('floating');
  el.style.transition = 'transform 0.5s cubic-bezier(0.55,0,1,0.45), opacity 0.4s ease';
  el.style.transform  = to; el.style.opacity = '0';
}

function typeWriter(text) {
  return new Promise(resolve => {
    let i = 0; cursor.classList.add('blinking');
    (function typeNext() {
      if (i < text.length) { chatText.textContent += text[i++]; setTimeout(typeNext, TYPE_SPEED_MS + Math.random()*30-10); }
      else { cursor.classList.remove('blinking'); resolve(); }
    })();
  });
}

async function runLoop() {
  while (true) {
    await typeWriter(MESSAGE); await wait(300);
    sendBtn.classList.add('pulse'); await wait(450); sendBtn.classList.remove('pulse'); await wait(150);
    springIn(cardA, 'translateX(180px) translateY(-80px)');  await wait(180);
    springIn(cardB, 'translateX(-200px) translateY(0px)');   await wait(180);
    springIn(cardC, 'translateX(160px) translateY(40px)');
    await wait(700);
    cardA.classList.add('floating'); cardB.classList.add('floating'); cardC.classList.add('floating');
    startThinking();
    await wait(HOLD_MS);
    stopThinking();
    springOut(cardA, 'translateX(200px) translateY(-80px)');  await wait(120);
    springOut(cardB, 'translateX(-220px) translateY(0px)');   await wait(120);
    springOut(cardC, 'translateX(180px) translateY(40px)');
    await wait(550);
    chatText.textContent = ''; cursor.classList.add('blinking'); await wait(600);
  }
}

[cardA, cardB, cardC].forEach(c => { c.style.opacity = '0'; c.style.transform = 'translateX(0) translateY(0)'; });
setTimeout(runLoop, 400);
```

---

## 6 · Verify

1. `python3 -m http.server 8765` from the output folder
2. Open `http://localhost:8765/{name}.html`
3. Check: images load, animation loops cleanly, no console errors
4. Take a screenshot and share with the user

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Figma API 403 | Token expired — ask user to regenerate at figma.com → Settings → Personal Access Tokens |
| Image 404 | Node IDs must use `:` in API calls, not `-` |
| Shadow clipped (carousel) | `.carousel` must have `overflow: visible`; use `body { overflow-x: hidden }` for h-scroll |
| Cards wrong stacking | z-index must be: slot 0 = 5, slot ±1 = 3, slot ±2 = 1 |
| Entrance flash | Initial `applySlots()` must run while all cards have `.no-transition`; double-rAF before removing |
| Floating scene too small | Increase the `* 0.94` multiplier in `scaleScene()` |
| SVG not filling image area | Add `object-fit: cover; width: 100%; height: 100%` to the `<img>` |
