# PhysioAI Frontend Redesign — Stitch Generation Spec

**Date:** 2026-03-28
**Scope:** Generate 6 accurate Stitch screens matching real app functionality, then implement HTML in the frontend.

---

## Goal

Regenerate all 6 frontend screens from scratch using the Stitch MCP. Each screen must reflect exact app functionality — correct exercises, real buttons only, no placeholder elements. Screens will be polished (text, graphics, animations) in a later pass.

---

## Visual Theme: Serene Clinician (preserved)

| Token | Value |
|-------|-------|
| Primary | `#006a71` (teal) |
| Background | `#f7f9fe` |
| Surface | `#ffffff` |
| Surface container | `#e8eef6` |
| On-surface | `#2b333b` |
| On-surface-variant | `#576068` |
| Headline font | Manrope |
| Body font | Inter |
| Button rounding | `1.5rem` (xl) |
| Card rounding | `1rem` (lg) |
| No border lines | depth via background shifts only |
| Button style | Teal gradient, uppercase label, Inter label-md |
| Input style | Filled, teal underline on focus |
| Layout | Desktop 1280px |

**Animations:** Not included in this phase. Structure should leave room for hover states and background transitions.

---

## Screen Specifications

### 1. Login (`index.html`)

**Elements:**
- PhysioAI wordmark (Manrope, large)
- Tagline: "Track. Improve. Recover."
- Email input field
- Password input field
- Primary CTA button: "Login"
- Link below button: "New user? Register"
- Error message area (subtle, below button)

**No:** Social login, forgot password, remember me.

**Required element IDs (for JS reattachment):**
| ID | Element |
|----|---------|
| `login-form` | The `<form>` element |
| `email` | Email input |
| `password` | Password input |
| `error` | Error message paragraph |

---

### 2. Sign Up (`signup.html`)

**Elements:**
- PhysioAI wordmark + tagline
- Full Name input
- Email input
- Age input (number)
- Gender dropdown (Male / Female / Other / Prefer not to say)
- Password input
- Confirm Password input *(required — JS validates passwords match before submitting)*
- Primary CTA button: "Create Account"
- Link: "Already have an account? Login"
- Error message area

**No:** Profile photo, terms checkbox, email confirmation note.

**Required element IDs:**
| ID | Element |
|----|---------|
| `signup-form` | The `<form>` element |
| `name` | Full name input |
| `email` | Email input |
| `age` | Age input |
| `gender` | Gender select |
| `password` | Password input |
| `confirm` | Confirm password input |
| `error` | Error message paragraph |

---

### 3. Exercise Catalog (`exercises.html`)

**Elements:**
- Header: "PhysioAI" left, "Session History" button/link (`id="session-history-btn"`) right
- Subheading: "Select 5 exercises to begin your session"
- Selection counter: e.g. "2 of 5 selected"
- 10 exercise cards in a 2-column grid
- Each card contains: exercise name (Manrope title), short description (Inter body), selectable highlight state (teal when selected)
- **Card structure note:** Each card must be a `<label>` wrapping a hidden `<input type="checkbox" class="exercise-checkbox">`. Selection state is driven by toggling a `.selected` CSS class on the label — no visible checkbox in the UI.
- Primary CTA: "Start Session" button (`id="start-session-btn"`, greyed/disabled until exactly 5 selected, bottom right)
- Helper text: `id="exercise-helper"` (shows selection status)
- Message area: `id="exercises-message"`

**The 10 exercises (exact names + descriptions):**
1. Standing Hip Flexion — Gently lift one knee forward while maintaining balance
2. Glute Bridge — Lie on your back and lift your hips toward the ceiling
3. Cobra Pose — Lie face down and gently lift your chest using your arms
4. Standing March — Alternate lifting each knee slightly while standing
5. Standing Forward Arm Raise — Slowly raise both arms forward to shoulder height
6. Standing Lateral Arm Raise — Gently raise both arms out to your sides
7. Shoulder Shrugs — Lift your shoulders toward your ears and lower them slowly
8. Standing Trunk Side Bend — Gently lean your torso to one side
9. Standing Arm Circles — Make small circular motions with your arms
10. Neutral Posture Hold — Stand tall with shoulders aligned over hips

**No:** Filters, sort controls, difficulty ratings, duration, favourites.

**Required element IDs:**
| ID | Element |
|----|---------|
| `exercise-list` | Container `<div>` where JS renders exercise cards |
| `start-session-btn` | Start Session button |
| `session-history-btn` | Session History link/button |
| `exercise-helper` | Selection counter text |
| `exercises-message` | Status message paragraph |

---

### 4. Live Session (`session.html`)

**Layout:** Two-column. Left: webcam feed (large). Right: session controls.

**Left column — Webcam:**
- Video feed placeholder area (`id="video"`, a `<video>` element, autoplay, playsinline)
- Pose overlay canvas (`id="output-canvas"`) overlaid on video
- Camera status text (`id="camera-status"`)

**Right column — Session info:**
- Current exercise name (`id="current-exercise"`, Manrope, large, prominent)
- **AI Feedback text (`id="feedback-text"`)** — must be highly visible: large Inter body, dark `#2b333b` colour, white card, generous padding. NOT secondary grey.
- Rep counter — two distinct values (both `id="rep-stats"`, JS writes e.g. `"3 / 10 (total: 4)"`):
  - Primary: correct reps / 10 cap (Manrope, large)
  - Secondary: total reps (Inter, smaller label beneath)
- Secondary button: "Next Exercise" (`id="next-exercise-btn"`)
- Primary button: "End Session" (`id="end-session-btn"`)
- Status message area (`id="session-message"`)

**Hidden audio elements (not visible in UI but required by JS):**
```html
<audio id="correctSound" src="assets/correct.mp3" preload="auto"></audio>
<audio id="wrongSound" src="assets/wrong.mp3" preload="auto"></audio>
```
These must be present in the final HTML but are hidden from the visual design.

**No:** Settings, timer countdown, exercise list sidebar, progress bar.

**Required element IDs:**
| ID | Element |
|----|---------|
| `video` | `<video>` element |
| `output-canvas` | `<canvas>` element |
| `camera-status` | Camera status paragraph |
| `current-exercise` | Exercise name span |
| `feedback-text` | AI feedback span |
| `rep-stats` | Rep counter span |
| `next-exercise-btn` | Next Exercise button |
| `end-session-btn` | End Session button |
| `session-message` | Status message paragraph |
| `correctSound` | Hidden audio element |
| `wrongSound` | Hidden audio element |

---

### 5. Session Summary (`summary.html`)

**Elements:**
- "Session Complete" heading
- Overall score: large Manrope number (e.g. "82") + "/ 100" — rendered into `id="overall-score"` span
- Total reps stat — rendered into `id="total-reps"` span. Must be a standalone addressable element.
- Per-exercise breakdown table (`id="summary-table"`):
  - `<thead>` with columns: Exercise | Correct Reps | Incorrect Reps | Total Reps | Posture %
  - `<tbody>` populated by JS (5 rows, one per selected exercise)
- Two navigation buttons:
  - "Start New Session" → links to `exercises.html`
  - "View History" → links to `history.html`
- Message area: `id="summary-message"`

**No:** Share, download PDF, badges, back to login.

**Required element IDs:**
| ID | Element |
|----|---------|
| `overall-score` | Score span (JS writes the number here) |
| `total-reps` | Total reps span (separately addressable) |
| `summary-table` | `<table>` element |
| `summary-message` | Status message paragraph |

---

### 6. Session History (`history.html`)

**Elements:**
- Header: "PhysioAI" left, logout link right
- Page title: "Session History"
- Session list container (`id="history-list"`) — JS renders rows here from localStorage
- Each row shows: date + time (Inter, secondary), session score (Manrope, teal, prominent)
- Empty state: shown when no sessions exist — "No sessions yet. Start your first session."
- Primary CTA button: "Start New Session" → links to `exercises.html`
- Message area: `id="history-message"`

**Data source note:** `history.js` reads from `localStorage` key `physioai_session_history` (written by session.js at session end). It does NOT call the `/history` backend API in the current implementation. No "View Details" link is included — detail navigation is not wired up and is out of scope for this phase.

**No:** View Details links, filter by date, export, delete, pagination.

**Required element IDs:**
| ID | Element |
|----|---------|
| `history-list` | Container where JS renders session rows |
| `history-message` | Status message paragraph |

---

## Implementation Notes (Phase 3)

- Stitch generates standalone HTML with inline styles — adapted into the existing `frontend/` file structure
- JS logic in `frontend/js/` is preserved and re-attached using the element IDs documented per screen above
- `session.html` must include two hidden `<audio>` elements (`correctSound`, `wrongSound`) — these are functional requirements, not design elements
- The exercise cards in `exercises.html` must use a `<label>` + hidden `<input type="checkbox" class="exercise-checkbox">` pattern for `exercises.js` compatibility
- `confirm` password field in `signup.html` is required for client-side validation in `auth.js`
- Animations (button hovers, background transitions) are a separate later pass
- `frontend/css/styles.css` will be replaced by Stitch design tokens

---

## Out of Scope (this phase)

- Animations and micro-interactions
- Mobile/responsive layout
- Exercise illustrations/icons
- Real-time pose skeleton overlay styling
- Session detail view (history → `/history/<session_id>`)
- Migrating history.js to use the `/history` backend API
