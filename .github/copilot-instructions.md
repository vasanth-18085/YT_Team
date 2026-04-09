# YouTube Team — Copilot Workspace Instructions

## System Overview
This workspace manages 3 YouTube channels using Oscar Owen's 18-task YouTube AI Team system.
- **Quant Trading** — active (proving workflow first)
- **Cricket Analytics** — waiting
- **Gaming Noob** — waiting

## Before Every Task
1. Read `YouTube Team/_SYSTEM/DASHBOARD.md` to see current status across all channels
2. Read the target channel's `MASTER-CONTEXT.md` (in its `00 - Master Context Doc/` folder)
3. Read the relevant instruction file from `YouTube Team/_TEMPLATES/instructions/`
4. Check `/memories/yt-team-context.md` for cross-session decisions and context

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

## File Structure
```
YouTube Team/
├── _SYSTEM/           → DASHBOARD.md, SESSION-LOG.md, MEMORY-INDEX.md
├── _TEMPLATES/        → master-context, task-snapshot, handoff templates + instructions + examples
├── Quant-Trading/     → 6 phases × 18 task folders
├── Cricket-Analytics/  → same structure (empty, waiting)
└── Gaming-Noob/       → same structure (empty, waiting)
```

## Task Reference (18 tasks, 6 phases)
- Phase 1 — Ideas & Research: Task 1 (Content Research), Task 2 (Competitor Analysis), Task 3 (Idea Validation)
- Phase 2 — Titles & Thumbnails: Task 4 (Title Generator + 100 frameworks), Task 5 (Thumbnail Concepts)
- Phase 3 — Scripting: Task 6 (Brain Dump), Task 7 (Script Refiner), Task 8 (Intro/Hook), Task 9 (Fluff Reducer), Task 10 (CTA Inserter)
- Phase 4 — Community & Comments: Task 11 (Community Posts), Task 12 (Comment Replies)
- Phase 5 — Channel & Positioning: Task 13 (Channel Audit), Task 14 (About Section), Task 15 (Banner), Task 16 (Playlist Strategy)
- Phase 6 — Monetisation & Outreach: Task 17 (Brand Outreach), Task 18 (Creator Collab)
