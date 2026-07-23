# Easing Functions Reference

All functions take `x: number` (0–1) and return `number` (0–1).
Source: [easings.net](https://easings.net) / github.com/ai/easings.net

## Shared constants (used in JS implementations)

```js
const c1 = 1.70158;
const c2 = c1 * 1.525;
const c3 = c1 + 1;       // 2.70158
const c4 = (2 * Math.PI) / 3;
const c5 = (2 * Math.PI) / 4.5;
```

---

## linear

```js
(x) => x
```
CSS: `linear`

---

## Sine

### easeInSine
```js
function easeInSine(x) {
  return 1 - Math.cos((x * Math.PI) / 2);
}
```
CSS: `cubic-bezier(0.12, 0, 0.39, 0)`

### easeOutSine
```js
function easeOutSine(x) {
  return Math.sin((x * Math.PI) / 2);
}
```
CSS: `cubic-bezier(0.61, 1, 0.88, 1)`

### easeInOutSine
```js
function easeInOutSine(x) {
  return -(Math.cos(Math.PI * x) - 1) / 2;
}
```
CSS: `cubic-bezier(0.37, 0, 0.63, 1)`

---

## Quad

### easeInQuad
```js
function easeInQuad(x) {
  return x * x;
}
```
CSS: `cubic-bezier(0.11, 0, 0.5, 0)`

### easeOutQuad
```js
function easeOutQuad(x) {
  return 1 - (1 - x) * (1 - x);
}
```
CSS: `cubic-bezier(0.5, 1, 0.89, 1)`

### easeInOutQuad
```js
function easeInOutQuad(x) {
  return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;
}
```
CSS: `cubic-bezier(0.45, 0, 0.55, 1)`

---

## Cubic

### easeInCubic
```js
function easeInCubic(x) {
  return x * x * x;
}
```
CSS: `cubic-bezier(0.32, 0, 0.67, 0)`

### easeOutCubic
```js
function easeOutCubic(x) {
  return 1 - Math.pow(1 - x, 3);
}
```
CSS: `cubic-bezier(0.33, 1, 0.68, 1)`

### easeInOutCubic
```js
function easeInOutCubic(x) {
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
}
```
CSS: `cubic-bezier(0.65, 0, 0.35, 1)`

---

## Quart

### easeInQuart
```js
function easeInQuart(x) {
  return x * x * x * x;
}
```
CSS: `cubic-bezier(0.5, 0, 0.75, 0)`

### easeOutQuart
```js
function easeOutQuart(x) {
  return 1 - Math.pow(1 - x, 4);
}
```
CSS: `cubic-bezier(0.25, 1, 0.5, 1)`

### easeInOutQuart
```js
function easeInOutQuart(x) {
  return x < 0.5 ? 8 * x * x * x * x : 1 - Math.pow(-2 * x + 2, 4) / 2;
}
```
CSS: `cubic-bezier(0.76, 0, 0.24, 1)`

---

## Quint

### easeInQuint
```js
function easeInQuint(x) {
  return x * x * x * x * x;
}
```
CSS: `cubic-bezier(0.64, 0, 0.78, 0)`

### easeOutQuint
```js
function easeOutQuint(x) {
  return 1 - Math.pow(1 - x, 5);
}
```
CSS: `cubic-bezier(0.22, 1, 0.36, 1)`

### easeInOutQuint
```js
function easeInOutQuint(x) {
  return x < 0.5 ? 16 * x * x * x * x * x : 1 - Math.pow(-2 * x + 2, 5) / 2;
}
```
CSS: `cubic-bezier(0.83, 0, 0.17, 1)`

---

## Expo

### easeInExpo
```js
function easeInExpo(x) {
  return x === 0 ? 0 : Math.pow(2, 10 * x - 10);
}
```
CSS: `cubic-bezier(0.7, 0, 0.84, 0)`

### easeOutExpo
```js
function easeOutExpo(x) {
  return x === 1 ? 1 : 1 - Math.pow(2, -10 * x);
}
```
CSS: `cubic-bezier(0.16, 1, 0.3, 1)`

### easeInOutExpo
```js
function easeInOutExpo(x) {
  return x === 0 ? 0
    : x === 1 ? 1
    : x < 0.5 ? Math.pow(2, 20 * x - 10) / 2
    : (2 - Math.pow(2, -20 * x + 10)) / 2;
}
```
CSS: `cubic-bezier(0.87, 0, 0.13, 1)`

---

## Circ

### easeInCirc
```js
function easeInCirc(x) {
  return 1 - Math.sqrt(1 - Math.pow(x, 2));
}
```
CSS: `cubic-bezier(0.55, 0, 1, 0.45)`

### easeOutCirc
```js
function easeOutCirc(x) {
  return Math.sqrt(1 - Math.pow(x - 1, 2));
}
```
CSS: `cubic-bezier(0, 0.55, 0.45, 1)`

### easeInOutCirc
```js
function easeInOutCirc(x) {
  return x < 0.5
    ? (1 - Math.sqrt(1 - Math.pow(2 * x, 2))) / 2
    : (Math.sqrt(1 - Math.pow(-2 * x + 2, 2)) + 1) / 2;
}
```
CSS: `cubic-bezier(0.85, 0, 0.15, 1)`

---

## Back  _(slight overshoot)_

### easeInBack
```js
function easeInBack(x) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return c3 * x * x * x - c1 * x * x;
}
```
CSS: `cubic-bezier(0.36, 0, 0.66, -0.56)`

### easeOutBack
```js
function easeOutBack(x) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
}
```
CSS: `cubic-bezier(0.34, 1.56, 0.64, 1)`

### easeInOutBack
```js
function easeInOutBack(x) {
  const c1 = 1.70158;
  const c2 = c1 * 1.525;
  return x < 0.5
    ? (Math.pow(2 * x, 2) * ((c2 + 1) * 2 * x - c2)) / 2
    : (Math.pow(2 * x - 2, 2) * ((c2 + 1) * (x * 2 - 2) + c2) + 2) / 2;
}
```
CSS: `cubic-bezier(0.68, -0.6, 0.32, 1.6)`

---

## Elastic  _(oscillates — no CSS equivalent)_

### easeInElastic
```js
function easeInElastic(x) {
  const c4 = (2 * Math.PI) / 3;
  return x === 0 ? 0
    : x === 1 ? 1
    : -Math.pow(2, 10 * x - 10) * Math.sin((x * 10 - 10.75) * c4);
}
```
CSS: no equivalent

### easeOutElastic
```js
function easeOutElastic(x) {
  const c4 = (2 * Math.PI) / 3;
  return x === 0 ? 0
    : x === 1 ? 1
    : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * c4) + 1;
}
```
CSS: no equivalent

### easeInOutElastic
```js
function easeInOutElastic(x) {
  const c5 = (2 * Math.PI) / 4.5;
  return x === 0 ? 0
    : x === 1 ? 1
    : x < 0.5
    ? -(Math.pow(2, 20 * x - 10) * Math.sin((20 * x - 11.125) * c5)) / 2
    : (Math.pow(2, -20 * x + 10) * Math.sin((20 * x - 11.125) * c5)) / 2 + 1;
}
```
CSS: no equivalent

---

## Bounce  _(no CSS equivalent)_

### easeOutBounce  _(the base — others derive from it)_
```js
function easeOutBounce(x) {
  const n1 = 7.5625;
  const d1 = 2.75;
  if (x < 1 / d1) {
    return n1 * x * x;
  } else if (x < 2 / d1) {
    return n1 * (x -= 1.5 / d1) * x + 0.75;
  } else if (x < 2.5 / d1) {
    return n1 * (x -= 2.25 / d1) * x + 0.9375;
  } else {
    return n1 * (x -= 2.625 / d1) * x + 0.984375;
  }
}
```
CSS: no equivalent

### easeInBounce
```js
function easeInBounce(x) {
  return 1 - easeOutBounce(1 - x);
}
```
CSS: no equivalent

### easeInOutBounce
```js
function easeInOutBounce(x) {
  return x < 0.5
    ? (1 - easeOutBounce(1 - 2 * x)) / 2
    : (1 + easeOutBounce(2 * x - 1)) / 2;
}
```
CSS: no equivalent
