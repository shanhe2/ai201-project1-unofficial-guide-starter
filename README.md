# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

RPI campus community knowledge including housing, clubs, social life, study spots, packing, and campus resources, sourced from student Reddit threads. This knowledge is valuable because it reflects unfiltered, peer-to-peer experience that dictates a student's actual day-to-day college life. Official university resources like admissions websites are designed for marketing and administration. These websites are lack real-time student opinions on which dorms have AC, what Greek life rush actually looks like, or which websites make scheduling bearable.


---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Reddit|First Year Housing Tier List |https://www.reddit.com/r/RPI/comments/1ap0cuk/first_year_housing/ |
| 2 |Reddit|Prospective Student Q&A |https://www.reddit.com/r/RPI/comments/1qevhdr/prospective_student/ |
| 3 |Reddit |Clubs recommanded |https://www.reddit.com/r/RPI/comments/cp98ps/what_clubsgroups_official_and_not_should_i_check/|
| 4 | Reddit|Social life opinions|https://www.reddit.com/r/RPI/comments/1ayi1im/social_life_is_it_really_that_bad/ |
| 5 |Reddit|On-campus gender inclusive housing |https://www.reddit.com/r/RPI/comments/1coxkbd/gender_inclusive_housing/ |
| 6 |Reddit|Accessing supercomputer resources |https://www.reddit.com/r/RPI/comments/28ds30/accessing_supercomputer_resources/|
| 7 |Reddit |Study spot recommandations for both on campus and off campus |https://www.reddit.com/r/RPI/comments/cf25ul/study_spots_onoff_campus/ |
| 8 |Reddit|Useful websites for better campus experience |https://www.reddit.com/r/RPI/comments/1n1wdpg/sites_you_need_to_know_about_as_an_incoming/ |
| 9 |Reddit|Incoming Freshman Packing List  |https://www.reddit.com/r/RPI/comments/uierkf/incoming_freshman_packing_list/ |
| 10 |Reddit |Dorm Room necessities |https://www.reddit.com/r/RPI/comments/v0cwth/dorm_room_necessities/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 400 characters

**Overlap:** 75 characters

**Why these choices fit your documents:** Documents were preprocessed by inserting === comment === delimiters between Reddit comments before chunking. The splitter splits on that delimiter first, keeping each person's opinion as an atomic unit, then sub-splits only within long comments. The Title: line is prepended to every chunk so retrieved chunks carry their subject even if sub-split.

**Final chunk count:** 145

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers

**Production tradeoff reflection:** If cost wasn't a constraint, I'll collect as many data as I could and use a commercial API model to weigh upgrade. The large language model is able to capture more slang and informal internet speech accurately. While an API model might offer better accuracy, it introduces network latency and requires sending student-generated data to a third-party server. The local MiniLM model guarantees zero network latency and complete data privacy.


---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** You may only answer using the numbered passages provided in the user message. Do not use any knowledge from your training data. Do not guess or infer details that are not explicitly stated in the passages.
If the passages do not contain enough information to answer the question, respond with exactly: "I don't have enough information in my sources to answer that." Write your answer as a single prose response. Do not number your answer or mirror the passage numbering.


**How source attribution is surfaced in the response:** After the model returns its answer, the corresponding code in generate.py collects sources directly from the retrieved chunk metadata. The LLM is not asked to produce citations.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 |What do students say about VCC North and VCC South? |It is pretty chill places to work in. |Correct answer retrieved | Relevant| Accurate|
| 2 |Does RPI have supercomputer cluster? |RPI has a bunch of supercomputer clusters. |Correct source retrieved. | Relevant| Accurate|
| 3 | What do people say about the Fall rush for Greek life? | Fall rush is now only open to sophomores and higher. | Core answer correct, extra detail from a second chunk| Relevant| Accurate|
| 4 | What do students say about the website QUACS|It's a godsend for picking classes  |Correct answer retrieved. | Relevant| Accurate|
| 5 |What do students say about the sq ft in Sharp dorm? | It's 101 sq ft.| it invented a list structure that doesn't exist in my prompt| Partially relevant|Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** What do students say about the sq ft in Sharp dorm?

**What the system returned:** The system returned a list of 5 sentences but only the first sentence include the correct answer. Sentences 2 said "No direct quote about sq ft, but it's mentioned that students get their own private room in Sharp." Sentences 3-5 all said "No information about Sharp dorm."

**Root cause (tied to a specific pipeline stage):**
the system prompt didn't prohibit the model from structuring its output as a numbered list mirroring the passage numbering.
**What you would change to fix it:** Add to the system prompt: "Do not number your answer or mirror the passage structure. Write a single prose response."

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** My planning.md Chunking Strategy section planned the 300–500 / 50–100 character targets upfront, which gave clear parameters to hand to the implementation. Without it, chunk size would have been arbitrary.

**One way your implementation diverged from the spec, and why:**  The spec described a plain RecursiveCharacterTextSplitter pass over the documents. During implementation it became clear the splitter couldn't distinguish between different people's comments (it's just a character counter). The approach was changed to insert === comment === delimiters at ingestion time so the splitter always cuts between people first, never across them.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* What are the ways to get my documents from Reddit websites.
- *What it produced:* Option A — Plain copy/paste (simplest)
Open each thread in your browser.
Select the post + the comments you want, copy.
Paste into a new .txt file in your documents/ folder.
Name each file after the topic, e.g. dorm_room_necessities.txt, first_year_housing.txt.
Tip: use old.reddit.com instead of www — same thread, much cleaner layout that copies without all the UI clutter. Just change the domain in the URL bar.

Option B — Save the JSON in your browser, then parse it (keeps structure)
The .json endpoint works in your real browser even though the script got 403'd:

In your browser, open each thread URL with .json appended, e.g. https://www.reddit.com/r/RPI/comments/v0cwth/dorm_room_necessities/.json
Ctrl+S → save it into a new raw/ folder (e.g. raw/dorm_room_necessities.json).
I give you a tiny parser that reads every file in raw/ and writes clean .txt files into documents/ — post + top-level comments, plain text, exactly like before but reading from disk instead of the network.
- *What I changed or overrode:* Since there's only 10 reddit websites as my source, I chose to follow option A. 

**Instance 2**

- *What I gave the AI:* As I'm following option A, is there a way to make sure chunking recognize the difference between different comments and one comment with several paragraphs?
- *What it produced:* What the chunker actually sees vs. what you want it to see
A RecursiveCharacterTextSplitter (your planning.md choice) does one thing: it counts characters up to your chunk size (~300–500), and when it has to cut, it prefers to cut at a separator — \n\n first, then \n, then a space. That's it. It has zero concept of "person," "opinion," or "comment." It's a character counter with a tie-breaker.
So the boundary you care about (one person's complete opinion) and the boundary the splitter uses (a blank line that happens to fall near the 500-char mark) are two different things that only sometimes line up. That mismatch is exactly why it feels hard — you're not imagining it.
The fix: encode the boundary the splitter can't infer
Since the chunker can't discover where one person stops, you tell it at ingestion time. Two levels:

1. Make each comment an atomic unit. Don't flatten everything into one blob and turn the splitter loose. Instead, split the document into comments first (on a delimiter you control), then only size-split within a comment if it's genuinely too long. One comment → one chunk (or several chunks that all belong to the same author).

2. Re-attach the subject to every chunk. Prefix each chunk with the thread title, so even a half-comment carries Title: First Year Housing — that's your defense for Challenge #1 in planning.md.

Concretely, the format I'd save in becomes:


Title: First Year Housing Tier List

=== comment ===
Really depends on what you value. Most people prefer...

=== comment ===
You can't live outside RPI residence halls till 3rd year...

=== comment ===
I always assumed most student-athletes get put in BARH...
Davison and Nugent. Every prospective freshman... (250 sq ft)...
Barton. If you're okay with a forced triple...
[the whole tier list — ONE person — stays in this block]
Then at chunk time you split on === comment === first. Each block is one author. A long block (like the tier list) gets sub-split by size within itself, so worst case you split one person's opinion — never merge two.
- *What I changed or overrode:* I followed the formatt it suggested. It made chunking step easier. 
