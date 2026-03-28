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
**Stitch prompt focus:** Centered card on teal-tinted background. PhysioAI brand name + "Track. Improve. Recover." tagline above the card.

**Elements:**
- PhysioAI logo/wordmark (Manrope, large)
- Tagline: "Track. Improve. Recover."
- Email input field
- Password input field
- Primary CTA button: "Login"
- Link below button: "New user? Register"
- Error message area (subtle, below button)

**No:** Social login buttons, "forgot password", remember me checkbox.

---

### 2. Sign Up (`signup.html`)
**Stitch prompt focus:** Same centered card layout as Login. Single-column form.

**Elements:**
- PhysioAI wordmark + tagline
- Full Name input
- Email input
- Age input (number)
- Gender dropdown (Male / Female / Other / Prefer not to say)
- Password input
- Primary CTA button: "Create Account"
- Link: "Already have an account? Login"
- Error message area

**No:** Profile photo upload, terms checkbox, email confirmation note.

---

### 3. Exercise Catalog (`exercises.html`)
**Stitch prompt focus:** Full-width catalog page. Header with nav. Grid of exercise cards.

**Elements:**
- Header: "PhysioAI" left, "Session History" text-link right
- Subheading: "Select 5 exercises to begin your session"
- Selection counter: e.g. "2 of 5 selected" (updates dynamically)
- 10 exercise cards in a grid (2 columns), each showing:
  - Exercise name (Manrope, title)
  - Short description (1 line, Inter body)
  - Selectable state (teal highlight when selected)
- Primary CTA button: "Start Session" (disabled/greyed until 5 selected, bottom right)

**The 10 exercises (exact names):**
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

**No:** Filter/sort controls, difficulty ratings, duration estimates, favourites.

---

### 4. Live Session (`session.html`)
**Stitch prompt focus:** Two-column layout. Webcam feed left (large), session controls right.

**Elements — Left column (webcam):**
- Video feed placeholder (labelled "Camera Feed")
- Pose overlay canvas area
- Camera status text (small, below video)

**Elements — Right column (session info):**
- Current exercise name (Manrope, large, prominent)
- AI Feedback text — **must be highly visible**: large Inter body, dark `on-surface` `#2b333b` colour, on a white card with generous padding. Not secondary grey.
- Rep counter: "4 / 10 reps" (Manrope, large number)
- Secondary button: "Next Exercise"
- Primary button: "End Session"
- Status message area

**No:** Settings gear, timer countdown, exercise list sidebar, progress bar across top.

---

### 5. Session Summary (`summary.html`)
**Stitch prompt focus:** Celebration/results layout. Large score hero at top, breakdown table below.

**Elements:**
- "Session Complete" heading
- Overall score (large Manrope number, e.g. "82 / 100")
- Total reps stat card
- Per-exercise breakdown table:
  - Columns: Exercise | Correct Reps | Incorrect Reps | Total Reps | Posture %
  - 5 rows (one per selected exercise)
- Two navigation buttons: "Start New Session" (primary) + "View History" (secondary)

**No:** Share button, download PDF, badges/achievements, back to login.

---

### 6. Session History (`history.html`)
**Stitch prompt focus:** Clean list view. Newest sessions at top.

**Elements:**
- Header: "PhysioAI" left, "Logout" text-link right
- Page title: "Session History"
- List of session rows, each showing:
  - Date + time (Inter, secondary)
  - Session score (Manrope, prominent, teal)
  - "View Details" chevron/link
- Empty state: illustration placeholder + "No sessions yet. Start your first session."
- Primary CTA button: "Start New Session" (bottom or header)

**No:** Filter by date, export, delete session, pagination controls.

---

## Implementation Notes (Phase 3)

- Stitch generates standalone HTML with inline styles — these will be adapted into the existing `frontend/` file structure
- JS logic in `frontend/js/` (auth.js, exercises.js, session.js, summary.js, history.js) is preserved and re-attached to new HTML structure
- Animations (button hovers, background transitions) added as a separate pass after HTML implementation
- The existing `frontend/css/styles.css` will be replaced by the Stitch design tokens

---

## Out of Scope (this phase)

- Animations and micro-interactions
- Mobile/responsive layout
- Exercise illustrations/icons
- Real-time pose skeleton overlay styling
