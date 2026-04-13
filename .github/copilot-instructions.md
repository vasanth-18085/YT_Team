# YouTube Team — Copilot Workspace Instructions

## System Overview
This workspace manages 4 YouTube channels using Oscar Owen's 18-task YouTube AI Team system + 7 YouTube Playbook frameworks.
- **Quant Trading** — active (16/18 tasks done, all frameworks applied)
- **Cricket Analytics** — waiting
- **Gaming Noob** — waiting
- **Vasanth Builds** — waiting (live prep/building channel: QF learning, Cricket Analytics, AI projects)

## Before Every Task
1. Read `YouTube Team/_SYSTEM/DASHBOARD.md` to see current status across all channels
2. Read the target channel's `MASTER-CONTEXT.md` (in its `00 - Master Context Doc/` folder)
3. Read the relevant instruction file from `YouTube Team/_TEMPLATES/instructions/`
4. Read the relevant playbook(s) from `YouTube Team/_TEMPLATES/playbooks/`
5. Check `/memories/yt-team-context.md` for cross-session decisions and context

## After Every Task
1. Save a snapshot in the task folder using the template from `YouTube Team/_TEMPLATES/task-snapshot-template.md`
2. Update `YouTube Team/_SYSTEM/DASHBOARD.md` — set status, timestamp, and snapshot link
3. Update `YouTube Team/_SYSTEM/SESSION-LOG.md` with what was done
4. If the task feeds into another task, create a handoff doc using `YouTube Team/_TEMPLATES/handoff-template.md`

## Key Rules
- **Every task starts with the Master Context Doc.** If the channel's MASTER-CONTEXT.md doesn't exist yet, fill it first using `YouTube Team/_TEMPLATES/master-context-template.md`
- **Information Gain matters.** Scripts must be built from the user's voice notes and personal experience, not generic AI generation
- **Full logging.** Every decision, blocker, and output must be timestamped and recorded
- **One channel at a time.** Finish proving the workflow on Quant Trading before moving to others
- **Persistent memory.** Always update `/memories/yt-team-context.md` with important decisions or context changes

## YouTube Playbook Frameworks (Applied to EVERY Channel)

### Quality Gates by Task

| Task | Required Framework(s) | Quality Gate |
|------|----------------------|-------------|
| Task 1 — Content Research | **FIIRE** | Every video must be categorized: Tinder (trending), Kindling (core), Logs (evergreen), or Flint (experimental). Target: 15–25% Tinder, 25–35% Kindling, 40–50% Logs, 5–15% Flint. |
| Task 3 — Idea Validation | **SEAS** | Score every idea 1–10 on: Spread of Users, Excitement, Audience Match, Simplicity. CCN Fit (Core/Casual/New viewers) must be validated. |
| Task 4 — Title Generator | **40–60 char rule** | All top-pick titles must be 40–60 characters. Generate 10–20 variations per video. |
| Task 5 — Thumbnail Concepts | **5C Framework** | Every concept must pass: Composition (framing), Context (18% glance test), Clean (≤3 elements), Curiosity (knowledge gap), Color (brand accent). |
| Task 7 — Script Refiner | **3 B's** | Be Bold (no hedging), Be Basic (jargon defined on first use), Be Brief (≤25 words/sentence, ≤3 sentences/paragraph). |
| Task 8 — Intro/Hook | **R.A.I.N.Y** | Every hook must have: Result (outcome stated), Address Objections (proof), Instant (under 40s), Why Now (urgency), Why You (authority). |
| Task 8 — Intro/Hook | **10 Hook Types** | Test at least 3 hook types: Question, Shocking Statement, Storytelling, Preview, Personal Connection, Statistic, Challenge, Quotation, Metaphor, Proof. |
| Pre-Launch | **COIN** | Create Audience Language doc: Audience Language (their words) + My Language (creator voice) = New Language (signature phrases + tone rules). |
| Pre-Launch | **TEACH** | Define for each video archetype: Tone, Eye Contact/Engagement, Animation/Vocal variety, Coherence, Haste/Pacing. Set energy level (3–4/10 for stories, 7/10 for tutorials). |

### Framework Quick Reference

**R.A.I.N.Y** (Hooks) — Result, Address Objections, Instant, Why Now, Why You  
**3 B's** (Scripts) — Be Bold, Be Basic, Be Brief  
**5C** (Thumbnails) — Composition, Context, Clean, Curiosity, Color  
**FIIRE** (Content Mix) — Flint, (K)Indling, Logs, Tinder + their balance ratios  
**SEAS** (Idea Validation) — Spread of Users, Excitement, Audience Match, Simplicity  
**COIN** (Audience Voice) — Audience Language + My Language = New Language (signature phrases)  
**TEACH** (On-Camera) — Tone, Eye Contact, Animation, Coherence, Haste  

### Playbook Source Files
All 4 playbook files are in `YouTube Team/_TEMPLATES/playbooks/`:
- `YOUTUBE CHANNEL PLAYBOOK.md` — FIIRE, SEAS, 5C, CCN Fit, MatPat Method, 80/20 Rule
- `SCRIPTWRITING PLAYBOOK.md` — R.A.I.N.Y, 3 B's, Bryan System, 6-Point Grading
- `ON CAMERA PLAYBOOK.md` — TEACH, Energy Guidelines, 7 Skill Drills
- `YOUTUBE CHANNEL CHECKLIST.md` — Pre-launch, per-video, monthly, quarterly checklists

## Quant Trading — Key References
- **V-Number Resolution:** `Quant-Trading/V-NUMBER-RESOLUTION.md` — Script V-numbers are production standard. Title/thumbnail files use different V-numbers from V8+. Always use the mapping table.
- **Channel Audit Summary:** `Quant-Trading/CHANNEL-WIDE-AUDIT-SUMMARY.md` — Full status of all 18 tasks + 7 frameworks
- **Brand Color:** Gold #FFD700 (thumbnails, banner, visual identity)
- **COIN Document:** `05 - Channel & Positioning/Audience Language — COIN Framework.md`
- **FIIRE Categorization:** `01 - Ideas & Research/Task 1 - Content Research/FIIRE Categorization — All 26 Videos.md`

## File Structure
```
YouTube Team/
├── _SYSTEM/           → DASHBOARD.md, SESSION-LOG.md, MEMORY-INDEX.md
├── _TEMPLATES/        → master-context, task-snapshot, handoff templates + instructions + examples + playbooks
├── Quant-Trading/     → 6 phases × 18 task folders + V-NUMBER-RESOLUTION.md + CHANNEL-WIDE-AUDIT-SUMMARY.md
├── Cricket-Analytics/  → same structure (empty, waiting)
├── Gaming-Noob/       → same structure (empty, waiting)
└── Vasanth-Builds/    → same structure (empty, waiting) — live prep & building channel
```

## Task Reference (18 tasks, 6 phases)
- Phase 1 — Ideas & Research: Task 1 (Content Research + FIIRE), Task 2 (Competitor Analysis), Task 3 (Idea Validation + SEAS)
- Phase 2 — Titles & Thumbnails: Task 4 (Title Generator + 100 frameworks + 40–60 char rule), Task 5 (Thumbnail Concepts + 5C)
- Phase 3 — Scripting: Task 6 (Brain Dump), Task 7 (Script Refiner + 3 B's), Task 8 (Intro/Hook + R.A.I.N.Y), Task 9 (Fluff Reducer), Task 10 (CTA Inserter)
- Phase 4 — Community & Comments: Task 11 (Community Posts), Task 12 (Comment Replies)
- Phase 5 — Channel & Positioning: Task 13 (Channel Audit), Task 14 (About Section), Task 15 (Banner), Task 16 (Playlist Strategy)
- Phase 6 — Monetisation & Outreach: Task 17 (Brand Outreach), Task 18 (Creator Collab)
- Cross-cutting: COIN (audience voice, pre-launch), TEACH (on-camera prep, pre-launch)
