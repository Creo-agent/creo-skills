# Monday Icons Font Reference

268 monday.com icons as a single WOFF2 icon font. Use this reference to select icons by semantic meaning and render them with the correct HTML entity.

---

## How to Use

### HTML Pattern

```html
<span class="monday-icon">&#xf096;</span>  <!-- Checkmark -->
```

### With Size + Color Classes

```html
<span class="monday-icon ds-icon-sm">&#xf096;</span>
<span class="monday-icon ds-icon-md ds-icon-white">&#xf098;</span>
```

### CSS (already embedded in icon-font.css)

```css
@font-face {
  font-family: "MondayIcons";
  src: url(data:font/woff2;base64,...) format("woff2");
  font-weight: normal;
  font-style: normal;
  font-display: block;
}
.monday-icon {
  font-family: "MondayIcons" !important;
  font-style: normal;
  font-weight: normal;
  line-height: 1;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

---

## Icon Selection by Category

Use these categories to find the right icon for slide content. Each table is sorted by common usage.

### Process & Workflow
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Flow | f001 | `&#xf001;` | workflow, process, pipeline, automation, sequence |
| ArrowPath | f0f6 | `&#xf0f6;` | journey, path, direction, route, progression |
| Arrows | f0ea | `&#xf0ea;` | exchange, bidirectional, compare, transfer |
| Arrowup | f0ed | `&#xf0ed;` | increase, growth, upload, improve, rise |
| Refresh | f006 | `&#xf006;` | reload, retry, cycle, update, repeat |
| Refresh3 | f004 | `&#xf004;` | sync, reload, cycle, renew |
| Loop | f07a | `&#xf07a;` | repeat, cycle, recurring, iteration, continuous |
| Sync | f0b5 | `&#xf0b5;` | synchronize, update, realtime, mirror |
| Split | f0cd | `&#xf0cd;` | branch, divide, fork, separate, decision |
| Funnel | f104 | `&#xf104;` | filter, narrow, qualify, pipeline, conversion |
| Filter | f013 | `&#xf013;` | sort, refine, narrow, criteria |
| Filter2 | f011 | `&#xf011;` | sort, refine, narrow, criteria, alt |

### Achievement & Status
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Checkmark | f096 | `&#xf096;` | done, complete, success, approved, verified |
| Trophy | f07f | `&#xf07f;` | win, award, champion, achievement, first place |
| Win | f049 | `&#xf049;` | victory, success, celebrate, achievement |
| Badgecheck | f0e4 | `&#xf0e4;` | verified, certified, approved, quality |
| Badgestar | f0e1 | `&#xf0e1;` | premium, excellence, quality, star rating |
| Badge | f0de | `&#xf0de;` | award, rank, recognition, certification |
| Badge2 | f0db | `&#xf0db;` | award, rank, recognition, alt |
| Rankstarbadge | f008 | `&#xf008;` | ranking, star, top performer, leaderboard |
| Crown | — | — | royalty, premium, top tier, leadership |
| ThumbsUp | f097 | `&#xf097;` | approve, like, positive, agree, good |
| ThumbsDown | f09a | `&#xf09a;` | reject, dislike, negative, disagree, bad |
| Smiley | f0df | `&#xf0df;` | happy, positive, satisfaction, emoji |
| Sadsmiley | f000 | `&#xf000;` | unhappy, negative, dissatisfaction, pain point |

### Data & Metrics
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| BarChart | f0d8 | `&#xf0d8;` | analytics, statistics, metrics, data, report |
| Chartup | f09c | `&#xf09c;` | growth, increase, trending up, positive trend |
| Chartdown | f09f | `&#xf09f;` | decline, decrease, trending down, negative trend |
| Graph | f0e3 | `&#xf0e3;` | data, visualization, chart, analytics |
| Grapharrowup | f0ef | `&#xf0ef;` | growth metric, increase, performance up |
| Grapharrowdown | f0f2 | `&#xf0f2;` | decline metric, decrease, performance down |
| Graphup | f0e9 | `&#xf0e9;` | trending up, positive, growth |
| Graphdown | f0ec | `&#xf0ec;` | trending down, negative, decline |
| Graphups | f0e6 | `&#xf0e6;` | multiple growth, compound, portfolio |
| Stats | f0c7 | `&#xf0c7;` | statistics, numbers, KPIs, dashboard |
| Statsdoc | f0ca | `&#xf0ca;` | report, statistics document, analysis |
| Docstats | f037 | `&#xf037;` | document analytics, data report |
| Pie | f022 | `&#xf022;` | pie chart, distribution, breakdown, share |
| Barup | f0d5 | `&#xf0d5;` | bar increase, growth chart, histogram |
| Webchart | f052 | `&#xf052;` | web analytics, online metrics, dashboard |
| Webmeter | f04f | `&#xf04f;` | web performance, speed, gauge |
| Thermometer | f09d | `&#xf09d;` | temperature, level, gauge, measure |

### People & Teams
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Users | f064 | `&#xf064;` | team, people, group, collaboration, staff |
| User | f06a | `&#xf06a;` | person, individual, profile, account |
| Userscircle | f067 | `&#xf067;` | team circle, group, community |
| Userhand | f06d | `&#xf06d;` | volunteer, raise hand, participate |
| Pointusers | f01a | `&#xf01a;` | assign, delegate, point to team |
| Connectionuser | f063 | `&#xf063;` | connected person, linked user, network |
| Transfermoneyusers | f088 | `&#xf088;` | payment, transfer, payroll, transaction |
| Collaboration | f069 | `&#xf069;` | teamwork, cooperate, together, partnership |
| Handshake | f0d4 | `&#xf0d4;` | deal, agreement, partnership, contract |
| Organization | f034 | `&#xf034;` | org chart, hierarchy, structure, company |
| Hierachy | f0c8 | `&#xf0c8;` | tree, levels, org structure, chain of command |

### Communication
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Bubbletalk | f0b1 | `&#xf0b1;` | chat, message, conversation, discuss |
| Speechbubble | f0d0 | `&#xf0d0;` | speak, comment, feedback, dialogue |
| Quote | f00e | `&#xf00e;` | testimonial, quote, citation, reference |
| Megaphone | f068 | `&#xf068;` | announce, broadcast, promote, shout |
| Email | f027 | `&#xf027;` | mail, message, inbox, send |
| Envelope | f025 | `&#xf025;` | letter, mail, correspondence |
| Phone | f026 | `&#xf026;` | call, contact, telephone, support |
| Phone2 | f024 | `&#xf024;` | call, contact, telephone, alt |
| Phonering | f028 | `&#xf028;` | incoming call, ringing, alert |
| Microphone | f062 | `&#xf062;` | record, voice, audio, speak, podcast |
| Microphonemute | f065 | `&#xf065;` | mute, silent, no audio |
| Speaker | f0d3 | `&#xf0d3;` | audio, sound, volume, loudspeaker |
| Headphones | f0d1 | `&#xf0d1;` | listen, audio, music, support |
| Headset | f0ce | `&#xf0ce;` | support, call center, service, customer |
| Video | f061 | `&#xf061;` | video call, meeting, camera, record |
| Notification | f036 | `&#xf036;` | alert, bell, notify, update |
| Bell | f0cc | `&#xf0cc;` | notification, alert, reminder, alarm |
| Loud | — | — | volume, amplify, noise |

### Business & Finance
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Dollar | f02d | `&#xf02d;` | money, currency, price, cost, revenue |
| Cash | f0a2 | `&#xf0a2;` | payment, money, bills, finance |
| Coins | f06c | `&#xf06c;` | money, savings, investment, currency |
| Moneybag | f059 | `&#xf059;` | budget, funds, investment, wealth |
| Moneybags | f056 | `&#xf056;` | revenue, multiple funds, wealth, profit |
| Creditcard | f05a | `&#xf05a;` | payment, purchase, billing, transaction |
| Wallet | f05e | `&#xf05e;` | finance, personal funds, payment |
| Shoppingbag | f0ee | `&#xf0ee;` | purchase, retail, buy, ecommerce |
| ShoppingCart | f0eb | `&#xf0eb;` | cart, purchase, ecommerce, buy |
| Spaceshipdollars | f0d9 | `&#xf0d9;` | revenue growth, profit launch, financial boost |
| Targetdollar | f0af | `&#xf0af;` | revenue target, financial goal, sales target |
| Suitcase | f0be | `&#xf0be;` | business, travel, work, professional |

### Navigation & Location
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Compass | f066 | `&#xf066;` | direction, navigate, explore, strategy |
| Map | f06b | `&#xf06b;` | location, geography, territory, route |
| Location | f08c | `&#xf08c;` | place, pin, position, where |
| Pin | f020 | `&#xf020;` | location, mark, save, bookmark |
| Globe | f0f8 | `&#xf0f8;` | world, international, global, earth |
| Flag | f009 | `&#xf009;` | milestone, mark, start, country, priority |
| Sign | f0e8 | `&#xf0e8;` | signpost, direction, wayfinding |
| Door | f02b | `&#xf02b;` | entry, exit, opportunity, access |
| Home | f0c2 | `&#xf0c2;` | house, main, start, dashboard |
| House | f0bc | `&#xf0bc;` | home, property, residence |
| Mountain | f050 | `&#xf050;` | challenge, peak, climb, achievement, goal |

### Time & Scheduling
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Clock | f07e | `&#xf07e;` | time, schedule, duration, hours |
| Hourglass | f0bf | `&#xf0bf;` | waiting, countdown, deadline, patience |
| Calendar | f0a8 | `&#xf0a8;` | date, schedule, plan, event |
| Calendarcheck | f0ae | `&#xf0ae;` | scheduled, confirmed, booked, date set |
| Calendarplus | f0ab | `&#xf0ab;` | add event, schedule new, plan ahead |
| Alarm | f105 | `&#xf105;` | alert, urgent, deadline, warning |
| Alarmcheck | f108 | `&#xf108;` | alarm set, confirmed alert, scheduled |
| Watch | f058 | `&#xf058;` | time, wearable, quick, stopwatch |

### Technology & Systems
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Settingsgear | f0fa | `&#xf0fa;` | settings, configure, preferences, control |
| Gear | f101 | `&#xf101;` | settings, mechanical, configure |
| Gears | f0fe | `&#xf0fe;` | automation, machinery, system, engineering |
| Handgear | f0d7 | `&#xf0d7;` | manual settings, hands-on config, craft |
| Tool | f08e | `&#xf08e;` | wrench, fix, repair, utility |
| Tools | f08b | `&#xf08b;` | toolkit, utilities, build, repair |
| Chip | f093 | `&#xf093;` | processor, hardware, computing, AI |
| Chip2 | f090 | `&#xf090;` | processor, hardware, computing, alt |
| Database | f04b | `&#xf04b;` | storage, data, server, backend |
| Database2 | f048 | `&#xf048;` | storage, data, server, alt |
| Network | f04a | `&#xf04a;` | infrastructure, connected, nodes, topology |
| Network2 | f047 | `&#xf047;` | infrastructure, connected, nodes, alt |
| Connection | f060 | `&#xf060;` | link, integrate, connect, bridge |
| Link | f095 | `&#xf095;` | url, chain, connect, reference |
| WiFi | f04c | `&#xf04c;` | wireless, internet, connectivity |
| Signal | f0e2 | `&#xf0e2;` | reception, connectivity, strength |
| Signalradar | f0e5 | `&#xf0e5;` | detection, scanning, monitoring, signal |
| Radar | f00c | `&#xf00c;` | scan, detect, monitor, search |
| Desktop | f03f | `&#xf03f;` | computer, monitor, workstation |
| Desktop2 | f03d | `&#xf03d;` | computer, monitor, workstation, alt |
| Desktopcheck | f045 | `&#xf045;` | verified system, computer check, approved |
| Desktopstats | f042 | `&#xf042;` | analytics dashboard, monitoring, system stats |
| Laptop | f0a4 | `&#xf0a4;` | portable, computer, work, remote |
| Tablet | f0b2 | `&#xf0b2;` | mobile device, ipad, touch |
| TV | f079 | `&#xf079;` | television, display, screen, broadcast |
| Molecular | f05c | `&#xf05c;` | science, chemistry, atomic, structure |
| Cube | f054 | `&#xf054;` | 3d, block, module, component |
| Container | f05d | `&#xf05d;` | docker, package, module, encapsulate |

### Documents & Content
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Document | f02f | `&#xf02f;` | file, page, paper, report |
| Documentbar | f033 | `&#xf033;` | document with progress, status bar |
| Documenttext | f031 | `&#xf031;` | text file, article, content, readme |
| Docs | f035 | `&#xf035;` | multiple documents, files, documentation |
| Doccomputer | f039 | `&#xf039;` | digital document, online file |
| Paper | f030 | `&#xf030;` | page, note, sheet, blank |
| Paperplane | f032 | `&#xf032;` | send, launch, deploy, submit |
| Clipboard | f081 | `&#xf081;` | paste, copy, tasks, notes |
| Clipboardpen | f084 | `&#xf084;` | form, fill out, sign, edit tasks |
| Book | f0c0 | `&#xf0c0;` | manual, documentation, guide, reference |
| Bookopen | f0c6 | `&#xf0c6;` | reading, study, learning, open book |
| Bookopen2 | f0c3 | `&#xf0c3;` | reading, study, learning, alt |
| Bookbookmark | f0c9 | `&#xf0c9;` | saved page, reference, marked |
| Bookmark | f0bd | `&#xf0bd;` | save, favorite, mark, later |
| Checklist | f099 | `&#xf099;` | tasks, to-do, action items, list |
| List | f08f | `&#xf08f;` | items, menu, options, enumerate |
| Text | f0a0 | `&#xf0a0;` | text, type, content, paragraph |
| Edit | f029 | `&#xf029;` | modify, change, write, update |
| Pen | f02c | `&#xf02c;` | write, sign, author, compose |
| Pencil | f02a | `&#xf02a;` | write, sketch, draw, edit |
| Penwrite | f02e | `&#xf02e;` | compose, author, write, create |

### Security & Protection
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Lock | f086 | `&#xf086;` | secure, locked, private, protected |
| Unlock | f070 | `&#xf070;` | open, access, unsecure, released |
| Locker | f083 | `&#xf083;` | storage, secure, safe, vault |
| Locknetwork | f089 | `&#xf089;` | network security, VPN, secure connection |
| Key | f0aa | `&#xf0aa;` | access, authentication, password, unlock |
| Shieldcheck | f0f4 | `&#xf0f4;` | protected, verified, safe, security check |
| Shieldstar | f0f1 | `&#xf0f1;` | premium security, star protection, trust |
| Fingerprint | f00b | `&#xf00b;` | biometric, identity, authentication |
| Eye | f01b | `&#xf01b;` | view, visible, watch, observe |
| Eyecheck | f01f | `&#xf01f;` | reviewed, seen, verified, inspected |
| Eyepie | f01d | `&#xf01d;` | analytics view, data insight, observe data |
| Noeye | f03e | `&#xf03e;` | hidden, invisible, private, concealed |
| Prohibited | f016 | `&#xf016;` | blocked, forbidden, restricted, not allowed |

### Alerts & Notifications
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Warning | f05b | `&#xf05b;` | caution, alert, danger, risk, attention |
| Exclamation | f023 | `&#xf023;` | important, attention, critical, urgent |
| Info | f0b3 | `&#xf0b3;` | information, details, about, help |
| Info2 | f0b0 | `&#xf0b0;` | information, details, about, alt |
| Question | f010 | `&#xf010;` | help, ask, unknown, faq |
| Questionbrain | f012 | `&#xf012;` | think, brainstorm, question, curiosity |
| Nocall | f044 | `&#xf044;` | do not disturb, no phone, silent |
| Nocloud | f041 | `&#xf041;` | offline, no sync, disconnected |
| NoImage | f03c | `&#xf03c;` | missing image, broken, placeholder |
| Noring | f03a | `&#xf03a;` | silent, muted, no notification |
| Novideo | f038 | `&#xf038;` | camera off, no video, disabled |

### Actions & UI
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Plus | f01c | `&#xf01c;` | add, create, new, expand |
| Minus | f05f | `&#xf05f;` | remove, subtract, reduce, collapse |
| Close | f07b | `&#xf07b;` | delete, dismiss, cancel, x |
| Search | f0fd | `&#xf0fd;` | find, lookup, discover, magnify |
| Magnifying | f06e | `&#xf06e;` | search, zoom, inspect, examine |
| Expand | f021 | `&#xf021;` | fullscreen, enlarge, maximize |
| Crop | f057 | `&#xf057;` | resize, trim, cut, frame |
| Copy | — | — | duplicate, clone, replicate |
| Trash | f082 | `&#xf082;` | delete, remove, discard, bin |
| Save | f109 | `&#xf109;` | store, preserve, keep, download |
| Click | f08a | `&#xf08a;` | tap, press, interact, action |
| Cursor | f04e | `&#xf04e;` | pointer, mouse, select, navigate |
| Cursorfinger | f051 | `&#xf051;` | touch, tap, point, select |
| Finger | f00d | `&#xf00d;` | point, indicate, touch, direct |
| Fingerclick | f00f | `&#xf00f;` | tap, press, touch, interact |
| Toggle | f091 | `&#xf091;` | switch, on/off, enable/disable |
| Togglebox | f094 | `&#xf094;` | checkbox, option, select, switch |
| PlayButton | f01e | `&#xf01e;` | play, start, video, media |
| Login | f080 | `&#xf080;` | sign in, enter, access, authenticate |
| LogOut | f07d | `&#xf07d;` | sign out, exit, leave, disconnect |
| Share | f0f7 | `&#xf0f7;` | distribute, send, forward, social |
| Translate | f085 | `&#xf085;` | language, localize, i18n, multilingual |
| Scissors | f100 | `&#xf100;` | cut, trim, edit, separate |
| Magicwand | f077 | `&#xf077;` | auto, magic, AI, generate, transform |
| Magicwand2 | f074 | `&#xf074;` | auto, magic, AI, generate, alt |

### Objects & Things
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Lightbulb | f098 | `&#xf098;` | idea, insight, innovation, tip, inspiration |
| Flash | f007 | `&#xf007;` | fast, instant, power, energy, lightning |
| Flash2 | f005 | `&#xf005;` | fast, instant, power, energy, alt |
| Spaceship | f0d6 | `&#xf0d6;` | launch, rocket, speed, moonshot, startup |
| Launch | f0a1 | `&#xf0a1;` | rocket, deploy, release, go live |
| Diamond | f03b | `&#xf03b;` | premium, valuable, gem, quality |
| Heart | f0cb | `&#xf0cb;` | love, favorite, like, health |
| Gift | f0fb | `&#xf0fb;` | present, reward, bonus, surprise |
| Puzzle | f014 | `&#xf014;` | solve, piece, fit, problem, integration |
| Umbrella | f073 | `&#xf073;` | protect, insurance, cover, shield |
| Coffee | f06f | `&#xf06f;` | break, cafe, energy, morning |
| Camera | f0a5 | `&#xf0a5;` | photo, capture, screenshot, visual |
| Image | f0b9 | `&#xf0b9;` | picture, photo, visual, media |
| Film | f015 | `&#xf015;` | movie, video, cinema, media |
| Music | f04d | `&#xf04d;` | audio, song, sound, melody |
| Stereo | f0c4 | `&#xf0c4;` | audio, music, sound system |
| Feather | f017 | `&#xf017;` | light, write, author, delicate |
| Anchor | f102 | `&#xf102;` | stable, grounded, port, foundation |
| Battery | f0cf | `&#xf0cf;` | power, energy, charge, capacity |
| Batterycharge | f0d2 | `&#xf0d2;` | charging, power up, energy, filling |
| Magnet | f071 | `&#xf071;` | attract, pull, magnetic, draw |
| Stethoscope | f0c1 | `&#xf0c1;` | health, diagnose, medical, check |
| Goggles | f0f5 | `&#xf0f5;` | VR, vision, lab, safety, immersive |
| Printer | f018 | `&#xf018;` | print, output, hardcopy |
| Truck | f07c | `&#xf07c;` | delivery, shipping, logistics, transport |
| Snowflake | f0dc | `&#xf0dc;` | freeze, cold, winter, pause |
| Sun | f0bb | `&#xf0bb;` | day, light, bright, energy |
| Moon | f053 | `&#xf053;` | night, dark mode, sleep |
| Rain | f00a | `&#xf00a;` | weather, storm, wet, cloud |
| Weather | f055 | `&#xf055;` | climate, forecast, conditions |
| Wind | f046 | `&#xf046;` | air, breeze, speed, fast |
| Cloud | f075 | `&#xf075;` | cloud, hosting, saas, storage |
| Cloud2 | f072 | `&#xf072;` | cloud, hosting, saas, alt |
| Cloudflash | f078 | `&#xf078;` | cloud computing, serverless, fast cloud |

### Targets & Goals
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Target | f0a6 | `&#xf0a6;` | goal, aim, objective, bullseye |
| Target2 | f0a3 | `&#xf0a3;` | goal, aim, objective, alt |
| Targeteye | f0ac | `&#xf0ac;` | focus, precision, observe target |
| Targetwin | f0a9 | `&#xf0a9;` | goal achieved, target hit, success |
| Scaletarget | f103 | `&#xf103;` | growth target, scaling goal |
| Scalebalance | f106 | `&#xf106;` | balance, fairness, compare, weigh |
| Arrowtarget | f0f0 | `&#xf0f0;` | aim, precision, hit target |
| Arrowprecentage | f0f3 | `&#xf0f3;` | percentage, rate, ratio, metric |

### Storage & Files
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Folder | f107 | `&#xf107;` | directory, organize, category |
| Folderdownload | f10a | `&#xf10a;` | download folder, export, save |
| Box | f0b7 | `&#xf0b7;` | package, contain, store, product |
| Box2 | f0b4 | `&#xf0b4;` | package, contain, store, alt |
| Boxarrows | f0ba | `&#xf0ba;` | distribute, ship, unbox, expand |
| Archive | f0fc | `&#xf0fc;` | store, backup, history, old |
| Archive2 | f0f9 | `&#xf0f9;` | store, backup, history, alt |
| Inbox | f0b6 | `&#xf0b6;` | receive, incoming, queue, pending |
| Clip | f087 | `&#xf087;` | attach, paperclip, attachment |
| Label | f0a7 | `&#xf0a7;` | tag, categorize, classify, name |
| grid | f0e0 | `&#xf0e0;` | layout, tiles, gallery, overview |
| Grid2 | f0dd | `&#xf0dd;` | layout, tiles, gallery, alt |
| Grid3 | f0da | `&#xf0da;` | layout, tiles, gallery, alt2 |
| Layers | f09e | `&#xf09e;` | stack, depth, levels, overlapping |
| Layers2 | f09b | `&#xf09b;` | stack, depth, levels, alt |

### Education & Knowledge
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Academy | f10b | `&#xf10b;` | school, education, learning, university, training |
| Bookopen | f0c6 | `&#xf0c6;` | study, read, learn, knowledge |
| Bookopen2 | f0c3 | `&#xf0c3;` | study, read, learn, alt |
| Lightbulb | f098 | `&#xf098;` | idea, insight, tip, eureka |
| Questionbrain | f012 | `&#xf012;` | think, brainstorm, curiosity |
| Resource | f002 | `&#xf002;` | asset, material, resource, supply |
| Float | f003 | `&#xf003;` | float, hover, elevate, buoyancy |

### Social & Brand
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Facebook | f019 | `&#xf019;` | social, facebook, meta |
| Instagram | f0ad | `&#xf0ad;` | social, instagram, photo |
| LinkedIn | f092 | `&#xf092;` | social, linkedin, professional |
| Twitter | f076 | `&#xf076;` | social, twitter, x |
| Youtube | f040 | `&#xf040;` | social, youtube, video |
| Windowat | f043 | `&#xf043;` | browser, window, web, app |

### Health & Wellness
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Stethoscope | f0c1 | `&#xf0c1;` | health, medical, diagnose, checkup |
| Heart | f0cb | `&#xf0cb;` | health, love, wellness, care |
| Auction | f0e7 | `&#xf0e7;` | bid, gavel, legal, judge, decision |
| Apps | f0ff | `&#xf0ff;` | applications, grid, app store, marketplace |

### Miscellaneous
| Icon | Code | Entity | Tags |
|------|------|--------|------|
| Hirarcyfiles | f0c5 | `&#xf0c5;` | file tree, structure, nested documents |
| Syncserch | f0b8 | `&#xf0b8;` | search sync, find updates, discover |

---

## Complete Alphabetical Index

Quick lookup — every icon sorted A-Z with its HTML entity.

| Icon | Entity | | Icon | Entity |
|------|--------|-|------|--------|
| Academy | `&#xf10b;` | | Alarmcheck | `&#xf108;` |
| Alarm | `&#xf105;` | | Anchor | `&#xf102;` |
| Apps | `&#xf0ff;` | | Archive | `&#xf0fc;` |
| Archive2 | `&#xf0f9;` | | ArrowPath | `&#xf0f6;` |
| Arrowprecentage | `&#xf0f3;` | | Arrows | `&#xf0ea;` |
| Arrowtarget | `&#xf0f0;` | | Arrowup | `&#xf0ed;` |
| Auction | `&#xf0e7;` | | Badge | `&#xf0de;` |
| Badge2 | `&#xf0db;` | | Badgecheck | `&#xf0e4;` |
| Badgestar | `&#xf0e1;` | | BarChart | `&#xf0d8;` |
| Barup | `&#xf0d5;` | | Battery | `&#xf0cf;` |
| Batterycharge | `&#xf0d2;` | | Bell | `&#xf0cc;` |
| Book | `&#xf0c0;` | | Bookbookmark | `&#xf0c9;` |
| Bookmark | `&#xf0bd;` | | Bookopen | `&#xf0c6;` |
| Bookopen2 | `&#xf0c3;` | | Box | `&#xf0b7;` |
| Box2 | `&#xf0b4;` | | Boxarrows | `&#xf0ba;` |
| Bubbletalk | `&#xf0b1;` | | Calendar | `&#xf0a8;` |
| Calendarcheck | `&#xf0ae;` | | Calendarplus | `&#xf0ab;` |
| Camera | `&#xf0a5;` | | Cash | `&#xf0a2;` |
| Chartdown | `&#xf09f;` | | Chartup | `&#xf09c;` |
| Checklist | `&#xf099;` | | Checkmark | `&#xf096;` |
| Chip | `&#xf093;` | | Chip2 | `&#xf090;` |
| Circle | `&#xf08d;` | | Click | `&#xf08a;` |
| Clip | `&#xf087;` | | Clipboard | `&#xf081;` |
| Clipboardpen | `&#xf084;` | | Clock | `&#xf07e;` |
| Close | `&#xf07b;` | | Cloud | `&#xf075;` |
| Cloud2 | `&#xf072;` | | Cloudflash | `&#xf078;` |
| Coffee | `&#xf06f;` | | Coins | `&#xf06c;` |
| Collaboration | `&#xf069;` | | Compass | `&#xf066;` |
| Connection | `&#xf060;` | | Connectionuser | `&#xf063;` |
| Container | `&#xf05d;` | | Creditcard | `&#xf05a;` |
| Crop | `&#xf057;` | | Cube | `&#xf054;` |
| Cursor | `&#xf04e;` | | Cursorfinger | `&#xf051;` |
| Database | `&#xf04b;` | | Database2 | `&#xf048;` |
| Desktop | `&#xf03f;` | | Desktop2 | `&#xf03d;` |
| Desktopcheck | `&#xf045;` | | Desktopstats | `&#xf042;` |
| Diamond | `&#xf03b;` | | Doccomputer | `&#xf039;` |
| Docs | `&#xf035;` | | Docstats | `&#xf037;` |
| Document | `&#xf02f;` | | Documentbar | `&#xf033;` |
| Documenttext | `&#xf031;` | | Dollar | `&#xf02d;` |
| Door | `&#xf02b;` | | Edit | `&#xf029;` |
| Email | `&#xf027;` | | Envelope | `&#xf025;` |
| Exclamation | `&#xf023;` | | Expand | `&#xf021;` |
| Eye | `&#xf01b;` | | Eyecheck | `&#xf01f;` |
| Eyepie | `&#xf01d;` | | Facebook | `&#xf019;` |
| Feather | `&#xf017;` | | Film | `&#xf015;` |
| Filter | `&#xf013;` | | Filter2 | `&#xf011;` |
| Finger | `&#xf00d;` | | Fingerclick | `&#xf00f;` |
| Fingerprint | `&#xf00b;` | | Flag | `&#xf009;` |
| Flash | `&#xf007;` | | Flash2 | `&#xf005;` |
| Float | `&#xf003;` | | Flow | `&#xf001;` |
| Folder | `&#xf107;` | | Folderdownload | `&#xf10a;` |
| Funnel | `&#xf104;` | | Gear | `&#xf101;` |
| Gears | `&#xf0fe;` | | Gift | `&#xf0fb;` |
| Globe | `&#xf0f8;` | | Goggles | `&#xf0f5;` |
| Graph | `&#xf0e3;` | | Grapharrowdown | `&#xf0f2;` |
| Grapharrowup | `&#xf0ef;` | | Graphdown | `&#xf0ec;` |
| Graphup | `&#xf0e9;` | | Graphups | `&#xf0e6;` |
| grid | `&#xf0e0;` | | Grid2 | `&#xf0dd;` |
| Grid3 | `&#xf0da;` | | Handgear | `&#xf0d7;` |
| Handshake | `&#xf0d4;` | | Headphones | `&#xf0d1;` |
| Headset | `&#xf0ce;` | | Heart | `&#xf0cb;` |
| Hierachy | `&#xf0c8;` | | Hirarcyfiles | `&#xf0c5;` |
| Home | `&#xf0c2;` | | Hourglass | `&#xf0bf;` |
| House | `&#xf0bc;` | | Image | `&#xf0b9;` |
| Inbox | `&#xf0b6;` | | Info | `&#xf0b3;` |
| Info2 | `&#xf0b0;` | | Instagram | `&#xf0ad;` |
| Key | `&#xf0aa;` | | Label | `&#xf0a7;` |
| Laptop | `&#xf0a4;` | | Launch | `&#xf0a1;` |
| Layers | `&#xf09e;` | | Layers2 | `&#xf09b;` |
| Lightbulb | `&#xf098;` | | Link | `&#xf095;` |
| LinkedIn | `&#xf092;` | | List | `&#xf08f;` |
| Location | `&#xf08c;` | | Lock | `&#xf086;` |
| Locker | `&#xf083;` | | Locknetwork | `&#xf089;` |
| Login | `&#xf080;` | | LogOut | `&#xf07d;` |
| Loop | `&#xf07a;` | | Magicwand | `&#xf077;` |
| Magicwand2 | `&#xf074;` | | Magnet | `&#xf071;` |
| Magnifying | `&#xf06e;` | | Map | `&#xf06b;` |
| Megaphone | `&#xf068;` | | Microphone | `&#xf062;` |
| Microphonemute | `&#xf065;` | | Minus | `&#xf05f;` |
| Molecular | `&#xf05c;` | | Moneybag | `&#xf059;` |
| Moneybags | `&#xf056;` | | Moon | `&#xf053;` |
| Mountain | `&#xf050;` | | Music | `&#xf04d;` |
| Network | `&#xf04a;` | | Network2 | `&#xf047;` |
| Nocall | `&#xf044;` | | Nocloud | `&#xf041;` |
| Noeye | `&#xf03e;` | | NoImage | `&#xf03c;` |
| Noring | `&#xf03a;` | | Notification | `&#xf036;` |
| Novideo | `&#xf038;` | | Organization | `&#xf034;` |
| Paper | `&#xf030;` | | Paperplane | `&#xf032;` |
| Pen | `&#xf02c;` | | Pencil | `&#xf02a;` |
| Penwrite | `&#xf02e;` | | Phone | `&#xf026;` |
| Phone2 | `&#xf024;` | | Phonering | `&#xf028;` |
| Pie | `&#xf022;` | | Pin | `&#xf020;` |
| PlayButton | `&#xf01e;` | | Plus | `&#xf01c;` |
| Pointusers | `&#xf01a;` | | Printer | `&#xf018;` |
| Prohibited | `&#xf016;` | | Puzzle | `&#xf014;` |
| Question | `&#xf010;` | | Questionbrain | `&#xf012;` |
| Quote | `&#xf00e;` | | Radar | `&#xf00c;` |
| Rain | `&#xf00a;` | | Rankstarbadge | `&#xf008;` |
| Refresh | `&#xf006;` | | Refresh3 | `&#xf004;` |
| Resource | `&#xf002;` | | Sadsmiley | `&#xf000;` |
| Save | `&#xf109;` | | Scalebalance | `&#xf106;` |
| Scaletarget | `&#xf103;` | | Scissors | `&#xf100;` |
| Search | `&#xf0fd;` | | Settingsgear | `&#xf0fa;` |
| Share | `&#xf0f7;` | | Shieldcheck | `&#xf0f4;` |
| Shieldstar | `&#xf0f1;` | | Shoppingbag | `&#xf0ee;` |
| ShoppingCart | `&#xf0eb;` | | Sign | `&#xf0e8;` |
| Signal | `&#xf0e2;` | | Signalradar | `&#xf0e5;` |
| Smiley | `&#xf0df;` | | Snowflake | `&#xf0dc;` |
| Spaceship | `&#xf0d6;` | | Spaceshipdollars | `&#xf0d9;` |
| Speaker | `&#xf0d3;` | | Speechbubble | `&#xf0d0;` |
| Split | `&#xf0cd;` | | Stats | `&#xf0c7;` |
| Statsdoc | `&#xf0ca;` | | Stereo | `&#xf0c4;` |
| Stethoscope | `&#xf0c1;` | | Suitcase | `&#xf0be;` |
| Sun | `&#xf0bb;` | | Sync | `&#xf0b5;` |
| Syncserch | `&#xf0b8;` | | Tablet | `&#xf0b2;` |
| Target | `&#xf0a6;` | | Target2 | `&#xf0a3;` |
| Targetdollar | `&#xf0af;` | | Targeteye | `&#xf0ac;` |
| Targetwin | `&#xf0a9;` | | Text | `&#xf0a0;` |
| Thermometer | `&#xf09d;` | | ThumbsDown | `&#xf09a;` |
| ThumbsUp | `&#xf097;` | | Toggle | `&#xf091;` |
| Togglebox | `&#xf094;` | | Tool | `&#xf08e;` |
| Tools | `&#xf08b;` | | Transfermoneyusers | `&#xf088;` |
| Translate | `&#xf085;` | | Trash | `&#xf082;` |
| Trophy | `&#xf07f;` | | Truck | `&#xf07c;` |
| TV | `&#xf079;` | | Twitter | `&#xf076;` |
| Umbrella | `&#xf073;` | | Unlock | `&#xf070;` |
| User | `&#xf06a;` | | Userhand | `&#xf06d;` |
| Users | `&#xf064;` | | Userscircle | `&#xf067;` |
| Video | `&#xf061;` | | Wallet | `&#xf05e;` |
| Warning | `&#xf05b;` | | Watch | `&#xf058;` |
| Weather | `&#xf055;` | | Webchart | `&#xf052;` |
| Webmeter | `&#xf04f;` | | WiFi | `&#xf04c;` |
| Win | `&#xf049;` | | Wind | `&#xf046;` |
| Windowat | `&#xf043;` | | Youtube | `&#xf040;` |
