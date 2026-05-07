# Mahabharatham Content AI — Engineering Spec
## YouTube Content Production Pipeline | Groq-Only

> **Version**: 1.0 — 2026-05-06
> **Purpose**: Produce production-ready video packages (script JSON + image prompts + metadata)
>   for all 7 channel pillars, from BORI source text.
> **Constraint**: Groq API only (free). No OpenAI, no Gemini, no paid APIs.
> **This is NOT a QA bot.** Input = video topic. Output = complete production package.

---

## What This Is vs What It Isn't

| | MahabharathamAI (QA Bot) | This Tool (Content AI) |
|---|---|---|
| **Input** | A user question | A video topic + pillar type |
| **Output** | A conversational answer | A production-ready JSON package |
| **Purpose** | Answer queries from the text | Generate YouTube videos |
| **Architecture** | RAG → LLM → hallucination check | Research → Script → Polish → Metadata |
| **Reuse** | Nothing | Nothing from QA bot |

---

## Data Foundation

### What We Have

```
~/Projects/MahabharathamAI/data/parsed_sections/
├── index.json                  ← 95 section entries, all 18 parvas listed
├── section_001.json            ← Adi Parva sections (19 total)
├── section_002.json
│   ...
└── section_095.json

Each section JSON:
{
  "section_number": int,
  "section_name": str,         ← Sub-parva name (e.g. "Sambhava Parva")
  "section_description": str,  ← Brief summary paragraph
  "parva_number": int,
  "parva_name": str,           ← One of 18 parva names
  "text": str,                 ← Full raw text from BORI PDF
  "page_start": int,
  "page_end": int
}
```

### Parva Coverage (All 18 Parvas Present)

| Parva | Sections | Notes |
|-------|---------|-------|
| Adi Parva | 19 | Largest — origins, curses, Kuru dynasty |
| Sabha Parva | 9 | Dice game, Draupadi humiliation |
| Aranyaka Parva | 16 | Forest exile, Yaksha questions |
| Virata Parva | 4 | Year in hiding |
| Udyoga Parva | 12 | Peace mission, warrior rankings |
| Bhishma Parva | 4 | Bhagavad Gita, first 10 days |
| Drona Parva | 8 | Abhimanyu, chakravyuha, Drona's death |
| Karna Parva | 1 | Day 17, Karna's death |
| Shalya Parva | 4 | Day 18, Duryodhana's fall |
| Sauptika Parva | 2 | Night massacre by Ashwatthama |
| Stri Parva | 4 | Gandhari's curse, women's grief |
| Shanti Parva | 4 | Bhishma on dharma and governance |
| Anushasana Parva | 1 | Bhishma's final teachings |
| Ashvamedhika Parva | 1 | Horse sacrifice |
| Ashramvasika Parva | 3 | Dhritarashtra's forest retirement |
| Mausala Parva | 1 | Dwarka's submersion, Yadava destruction |
| Mahaprasthanika Parva | 1 | The final journey |
| Svargarohana Parva | 1 | Heaven's gate, the dog |

### The Parva Map Layer (Build This First)

The raw section text is too large to feed into every Groq call. The solution is a
**pre-built Parva Map** per parva — a structured JSON that distills each parva into
a compact, queryable reference. Build once, use forever.

**Target output for each parva** (`parva_maps/adi_parva_map.json`):

```json
{
  "parva_name": "Adi Parva",
  "total_sections": 19,
  "total_pages": "444-1061",
  "summary": "One paragraph overview of the entire parva",
  "characters": {
    "Karna": {
      "role": "born of Kunti and the sun-god Surya",
      "key_events": ["tournament at Hastinapur", "crowned king of Anga by Duryodhana"],
      "sections_appearing": [5, 8, 12],
      "page_refs": [610, 720]
    }
  },
  "events": [
    {
      "event_id": "ADI_001",
      "title": "Vasu Uparichara establishes the Kuru dynasty",
      "section": "Sambhava Parva",
      "section_number": 3,
      "page": 490,
      "characters": ["Vasu Uparichara"],
      "summary": "2-3 sentence description",
      "raw_excerpt": "The first 300 chars of the relevant passage from text"
    }
  ],
  "sections": [
    {
      "section_number": 1,
      "section_name": "Anukramanika Parva",
      "pages": "444-460",
      "chapter_count": 1,
      "key_events_summary": "brief",
      "characters_mentioned": []
    }
  ]
}
```

**Why this layer exists**: Groq context limits are real. A 52K-char section of Adi Parva
will hit TPM limits fast. The map layer converts the raw text into a compact reference
(~5-8K tokens per parva map) that the script agent can use as context without burning tokens.

---

## Architecture

```
INPUT
  video_topic: str         e.g. "Bhishma rated Karna as Ardha-Rathi"
  pillar: str              one of: corrections | philosophy | mysteries |
                           character | narration | scaling | whatif
  primary_parvas: list     e.g. ["Udyoga Parva"]
  primary_characters: list e.g. ["Bhishma", "Karna"]

        │
        ▼

STAGE 1 — RESEARCH AGENT  (Groq: llama-4-scout-17b-16e-instruct)
  Load parva maps for relevant parvas.
  Load raw section text for high-relevance sections (page-windowed).
  Extract: key passages, BORI citations, character actions, quotes.
  Output: research_brief.json

        │
        ▼

STAGE 2 — SCRIPT AGENT  (Groq: llama-4-scout-17b-16e-instruct)
  Load research_brief + pillar-specific system prompt.
  Generate scene-by-scene script JSON (18-25 scenes).
  Each scene: narration + image_prompt + bori_ref + duration.
  Output: script_draft.json

        │
        ▼

STAGE 3 — POLISH AGENT  (Groq: llama-3.1-8b-instant)
  Check each scene's factual claims against research_brief.
  Flag unsupported claims. Return confidence score per scene.
  Optionally: rewrite low-confidence scenes.
  Output: script_final.json (with confidence scores)

        │
        ▼

STAGE 4 — METADATA AGENT  (Groq: llama-3.1-8b-instant)
  Input: script_final + pillar + primary_characters.
  Output: metadata.json
    - 3 title options (keyword-optimized, <60 chars)
    - SEO description (500 words)
    - 15 tags (tiered)
    - Chapter timestamps (from scene durations)
    - Thumbnail concept (6 words max)
    - Community post teaser (280 chars)

OUTPUT
  ~/Videos/Mahabharatham/{video_slug}/
  ├── research_brief.json
  ├── script_draft.json
  ├── script_final.json
  └── metadata.json
```

---

## Groq Model Assignment

| Stage | Model | Why |
|-------|-------|-----|
| Research | `meta-llama/llama-4-scout-17b-16e-instruct` | 130K context, best reasoning, handles long passages |
| Script | `meta-llama/llama-4-scout-17b-16e-instruct` | Long output, maintains narrative coherence |
| Polish | `llama-3.1-8b-instant` | Fast, cheap, good at structured fact-checking |
| Metadata | `llama-3.1-8b-instant` | Fast, structured JSON output |
| Parva Map Build | `meta-llama/llama-4-scout-17b-16e-instruct` | Needs reasoning to extract structured data from raw text |

**Token budget per video** (conservative estimate):
- Research: ~12K input, ~3K output
- Script: ~6K input, ~8K output
- Polish: ~10K input, ~2K output
- Metadata: ~3K input, ~2K output
- **Total per video: ~46K tokens** — well within free tier limits

---

## Per-Pillar System Prompts & Logic

This is the heart of the tool. Each pillar requires fundamentally different output.

---

### Pillar 1 — BORI Corrections

**What it needs to produce**: A video that identifies a widely-held misconception,
presents the BORI text counter-evidence, and explains why the gap exists.

**Script structure**:
1. Hook (30s): State the popular belief + why it's believed
2. The Evidence (60s): What BORI actually records — cite the exact parva, section, page
3. The Gap (90s): Why this divergence happened (folk tradition, TV show, retelling bias)
4. Deep Dive (8-12 min): Full BORI-sourced account of the event/claim in question
5. Reflection (3 min): What this correction changes about how we understand the epic
6. Outro (30s)

**Research agent prompt for this pillar**:
```
You are extracting evidence for a BORI Corrections video about: {topic}
The popular misconception is: {misconception}

From the following BORI source passages, extract:
1. Every passage that directly addresses this topic
2. The exact sequence of events as BORI records them
3. Any dialogue between characters related to this topic
4. The specific parva, section name, and page number for each passage

Format as: PASSAGE | PARVA | SECTION | PAGE

Do NOT paraphrase. Extract the actual text. If nothing in the passages directly
addresses the misconception, say "NOT COVERED IN THESE SECTIONS."
```

**Script agent prompt for this pillar**:
```
You are writing a YouTube script for a BORI Corrections video.
Channel: Vyasa's Witness — scholarly, authoritative English-language Mahabharata channel.
Topic: {topic}
Misconception being corrected: {misconception}
Research brief: {research_brief}

STRUCTURE: 18-22 scenes. Total narration: 6,000-8,000 words.
TONE: Like a documentary scholar who has lived with this text for years.
Never say "contrary to popular belief." Show, don't announce.
The BORI text speaks for itself. Your job is to present it fully.

For each scene output JSON:
{
  "scene_number": int,
  "scene_type": "hook|context|evidence|analysis|reflection|outro",
  "duration_seconds": int,
  "narration": str,          ← full narration text for this scene
  "bori_reference": str,     ← "Parva Name, Section Name, Page X"
  "image_prompt": str,       ← atmospheric, no photorealistic faces
  "ken_burns": "zoom_in|zoom_out|pan_left|pan_right"
}
```

---

### Pillar 2 — Philosophy Deep Dives

**What it needs to produce**: A video that builds a philosophical argument from
within the Mahabharata text itself — not imposing philosophy onto it, but extracting it.

**Script structure**:
1. Hook (45s): The philosophical question stated with full weight
2. Why This Question Matters (2 min): Stakes, universality, why BORI's answer is different
3. The Text's Own Framework (8-12 min): How the epic itself builds the argument, scene by scene
4. The Unresolved Tension (3 min): What the text leaves unanswered — and why deliberately
5. The Reflection (2 min): What this means for how we read the epic
6. Outro (30s)

**Research agent prompt**:
```
You are extracting material for a philosophy deep dive video about: {philosophical_question}
Relevant parvas: {parvas}

From the following BORI passages, extract:
1. Every passage where a character explicitly debates or embodies this philosophical question
2. Dialogue that represents competing positions on this question
3. Narrative moments where the text seems to take a position (or deliberately avoids one)
4. The specific parva, section, page for each passage

This is not a factual lookup. You are mapping the PHILOSOPHICAL ARCHITECTURE of
how this text engages with {philosophical_question}.
```

---

### Pillar 3 — Mysteries & Historical Evidence

**What it needs to produce**: A video that presents the text's claims about a
place, event, or phenomenon — then asks what they imply. Evidence-first, never speculative.

**Script structure**:
1. Hook (45s): The mystery stated. Not "was this real?" but "what does the text actually claim?"
2. The BORI Account (4-6 min): Every passage in BORI that directly describes this mystery
3. What It Implies (3-4 min): Logical implications of the text's own claims
4. The Historical/Archaeological Context (4-5 min): What external evidence says (framed as question)
5. What We Can Actually Conclude (2 min): Honest conclusion — what is textual, what is speculation
6. Outro (30s)

**Research agent prompt**:
```
You are extracting material for a mysteries video about: {mystery_topic}
(Examples: Dwarka's submersion, Kurukshetra astronomical references, Vimanas)

From the following BORI passages, extract ONLY what the text DIRECTLY STATES.
No interpretation yet. Raw text claims only.

For each claim, format as:
CLAIM: [what the text says]
PARVA: [parva name]
SECTION: [section name]
PAGE: [page number]
VERBATIM: [the exact passage from the text]

Then list: characters present, physical descriptions, measurements/distances if given,
temporal references if given.
```

---

### Pillar 4 — Character Studies

**What it needs to produce**: A complete character profile built from ALL parvas
where the character appears. The most research-intensive pillar.

**Script structure**:
1. Hook (45s): A single defining moment that captures the character's essence
2. Origins (3-4 min): Who they are when they enter the story
3. The Defining Decisions (8-10 min): 3-4 pivotal choices, what the text records them choosing
4. Relationships (3-4 min): Key relationships that define them — what the text actually records
5. The End (2-3 min): How they exit the story — what the text says
6. The Question (2 min): What this character leaves unresolved in the reader

**Research agent prompt**:
```
You are building a complete character profile of {character_name} from the BORI
Mahabharata for a 30-40 minute YouTube documentary.

From the following passages (covering all parvas where {character_name} appears):

1. FIRST APPEARANCE: Where and how does the text introduce them?
2. KEY ACTIONS: Every significant action or decision they take, in chronological order
3. KEY DIALOGUES: Every significant speech or exchange they have
4. RELATIONSHIPS: How the text describes their relationships with other characters
5. LAST APPEARANCE: How and where do they exit the story?
6. WHAT THE TEXT SAYS vs WHAT IT DOESN'T SAY: Are there gaps the text leaves open?

For each item: parva, section, page reference.
This is a CHARACTER ARCHAEOLOGY — pull everything the text gives us.
```

**Special handling**: Character studies need sections from MULTIPLE parvas loaded.
The research agent needs to load parva maps for ALL parvas where the character appears,
not just one. The `parva_maps/` layer is critical here.

---

### Pillar 5 — Parva Narration (Sequential)

**What it needs to produce**: A chapter-by-chapter narrative retelling of one
parva (or sub-parva), staying strictly sequential. This is the most text-faithful pillar.

**Script structure** (strict):
1. Context card (30s): Where in the epic are we? What just happened?
2. Sequential chapter narration: Follow the text chapter by chapter
3. Closing card (30s): What's coming in the next episode?

**This pillar uses the Parva Map directly as input**. The script agent doesn't
need the raw text — it works from the pre-built map.

**Research agent prompt** (different for this pillar — loads parva map, not raw text):
```
You are generating a narration script for: Mahabharata — {parva_name} | Episode {N}

This episode covers: Sections {start_section} to {end_section} (approximately {N} chapters)

Using the following parva map, generate scene-by-scene narration:
- Each chapter = 1-2 scenes
- Narrate in strict chronological order
- Include character dialogue where the text provides it
- Include chapter/section references naturally: "In chapter 45 of the Adi Parva..."
- Do NOT skip events to compress — if it's in the text, narrate it

Parva map: {parva_map_excerpt}
```

---

### Pillar 6 — Power Scaling & VS

**What it needs to produce**: A BORI-sourced analysis of warrior strength,
rankings, and direct encounters. Controversial, shareable, comment-generating.

**Script structure**:
1. Hook (30s): The question + why most answers you've seen are wrong
2. The BORI Rating System (3 min): Bhishma's Atiratha/Maharatha/Ardha-Rathi rankings
   from Udyoga Parva — the PRIMARY source for all rankings
3. Direct Encounter Evidence (8-10 min): Every time these two warriors directly clashed —
   what the text records happened
4. The Context Factors (3 min): Weapons, conditions, divine interventions — what the text says
5. The Verdict (2 min): What BORI actually supports vs what it leaves ambiguous

**Research agent prompt**:
```
You are extracting combat evidence for a power scaling video: {warrior1} vs {warrior2}

Step 1: From Udyoga Parva passages — extract Bhishma's EXACT ratings/classifications
of both warriors. Quote verbatim.

Step 2: From war parva passages — extract every DIRECT ENCOUNTER between {warrior1}
and {warrior2}. For each encounter:
  - Who struck first
  - What weapons were used
  - What the text records as the outcome
  - Any divine interventions mentioned
  - Page and section references

Step 3: Any passages where OTHER characters compare or comment on their relative strength.

Do NOT rank them yourself. Extract the evidence. The script agent will argue from evidence.
```

---

### Pillar 7 — What-If Simulations

**What it needs to produce**: A counterfactual video that identifies a pivot event,
establishes what BORI records actually happened, then traces the logical consequences
if the opposite had occurred — using only text-grounded causal chains.

**Script structure**:
1. Hook (30s): The pivot event stated. "On this day, this happened. But what if it hadn't?"
2. What Actually Happened (4-5 min): Full BORI account of the actual event
3. The Pivot (45s): The exact moment of the counterfactual — precise, not vague
4. The Cascade (10-12 min): Consequence chain — logically following from the text's own
   causal relationships. Each step grounded in what the text says would/wouldn't be
   possible given the change.
5. The Honest Limits (2 min): Where speculation begins and evidence ends
6. The Reflection (2 min): What this thought experiment reveals about the epic's design

**Research agent prompt**:
```
You are building the evidentiary foundation for a what-if video:
What if: {counterfactual}

Step 1: WHAT ACTUALLY HAPPENED — extract the full BORI account of the real event.
  Parva, section, page. Verbatim key passages.

Step 2: CAUSAL CHAINS — from the text, extract:
  - What did this event directly cause? (text-supported)
  - What alliances/enmities resulted from it?
  - What other characters' fates were bound to it?
  These are the dominoes. If the pivot changes, these dominoes fall differently.

Step 3: DEPENDENT EVENTS — list every subsequent event in the epic that
  the text explicitly links to this pivot event as cause and effect.

The script agent will build the counterfactual from these chains.
Do NOT speculate. Map the causal architecture.
```

---

## File Structure

```
~/Projects/MahabharathamYT/               ← NEW project, separate from QA bot
├── data/
│   ├── parva_maps/                       ← Pre-built (run build_parva_maps.py once)
│   │   ├── adi_parva_map.json
│   │   ├── sabha_parva_map.json
│   │   └── ... (18 total)
│   └── source/                           ← Symlink or copy from MahabharathamAI
│       └── parsed_sections/              ← The 95 section JSON files
│
├── pipeline/
│   ├── __init__.py
│   ├── run.py                            ← Entry point: python run.py --topic "..." --pillar corrections
│   ├── groq_client.py                    ← Simple Groq wrapper (just one key, rate-limited)
│   ├── research_agent.py                 ← Stage 1
│   ├── script_agent.py                   ← Stage 2
│   ├── polish_agent.py                   ← Stage 3
│   ├── metadata_agent.py                 ← Stage 4
│   └── pillar_prompts.py                 ← All 7 pillar system prompts (from this doc)
│
├── builders/
│   └── build_parva_maps.py               ← One-time: builds all 18 parva maps from raw sections
│
├── output/                               ← Per-video production packages
│   ├── karna_ardha_rathi/
│   │   ├── research_brief.json
│   │   ├── script_draft.json
│   │   ├── script_final.json
│   │   └── metadata.json
│   └── ...
│
└── .env                                  ← GROQ_API_KEY=...
```

---

## Output Schemas

### research_brief.json
```json
{
  "video_topic": str,
  "pillar": str,
  "parvas_searched": [str],
  "passages": [
    {
      "passage_id": str,
      "parva": str,
      "section_name": str,
      "page_start": int,
      "page_end": int,
      "relevance_score": float,     ← 0.0-1.0, assigned by research agent
      "excerpt": str,               ← Key 3-5 sentences
      "characters_present": [str],
      "event_type": str             ← "dialogue"|"action"|"description"|"prophecy"
    }
  ],
  "character_summary": {str: str},  ← {character_name: role_in_this_topic}
  "key_citations": [str],           ← ["Udyoga Parva, Bhishma Parva, Section 5, Page 2981"]
  "research_confidence": float      ← How well the parva text covers this topic
}
```

### script_final.json
```json
{
  "video_title": str,
  "pillar": str,
  "total_scenes": int,
  "estimated_duration_minutes": float,
  "estimated_word_count": int,
  "confidence_score": float,        ← From polish agent (average across scenes)
  "background_music_mood": str,
  "thumbnail_concept": str,
  "scenes": [
    {
      "scene_number": int,
      "scene_type": str,            ← hook|context|evidence|analysis|reflection|outro
      "duration_seconds": int,
      "narration": str,
      "bori_reference": str,        ← "Parva, Section, Page X"
      "image_prompt": str,          ← Ready to pass to Imagen 4 or FLUX
      "ken_burns": str,             ← zoom_in|zoom_out|pan_left|pan_right
      "confidence": float,          ← 0.0-1.0 from polish agent
      "flags": [str]                ← Any polish agent warnings
    }
  ]
}
```

### metadata.json
```json
{
  "title_options": [str, str, str],
  "selected_title": str,            ← Vasanth picks from options
  "description": str,               ← 500 words, SEO-optimized
  "tags": [str],                    ← 15 tags, tiered
  "chapters": [
    {"timestamp": "00:00", "title": str}
  ],
  "thumbnail_concept": str,
  "thumbnail_text": str,            ← Max 6 words
  "community_post": str,            ← 280 chars, post 3 days before upload
  "pinned_comment": str             ← BORI citation for pinned comment
}
```

---

## Build Order

Build in this exact order. Each step depends on the previous.

### Step 1 — Parva Map Builder (Foundation, Build Once)

**File**: `builders/build_parva_maps.py`

**What it does**: For each of the 18 parvas, loads all its raw section text,
sends to Groq, and generates a structured parva map JSON.

**Input**: `data/source/parsed_sections/*.json`
**Output**: `data/parva_maps/{parva_slug}_map.json`

**Prompt** (per section within a parva):
```
You are building a structured reference map of a section of the Mahabharata.

Section: {section_name}
Parva: {parva_name}
Pages: {page_start}-{page_end}

From the following raw text, extract and structure:

1. EVENTS: Every distinct narrative event, in order.
   Format: {{"event": str, "characters": [str], "page_approx": int, "verbatim_excerpt": str (first 200 chars)}}

2. CHARACTERS: Every named character who appears.
   Format: {{"name": str, "role_in_this_section": str}}

3. KEY_DIALOGUES: Every significant spoken exchange.
   Format: {{"speaker": str, "addressee": str, "summary": str, "page_approx": int}}

4. CROSS_REFERENCES: Any explicit references to other parvas or past/future events.

Output as raw JSON only. No commentary.

Raw text:
{text}
```

**Token strategy**: Process one section at a time. llama-4-scout-17b has 130K context,
but sections can be 50K+ chars. Chunk sections by 40K chars with 2K overlap if needed.

**Estimated cost**: 18 parvas × avg 5 sections × ~15K tokens = ~1.35M tokens total.
Free tier on llama-4-scout: 500K TPD × 3 keys = 1.5M/day. Runs in 1-2 days.

---

### Step 2 — Groq Client

**File**: `pipeline/groq_client.py`

Simple. No pool. No multi-key rotation (overkill for this use case).
Just: call Groq, handle rate limit with exponential backoff, return response.

```python
import os, time
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODELS = {
    "research": "meta-llama/llama-4-scout-17b-16e-instruct",
    "script":   "meta-llama/llama-4-scout-17b-16e-instruct",
    "polish":   "llama-3.1-8b-instant",
    "metadata": "llama-3.1-8b-instant",
}

def call(stage: str, system: str, user: str, temperature: float = 0.3) -> str:
    model = MODELS[stage]
    for attempt in range(4):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
                temperature=temperature,
                max_tokens=8192,
            )
            return resp.choices[0].message.content
        except Exception as e:
            if "rate_limit" in str(e).lower():
                time.sleep(2 ** attempt * 10)
            else:
                raise
    raise RuntimeError(f"Groq call failed after 4 attempts: stage={stage}")
```

---

### Step 3 — Research Agent

**File**: `pipeline/research_agent.py`

**Logic**:
1. Load `index.json` from parsed_sections
2. Filter sections by `parva_name` (using `primary_parvas` input or all if not specified)
3. Load parva maps for relevant parvas
4. Use parva maps to identify which sections are most relevant to the topic
5. Load raw text for top-N sections (N = 3-5 depending on pillar)
6. Call Groq with pillar-specific research prompt
7. Return `research_brief.json`

**Section relevance scoring** (simple keyword match before calling Groq):
```python
def score_section_relevance(topic: str, characters: list, section: dict) -> float:
    text = (section.get("section_description", "") + " " +
            section.get("section_name", "")).lower()
    score = 0
    topic_words = topic.lower().split()
    for word in topic_words:
        if word in text: score += 1
    for char in characters:
        if char.lower() in text: score += 2
    return score
```

This avoids burning Groq tokens on irrelevant sections.

---

### Step 4 — Script Agent

**File**: `pipeline/script_agent.py`

**Logic**:
1. Load `research_brief.json`
2. Load pillar system prompt from `pillar_prompts.py`
3. Build user message: research brief + scene structure instructions + tone guidelines
4. Call Groq script model
5. Parse JSON output (retry if malformed)
6. Return `script_draft.json`

**JSON parsing robustness** — Groq will sometimes return JSON with markdown fences:
```python
import json, re

def parse_json_response(text: str) -> dict:
    # Strip markdown fences
    text = re.sub(r"```json\n?|```\n?", "", text).strip()
    # Try direct parse
    try:
        return json.loads(text)
    except:
        # Find first { and last } as fallback
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
```

---

### Step 5 — Polish Agent

**File**: `pipeline/polish_agent.py`

**Logic**:
1. For each scene in `script_draft.json`
2. Check: does this scene's narration match the research_brief passages?
3. Flag any factual claim that isn't backed by a passage in research_brief
4. Assign confidence score 0.0-1.0 per scene
5. For scenes with confidence < 0.6: return flag, optionally rewrite

**Prompt**:
```
You are fact-checking a Mahabharata YouTube script against its research evidence.

Research passages (verified BORI sources):
{research_passages}

Script scene to check:
{scene_narration}

For each factual claim in the scene (characters' actions, events, dialogue, rankings):
- Is it directly supported by the research passages? (SUPPORTED / UNSUPPORTED / NEUTRAL)

Return JSON:
{
  "scene_number": int,
  "confidence": float,   ← fraction of claims that are SUPPORTED
  "unsupported_claims": [str],
  "flags": [str]
}
```

---

### Step 6 — Metadata Agent

**File**: `pipeline/metadata_agent.py`

**Prompt**:
```
Generate YouTube metadata for this Mahabharata video.

Video topic: {topic}
Pillar: {pillar}
Script summary (first 3 scenes narration): {hook_scenes}
Primary characters: {characters}
Primary parvas: {parvas}
Key BORI citations: {citations}

Channel: Vyasa's Witness — English, BORI-sourced, scholarly. Audience: Indian diaspora + philosophy readers.

Generate:
1. title_options: 3 titles. Primary keyword first. Max 60 chars. Authoritative, not clickbait.
2. description: 500 words. Include parva names, BORI citation, channel statement, keywords naturally.
3. tags: 15 tags. Tier 1 (broad): mahabharata, mahabharata documentary. Tier 2 (brand): bori mahabharata, bibek debroy. Tier 3 (video-specific): character + event.
4. chapters: from scene structure (scene_type = hook|context|evidence etc → timestamp blocks)
5. thumbnail_concept: visual description for Canva. Max 2 sentences.
6. thumbnail_text: max 6 words, high contrast readable at 120px.
7. community_post: 280 chars, post 3 days before upload.
8. pinned_comment: BORI citation to pin as first comment.

Output as JSON only.
```

---

### Step 7 — Entry Point

**File**: `pipeline/run.py`

```python
"""
Usage:
  python run.py \
    --topic "Bhishma rated Karna as Ardha-Rathi" \
    --pillar corrections \
    --parvas "Udyoga Parva" \
    --characters "Bhishma" "Karna"
"""
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--pillar", required=True,
        choices=["corrections","philosophy","mysteries","character","narration","scaling","whatif"])
    parser.add_argument("--parvas", nargs="+", default=[])
    parser.add_argument("--characters", nargs="+", default=[])
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    slug = args.topic.lower().replace(" ", "_")[:40]
    out = Path(args.output_dir) / slug
    out.mkdir(parents=True, exist_ok=True)

    from pipeline.research_agent import run_research
    from pipeline.script_agent import run_script
    from pipeline.polish_agent import run_polish
    from pipeline.metadata_agent import run_metadata

    print(f"[1/4] Research...")
    research = run_research(args.topic, args.pillar, args.parvas, args.characters)
    (out / "research_brief.json").write_text(research)

    print(f"[2/4] Script...")
    draft = run_script(args.topic, args.pillar, research)
    (out / "script_draft.json").write_text(draft)

    print(f"[3/4] Polish...")
    final = run_polish(draft, research)
    (out / "script_final.json").write_text(final)

    print(f"[4/4] Metadata...")
    meta = run_metadata(args.topic, args.pillar, final, args.characters, args.parvas)
    (out / "metadata.json").write_text(meta)

    print(f"\nDone. Output → {out}/")

if __name__ == "__main__":
    main()
```

---

## The Parva Summary Doc (What Vasanth Asked For)

The parva map builder produces one file per parva. But there's also a human-readable
version of each parva map that serves as a **reference document for Vasanth's own research** —
not for feeding to AI, but for Vasanth to read when planning videos.

**File**: `data/parva_summaries/adi_parva_summary.md`

This is generated separately from the map. Prompt:
```
Write a comprehensive chapter-by-chapter summary of {parva_name} from the following
section text. This is for a YouTube creator who will narrate this parva and needs to
know every significant event, character decision, and dialogue to plan their script.

Format:
## [Sub-parva Name]
### Chapter X
**Characters**: ...
**Event**: ...
**Key dialogue**: "..." (verbatim from text)
**Significance**: Why this matters for the larger epic arc

...

Be exhaustive. Don't skip chapters. Don't summarize away dialogue.
The creator needs enough detail to narrate this without reading the full text.
```

These summary docs also become the reference library Vasanth uses to validate
every BORI Correction video — the equivalent of "I read the actual text" as credibility.

---

## What This Gives You

| Need | How This Handles It |
|------|---------------------|
| BORI Corrections (P1) | Research agent finds contradicting passages. Script agent frames misconception vs text. |
| Philosophy (P2) | Research agent maps philosophical content. Script builds argument from within text. |
| Mysteries (P3) | Research agent extracts only what text STATES. No speculation injected. |
| Character Studies (P4) | Research agent pulls from ALL parvas for that character. Gives full arc. |
| Parva Narration (P5) | Works directly from parva maps. Chapter-level fidelity. |
| Power Scaling (P6) | Research agent extracts Udyoga Parva rankings + all combat encounters. |
| What-Ifs (P7) | Research agent maps causal chains first. Script builds counterfactual from them. |
| Source accuracy | Polish agent checks every scene against research passages. Confidence scored. |
| SEO/discoverability | Metadata agent uses BORI-specific terms that other channels don't target. |
| Groq-only constraint | All stages use llama-4-scout or llama-3.1-8b. Zero paid APIs. |

---

## Build Sequence (When You're Ready)

1. `builders/build_parva_maps.py` — run once per parva. Costs ~1.5M tokens total. Takes 1-2 days.
2. `pipeline/groq_client.py` — 30 lines. Write it.
3. `pipeline/research_agent.py` — builds on parva maps.
4. `pipeline/script_agent.py` + `pillar_prompts.py` — the creative core.
5. `pipeline/polish_agent.py` — fact-check layer.
6. `pipeline/metadata_agent.py` — structured output.
7. `pipeline/run.py` — wire it together.
8. Test on Video 1: "Karna Had No Choice" (Pillar 4: Character Study, Adi + Karna Parvas)

**Estimated build time**: 2-3 focused sessions of 3-4 hours each.
Total: ~10 hours to a working pipeline.

---

## Source Data Location

```
Parsed sections (all 18 parvas):
~/Projects/MahabharathamAI/data/parsed_sections/

BORI PDF (original source):
~/Downloads/Mahabharat critical edition -- Veda Vyasa, translated by Bibek debroy
  -- 2023 -- Bhandarkar Oriental Research Institute BORI -- ...pdf

Channel plan (video roadmap):
~/Projects/YT_Team/YouTube Team/Mahabharatham/MAHABHARAT_CHANNEL_PLAN.md
```

---

*This document is the spec. Build from this.*
*Channel plan = what to make. This spec = how to make it.*
