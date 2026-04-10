# New Channel Handoff — Complete Production Guide

> **Purpose:** Paste this document into a fresh Copilot chat window to bootstrap the full 18-task YouTube pre-production workflow for a new channel. This captures everything learned from building the Quant Trading (MLQuant) channel.
>
> **How to use:** Open a new chat in the YT_Team workspace. Paste this entire document. Then say: "I want to start building [CHANNEL NAME]. Follow this handoff guide."

---

## SECTION 1 — SYSTEM CONTEXT

### What this workspace is
This workspace (`/Users/vasanth-18085/Projects/YT_Team`) manages multiple YouTube channels using Oscar Owen's 18-task YouTube AI Team system. The system covers the entire pre-production pipeline from research to scripting to channel positioning to monetisation outreach.

### Workspace structure
```
YouTube Team/
├── _SYSTEM/           → DASHBOARD.md, SESSION-LOG.md
├── _TEMPLATES/        → Templates, instructions, examples
│   ├── instructions/  → 6 instruction files covering all 18 tasks
│   ├── examples/      → Oscar Owen's example outputs (channel audit, playlist strategy)
│   ├── master-context-template.md
│   ├── task-snapshot-template.md
│   └── handoff-template.md
├── Quant-Trading/     → COMPLETED channel (16/18 tasks done, use as reference)
├── Cricket-Analytics/  → Empty folder structure ready
├── Gaming-Noob/       → Empty folder structure ready
└── Vasanth-Builds/    → Empty folder structure ready
```

Each channel has 6 phase folders with 18 task subfolders inside:
```
[Channel]/
├── 00 - Master Context Doc/
├── 01 - Ideas & Research/
│   ├── Task 1 - Content Research/
│   ├── Task 2 - Competitor Analysis/
│   └── Task 3 - Idea Validation/
├── 02 - Titles & Thumbnails/
│   ├── Task 4 - Title Generator/
│   └── Task 5 - Thumbnail Concept Generator/
├── 03 - Scripting/
│   ├── Task 6 - Brain Dump Organiser/
│   ├── Task 7 - Script Refiner/
│   ├── Task 8 - Intro Writer/
│   ├── Task 9 - Fluff Reducer/
│   └── Task 10 - CTA Inserter/
├── 04 - Community & Comments/
│   ├── Task 11 - Community Posts/
│   └── Task 12 - Comment Replies/
├── 05 - Channel & Positioning/
│   ├── Task 13 - Channel Audit/
│   ├── Task 14 - About Section/
│   ├── Task 15 - Banner/
│   └── Task 16 - Playlist Strategy/
└── 06 - Monetisation & Outreach/
    ├── Task 17 - Brand Outreach/
    └── Task 18 - Creator Collab/
```

### Where to find things
| What | Location |
|------|----------|
| Task instruction files | `YouTube Team/_TEMPLATES/instructions/` (6 files, one per phase) |
| Master Context template | `YouTube Team/_TEMPLATES/master-context-template.md` |
| Task snapshot template | `YouTube Team/_TEMPLATES/task-snapshot-template.md` |
| Handoff template | `YouTube Team/_TEMPLATES/handoff-template.md` |
| Oscar Owen examples | `YouTube Team/_TEMPLATES/examples/` |
| Dashboard (all channels) | `YouTube Team/_SYSTEM/DASHBOARD.md` |
| Session log | `YouTube Team/_SYSTEM/SESSION-LOG.md` |
| Quant Trading reference | `YouTube Team/Quant-Trading/` (completed example) |
| Cross-session memory | `/memories/yt-team-context.md` |

---

## SECTION 2 — BEFORE YOU DO ANYTHING

### Step 0: Read these files first (in this order)
1. `YouTube Team/_SYSTEM/DASHBOARD.md` — see what is done and what is not across all channels
2. `/memories/yt-team-context.md` — cross-session decisions and context
3. This handoff document (you are reading it)

### Step 1: Confirm channel identity with the user
Ask these questions one by one. Do NOT proceed until you have answers.

**Question 1 — Channel basics:**
> "Which channel are we building? Tell me:
> - Channel name (or working name)
> - What is it about in one sentence?
> - Who is your target viewer in one sentence?
> - What tone do you want? (e.g., nerdy + fun, serious + authoritative, casual + relatable)
> - Face on camera or faceless?"

**Question 2 — Content source:**
> "Do you have existing content, code, notes, or a project that this channel will be based on? If yes, tell me where the files are so I can read them for source material."

**Question 3 — Monetisation model:**
> "How do you plan to make money from this channel? (e.g., AdSense only, courses, sponsorships, consulting leads, affiliate links, no monetisation yet)"

**Question 4 — Experience level:**
> "Have you run a YouTube channel before? Any past attempts? This helps me calibrate how much guidance to give on setup decisions."

### Step 2: Fill the Master Context Doc
This is the single most important step. Every task reads from this document. If the Master Context is weak, every output will be generic.

**Process:**
1. Read `YouTube Team/_TEMPLATES/master-context-template.md`
2. Walk the user through ALL 10 sections interactively (see Section 3 below for the exact interview)
3. Save to `YouTube Team/[Channel]/00 - Master Context Doc/MASTER-CONTEXT.md`

---

## SECTION 3 — MASTER CONTEXT INTERVIEW (10 sections)

Walk the user through each section. Ask conversationally — do not dump all questions at once. Fill in their answers using the template structure.

### Section 1: Target Market
Ask:
- "Describe your ideal viewer. Age range, background, occupation, location?"
- "What situation are they in right now? What have they already tried?"
- "What do they need that they cannot currently find?"

### Section 2: "If You Are A..." Statements (need 10)
Ask:
- "Complete this sentence 10 different ways: 'If you are a [person] who [situation/desire]... this channel is for you.' Think about the different types of people who would watch."
- Help them brainstorm if they get stuck after 5-6.

### Section 3: Things They Have Tried (need 10)
Ask:
- "What has your ideal viewer already tried to solve their problem before finding your channel? Think: courses, YouTube videos, books, tools, communities, DIY attempts."

### Section 4: Primary Pains (need 10 with explanations)
Ask:
- "What are the top 10 frustrations, problems, or blockers your ideal viewer faces? For each one, explain why it hurts — what is the emotional or practical impact?"
- Movie scene column is optional (leave blank if user does not have ideas).

### Section 5: Primary Pleasures (need 10 with explanations)
Ask:
- "What are the top 10 outcomes, dreams, or wins your viewer wants to achieve? For each one, explain why it matters to them — what does it unlock in their life?"
- Movie scene column is optional.

### Section 6: "Without Having To..." Dreads (need 10)
Ask:
- "Complete this 10 times: 'My viewer wants [pleasure/outcome] WITHOUT HAVING TO [thing they dread doing].' What do they want to avoid on the way to their goal?"

### Section 7: Myths & Bad Common Advice (need 6+)
Ask:
- "What myths, bad advice, or wrong approaches do people in your niche commonly believe? What do gurus or popular content get wrong?"

### Section 8: Secret Sauce
Ask:
- "What is your unique method or framework? Give it a name (e.g., 'The [Name] Method'). Break it into 3 steps. For each step, list 3 bullet points explaining what happens."
- If they do not have a named method yet, help them create one from their content.

### Section 9: Channel Vision Statement
Ask them to fill in:
> "I help **[ideal viewer]** transition from **[pain point]** to **[goal]** so they can **[outcome]**."

### Section 10: Voice & Style Notes
Ask:
- "What tone should your videos have? (examples: nerdy, professional, casual, friendly, authoritative)"
- "What reading level? (assume viewer knows X, explain Y)"
- "What should the channel NEVER sound like?"
- "What should the channel ALWAYS embrace?"

---

## SECTION 4 — TASK EXECUTION ORDER

### Recommended order (proven on Quant Trading)

**Phase 5 first (if channel does not exist yet):**
```
Task 13 — Channel Setup Plan (name, format, visual identity decisions)
Task 14 — About Section
Task 15 — Banner Copy
```

**Then Phase 1:**
```
Task 1 — Content Research (generate video ideas from trends + ICP)
Task 2 — Competitor Gap Analysis (find what nobody else covers)
Task 3 — Idea Validation (score each video idea 0-10)
```

**Then Phase 2:**
```
Task 4 — Title Generator (20 titles per video, pick top 3)
Task 5 — Thumbnail Concepts (5 concepts per video, pick best)
```

**Then Phase 3 (per video or in bulk):**
```
Task 6 — Brain Dump Organiser (voice note → logical flow)
Task 7 — Script Refiner (logical flow → filming-ready script)
Task 8 — Hook Writer (90-second opening per video)
Task 9 — Fluff Reducer (tighten scripts to target length)
Task 10 — CTA Inserter (2 CTAs per script → Final Script)
```

**Then Phase 4:**
```
Task 11 — Community Posts (1 post per video, 50-150 words)
Task 12 — Comment Replies (post-launch only — needs real comments)
```

**Then Phase 6:**
```
Task 16 — Playlist Strategy (after 15+ videos planned/published)
Task 17 — Brand Outreach (3 brand suggestions + email template)
Task 18 — Creator Collab (3 creator suggestions + pitch email)
```

### Task dependencies
```
Master Context Doc ← EVERYTHING depends on this
Task 6 → Task 7 → Task 8 → Task 9 → Task 10 (strict chain)
Task 1 → Task 2 → Task 3 (recommended chain, not strict)
Task 4 → Task 5 (recommended, not strict)
All other tasks are independent once Master Context exists
```

---

## SECTION 5 — HOW TO EXECUTE EACH TASK

For every task:
1. Read the relevant instruction file from `YouTube Team/_TEMPLATES/instructions/`
2. Read the channel's `MASTER-CONTEXT.md`
3. Execute the task following the instruction file
4. Save output to the correct task folder: `YouTube Team/[Channel]/[Phase]/[Task]/`
5. Save a task snapshot using `YouTube Team/_TEMPLATES/task-snapshot-template.md`
6. Update `YouTube Team/_SYSTEM/DASHBOARD.md` with status
7. Update `YouTube Team/_SYSTEM/SESSION-LOG.md` with what was done

### Instruction file mapping
| Tasks | Instruction File |
|-------|-----------------|
| 1, 2, 3 | `01 - Ideas Agent Instructions.txt` |
| 4, 5 | `02 - Title and Thumbnail Agent Instructions.txt` |
| 6, 7, 8, 9, 10 | `03 - Script Writing Instructions.txt` |
| 11, 12 | `04 - Community And Comments Instructions.txt` |
| 13, 14, 15, 16 | `05 - Channel Positioning Instructions.txt` |
| 17, 18 | `06 - Outreach Agent Instructions.txt` |

### File naming convention
All output files follow: `[Description] — [DD Month YYYY].md`
Examples:
- `Content Research — 10 April 2026.md`
- `V3 — Triple Barrier Labeling — Final Script — 10 April 2026.md`
- `Community Posts — 10 April 2026.md`

---

## SECTION 6 — QUALITY LESSONS FROM QUANT TRADING

These are hard-learned lessons from the first channel build. Follow them to avoid repeating mistakes.

### Master Context
- A weak Master Context produces generic outputs across ALL 18 tasks. Spend real time on it.
- The "If You Are A..." statements and Pain/Pleasure lists are what make titles, hooks, and CTAs actually resonate.
- Movie scene column is optional — skip it if it slows things down.

### Task 1 — Content Research
- Do NOT generate generic "10 trending topics." Research the actual niche: YouTube search, Google Trends, competitor video view counts, Reddit/forum threads.
- Map video ideas to a series structure if the channel is course-style. A connected series (like MLQuant's 26-video plan) outperforms random standalone videos.
- Web research is essential — use real competitor data (SocialBlade, vidIQ) to validate demand.

### Task 2 — Competitor Analysis
- Research at least 8-10 channels. Get real numbers (subscriber counts, view counts, upload frequency) from SocialBlade.
- The most valuable output is the GAP MATRIX — what topics does nobody cover?
- Identify the #1 direct threat and articulate how this channel differentiates.

### Task 3 — Idea Validation
- Score every video idea 0-10 using ICP fit + CCN (Core/Casual/New viewer) + growth potential.
- Flag merge candidates (similar videos that could combine) and retitle candidates (weak cold-traffic titles).
- Front-load the highest-scoring videos in the release schedule.

### Task 4 — Title Generator
- Read the FULL Title Mastery Guide in the instruction file (100 frameworks). Do not skip it.
- Generate 20 titles per video, not 5. More options = better picks.
- Watch for framework overuse — if Framework #70 appears in 6/26 top picks, rotate.
- 60 character max per title. Trigger curiosity, desire, or fear.

### Task 5 — Thumbnail Concepts
- Each thumbnail targets ONE emotion only — no mixed signals.
- Thumbnail text should NEVER repeat the title — it should complete or amplify.
- For faceless channels: objects, diagrams, abstract visuals serve as the "face" element.

### Task 6 — Brain Dump Organiser
- If the user does not have voice notes, work with whatever they have (written notes, code documentation, project README, personal knowledge).
- Brain dumps should be substantial — 1,200-1,800+ words of source material per video. Thin brain dumps produce thin scripts.
- Flag [INFORMATION GAIN] moments (personal experience, real results, unique insights) and [NEEDS MORE] sections.

### Task 7 — Script Refiner
- Target word count depends on video length target. MLQuant used 2,300-3,850 words for 25-35 minute Indian English narration with code display pauses.
- Adjust for your channel: ~140 words per minute for conversational English, add 30-50% if there are visual pauses (code, diagrams, demos).
- Deep rewrite each script. A script refiner output should be FILMING READY — not an outline with headings.
- Mark [PERSONAL INSERT NEEDED] for any claim that requires the creator's actual data, story, or result.

### Task 8 — Hook Writer
- Each hook MUST be unique. Do NOT use a template and swap the topic.
- Structure: Hook Question → Credibility → Video Structure → Open Loop.
- 200-250 words max (90 seconds spoken).
- The hook must make the ideal viewer (from Master Context) feel "seen."

### Task 9 — Fluff Reducer
- This is actual editing, not just running the script through a filter.
- Preserve ALL [INFORMATION GAIN] moments. Remove: repetition, filler, unnecessary transitions, jargon.
- Verify every script hits the target word count range. Expand thin scripts and trim bloated ones.

### Task 10 — CTA Inserter
- Each video gets exactly 2 CTAs. Each CTA must reference that video's specific content.
- CTA 1: After Section 2 (first main value point). 3-4 sentences.
- CTA 2: At ~70% through the script. 1-2 sentences, shorter reminder.
- NEVER use generic CTAs. "If you are enjoying this series, hit subscribe" is lazy. Reference what was just taught.

### Task 11 — Community Posts
- One unique post per video. 50-150 words.
- Each post needs: distinctive hook, video-specific insight, natural CTA.
- Do NOT use a template with only the title swapped. Every post must be unique.
- British English. No hyphens. Short paragraphs (max 3 lines).

### Task 12 — Comment Replies
- Post-launch only. Cannot be done until real comments exist on published videos.

### Task 13-15 — Channel Setup, About, Banner
- Can be done early (before content research) since they only need the Master Context.
- Banner = one sentence. About section = 2-4 sentences max. Less is more.

### Task 16 — Playlist Strategy
- Maximum 3-4 playlists. 6-8 videos per playlist is ideal.
- A playlist with 14+ videos is too bloated — split it.
- Name playlists after VIEWER PAIN POINTS, not topics. "How to stop your system from blowing up" > "Risk Management Videos."

### Task 17 — Brand Outreach
- 3 brand suggestions that genuinely fit the channel's audience.
- Email template requires REAL personalization before sending — the user must find a specific recent thing from the brand.
- Include brand-specific value prop suggestions and which video each brand naturally fits into.

### Task 18 — Creator Collab
- Same structure as Task 17 but for creator collaborations.
- User must watch the target creator's latest video and find a genuine specific detail.

---

## SECTION 7 — AFTER EVERY TASK

1. **Save task snapshot** in the task folder using `YouTube Team/_TEMPLATES/task-snapshot-template.md`
2. **Update DASHBOARD.md** — set status to "done", add timestamp and snapshot link
3. **Update SESSION-LOG.md** — add session entry with actions, decisions, and next steps
4. **If the task feeds into another task**, create a handoff doc using `YouTube Team/_TEMPLATES/handoff-template.md`
5. **Git commit and push** at milestone points (after completing a phase or major task group)

---

## SECTION 8 — CHANNEL-SPECIFIC NOTES

### Channels waiting to be built

**Cricket Analytics**
- No Master Context yet — start from scratch
- User's knowledge area: cricket data and analytics
- Folder: `YouTube Team/Cricket-Analytics/`

**Gaming Noob**
- No Master Context yet — start from scratch
- Concept: gaming from a beginner/noob perspective
- Folder: `YouTube Team/Gaming-Noob/`

**Vasanth Builds**
- No Master Context yet — start from scratch
- Concept: live daily prep/building streams — commitment + inspiration
- Content scope: QF learning, Cricket Analytics projects, AI projects
- Not just learning — building real stuff live
- Folder: `YouTube Team/Vasanth-Builds/`

### Reference channel (completed)

**Quant Trading (MLQuant)** — 16/18 tasks done
- Master Context: `YouTube Team/Quant-Trading/00 - Master Context Doc/MASTER-CONTEXT.md`
- All task outputs in `YouTube Team/Quant-Trading/` — use as quality reference
- 26-video series (trailer + 25 main videos)
- Remaining: Task 12 (Comment Replies, post-launch) + Task 18 (Creator Collab)

---

## SECTION 9 — GIT WORKFLOW

- Remote: `https://github.com/vasanth-18085/YT_Team.git`
- Branch: `master`
- Local git config (not global): user `BeastSoul51430`, email `vasanth51430@gmail.com`
- Commit at milestone points with descriptive messages
- Push after each session or major phase completion

---

## SECTION 10 — QUICK START CHECKLIST

When the user says "start building [CHANNEL NAME]":

- [ ] Read DASHBOARD.md
- [ ] Read /memories/yt-team-context.md
- [ ] Confirm channel identity (Section 2, Step 1 questions)
- [ ] Run Master Context interview (Section 3, all 10 sections)
- [ ] Save MASTER-CONTEXT.md
- [ ] Begin Task 13 → 14 → 15 (channel setup)
- [ ] Begin Task 1 → 2 → 3 (content research)
- [ ] Begin Task 4 → 5 (titles and thumbnails)
- [ ] Begin Task 6 → 7 → 8 → 9 → 10 (scripting pipeline)
- [ ] Begin Task 11 (community posts)
- [ ] Begin Task 16 (playlist strategy)
- [ ] Begin Task 17 → 18 (outreach)
- [ ] Update DASHBOARD.md after every task
- [ ] Git commit + push at milestones

---

*Generated from the Quant Trading (MLQuant) channel build — 10 April 2026*
