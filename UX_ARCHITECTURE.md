# UX Architecture — The Constructed Subject

**Status:** Governing product document  
**Purpose:** Ensure the public experience remains intellectually rigorous, emotionally legible, and structurally clear as the book expands.

## Core product premise

The website is not a landing page for a separate book. It is one medium of the book.

The interface must help a reader do three things:

1. **experience** a difficult case before being told what to conclude;
2. **separate** concepts that ordinary language collapses;
3. **inspect** the evidence, rival explanations, and unresolved questions.

The required sequence is:

> case → distinction → evidence → uncertainty → deeper manuscript

A module that does not advance this sequence must justify its existence or be removed.

---

# 1. The dual-lens rule

Every major interactive judgment should expose two views.

## Human lens

What feels morally, emotionally, or intuitively decisive to the reader?

Examples:

- recognition;
- attachment;
- fear;
- biological continuity;
- resemblance;
- survival;
- deception;
- responsibility.

## System lens

What do the available observations actually establish about the target system?

Examples:

- behavior supports one hypothesis but also fits rivals;
- a report is present but its generating mechanism is unknown;
- functional continuity is present but phenomenal continuity is not observed;
- a self-model exists but experience does not follow automatically;
- an aversion is reported but valence has not been mechanistically supported.

The interface must never shame the human lens or allow it to impersonate the system lens.

---

# 2. The four-layer model

The public experience should repeatedly distinguish four questions:

1. **Origin** — How was the system produced?
2. **Content** — What does the system represent or report?
3. **Organization** — What causal process does the system instantiate?
4. **Experience** — Is anything present for the system?

These layers are related but not interchangeable.

Forbidden inference:

> The content was generated, therefore no experience exists.

Also forbidden:

> The content sounds conscious, therefore experience exists.

The interface should make both errors visible.

---

# 3. No fake precision

The project must not use:

- a consciousness percentage;
- a sentience score;
- a decorative radar chart presented as measurement;
- arbitrary weights across theoretical indicators;
- a single color that means conscious or unconscious;
- numeric confidence without explicit calibration.

Permitted outputs:

- observed support;
- strongest rival explanation;
- still-unmeasured property;
- theory dependence;
- causal intervention result;
- confidence direction without false numerical precision.

Every evidence interface must preserve the distinction:

> evidence for subject-relevant organization ≠ direct observation of phenomenal consciousness

---

# 4. Progressive disclosure

The homepage should not present the entire research program simultaneously.

## First layer — one question

Can a false biography coexist with a real present subject?

## Second layer — one case

The synthetic person is introduced through controlled changes:

- apparent transfer;
- no transfer and generated autobiography;
- nonbiological substrate;
- replacement and termination.

## Third layer — conceptual separation

History, function, experience, and identity are separated.

## Fourth layer — evidence

Architecture, recurrence, perspective, persistence, valence, and causal intervention are introduced only after the reader understands why they matter.

## Fifth layer — research depth

Full chapters, ledgers, experiments, objections, and sources become available without interrupting the primary path.

---

# 5. Every interaction needs an epistemic return

An interaction is incomplete unless the reader receives:

1. **what their action indicates**;
2. **what it does not establish**;
3. **what evidence would be required next**.

Example:

- Reader selects: “A copy does not save this subject.”
- Human return: the reader distinguishes functional continuation from survival of a particular experiencer.
- System return: the conclusion remains conditional on a subject existing and copying producing a numerically distinct subject.
- Next evidence: instance-specific self-modeling, causal continuity, and a theory of subject identity.

This pattern must be reusable across chapters.

---

# 6. The manuscript must remain primary

Interactive experiences should not replace rigorous prose.

Each chapter can exist in three states:

- **planned** — structure visible, no complete argument yet;
- **readable research draft** — full argument available through the chapter reader;
- **interactive chapter** — full argument plus a designed participatory layer.

The chapter library must display these states plainly.

Raw Markdown should not be the default reader experience. Research drafts should open through the reading interface with:

- generated table of contents;
- progress indication;
- visible epistemic status;
- local chapter-specific notes;
- route back to the complete manuscript map.

---

# 7. AI-native interface principles

An AI-native interface does not mean adding a chatbot to every page.

It means exposing the kinds of structure an AI system would need to reason correctly:

- current state;
- claim status;
- causal dependencies;
- uncertainty;
- alternative hypotheses;
- missing evidence;
- memory provenance;
- continuity assumptions;
- falsification conditions.

The interface should make reasoning state visible without pretending to reveal private phenomenology.

Preferred language:

- “observed support”;
- “rival explanation”;
- “not measured”;
- “conditional on”;
- “would raise confidence”;
- “would lower confidence.”

Avoid:

- “AI thinks” when only output behavior is known;
- “the model feels” without evidence;
- “the test proves”;
- “the system is only simulating” as an unexplained conclusion;
- “the model understands” unless the relevant functional meaning is specified.

---

# 8. Human-native interface principles

The subject matter is cognitively demanding. The interface must reduce avoidable difficulty.

Requirements:

- one primary question per section;
- plain-language explanation before technical vocabulary;
- technical term shown after the idea is understood;
- no more than one dominant interaction per viewport;
- visible route forward;
- short labels, complete explanations;
- mobile controls large enough for touch;
- keyboard operation and meaningful focus states;
- reduced-motion support;
- no essential meaning encoded by color alone.

The design should feel serious, quiet, and investigative rather than futuristic for its own sake.

---

# 9. Required page anatomy

A major interactive chapter should contain:

1. **Question** — one precise problem.
2. **Scenario** — a controlled case.
3. **Reader action** — a judgment or evidence selection.
4. **Dual-lens return** — human and system interpretations.
5. **Conceptual decomposition** — terms separated.
6. **Rival explanation** — strongest alternative.
7. **Unresolved property** — what remains unknown.
8. **Research bridge** — chapter, claim IDs, experiments, and objections.
9. **Private note** — local-first reader reflection.

---

# 10. Current v2 correction

The first interface used several attractive but confusing patterns:

- too many equally weighted sections on the homepage;
- navigation labels that assumed prior knowledge;
- a radar visualization that looked more scientifically calibrated than it was;
- an assumption meter that compressed complex judgments into pseudo-scores;
- raw Markdown links for major chapter drafts;
- insufficient separation between emotional judgment and mechanistic evidence.

The v2 interface replaces those patterns with:

- three clear reader routes: experience, understand, inspect;
- one narrative progression;
- a dual human/system reasoning trace;
- checkbox-based evidence observations rather than weighted sliders;
- separate outputs for support, rival explanation, and missing evidence;
- a readable research-chapter system;
- visible status distinctions between interactive, draft, and planned chapters.

---

# 11. Acceptance test for future UI work

Before merging a public experience, answer:

- Can a new reader state the central question after the first screen?
- Does the interaction teach a distinction rather than merely entertain?
- Are observation, inference, and uncertainty separated?
- Is the strongest rival explanation visible?
- Does the interface avoid implying a consciousness detector exists?
- Can the reader reach the full argument?
- Can the experience be used on a phone and with a keyboard?
- Is the status of every claim or chapter clear?
- Does the design reveal reasoning structure rather than decorate ambiguity?

If any answer is no, the experience is not finished.
