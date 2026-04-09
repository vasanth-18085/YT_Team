# Task Snapshot — Title Generator

| Field | Value |
|-------|-------|
| **Date** | 2025-06-06 |
| **Channel** | MLQuant (Quant Trading) |
| **Task** | Task 4 — Title Generator |
| **Status** | done |
| **Session** | Session 6 — 06 June 2025 |

---

## Inputs

- Master Context Doc (MLQuant ICP, tone, audience profile)
- Task 1 output: 26-video content plan with topics and descriptions
- Task 3 output: Tier scores (S/A/B) for all 26 videos
- Oscar Owen's 100-Framework Title Mastery Guide (1106 lines)
- 20 title rules, psychological lever glossary

---

## Outputs

- **`All Videos — Title Options — 06 June 2025.md`** — Complete title options document
  - 20 titles per video × 26 videos = **520 total titles**
  - Top 3 recommendations per video with detailed reasoning
  - Summary table of all #1 picks
  - Framework distribution analysis with overuse warnings

---

## Decisions Made

1. **Batched generation by 2-3 videos at a time** — Sub-agent calls with more than 3 videos exceeded response length limits. 2 videos per batch was the sweet spot.
2. **Grouped by tier** — Started with Tier-S (highest impact), then A-High, A-Low, B. Ensures best videos get the most attention.
3. **Flagged framework overuse** — Framework #70 (DON'T Matter But THIS) appeared 6 times in top picks. Added note recommending rotation before final selection.
4. **Single consolidated file** — All 26 videos in one document rather than 26 separate files. Easier to compare and make final selections.

---

## Blockers

- None

---

## Next Steps

1. **User review** — Pick final title for each video from Top 3 (or mix elements)
2. **Address framework #70 overuse** — Swap 2-3 of the 6 top picks using #70 to their alternates
3. **Task 5 — Thumbnail Concepts** — Generate thumbnail concepts that pair with chosen titles

---

## Notes

- All titles are 60 chars or fewer (Rule 1)
- Browse-based framing (Rule 2) — designed for homepage/suggested feed, not search
- Bold statements favored over questions (Rule 12)
- Specific numbers used wherever possible (Rule 11)
- No generic AI-sounding language (Rule 5)
