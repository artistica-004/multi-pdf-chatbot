---
title: Multi PDF Chatbot
emoji: 📚
colorFrom: blue
colorTo: blue
sdk: streamlit
sdk_version: "1.42.0"
python_version: "3.11"
app_file: app.py
pinned: false
---
# 📚 Multi-PDF Chatbot — Agentic RAG System

> **Task 2A — Fix My Life with AI (System Thinking)**  
> Built by: Shivani | Live Demo: https://huggingface.co/spaces/artistica-004/multi-pdf-chatbot

---

## Objective

Identify a genuine problem from your own life and design a practical AI solution for it. This task evaluates the ability to think clearly about real-world problems, not hypothetical ones.

---

## Step 1 — Identify the Pain

Every single study session — and that means every day — I find myself staring at 3 to 5 PDF tabs open simultaneously. The moment I need to find one specific answer, the real problem begins. I cannot just Ctrl+F, because I do not always know which PDF has the answer. So I search one document, don't find it, switch to the next tab, lose track of what I was looking for, scroll back, read a paragraph that is almost right but not quite, and then repeat the whole thing across every document.

This wastes **30–45 minutes per session** — not because the information is not there, but because I have no unified way to query across all of it at once. I cannot skip this. These are study materials, research papers, and internal docs that I am required to understand deeply. I cannot delegate it because the reading and comprehension is inherently mine to do.

**Why existing tools fail:**
- **Ctrl+F** — works inside one PDF, requires you to already know the exact keyword, gives no context
- **Google** — cannot access your private PDFs at all
- **ChatGPT without PDF context** — gives plausible-sounding answers with zero grounding in actual documents
- **Adobe Acrobat search** — still one file at a time, no semantic understanding, no synthesized answers

The core problem is not volume. It is **context reconstruction from scattered sources**. Every time I switch tabs, I lose the thread. That mental re-entry cost — multiplied by 15–20 tab switches per session — is where the time disappears.

---

## Step 2 — Document My Workflow (Before AI)

### Old Workflow — Step by Step

| Step | Action | Time |
|------|--------|------|
| 1 | Formulate question in my head | ~1 min |
| 2 | Open 3–5 PDFs in separate browser tabs | ~2 min |
| 3 | Choose starting PDF by gut feel | ~30 sec |
| 4 | Ctrl+F keyword search in first PDF | ~1–2 min |
| 5 | Read surrounding paragraph for context | ~3–5 min |
| 6 | If not found — switch tab, repeat | ~1–2 min |
| 7 | ⭐ Reconstruct mental context after switching | ~5–10 min |
| 8 | Cross-reference information across PDFs | ~5 min |
| 9 | Manually compile final answer | ~5 min |
| 10 | Verify by re-opening source page | ~2 min |

> ⭐ **Most mentally demanding step — Step 7: Context Reconstruction**  
> After switching tabs, working memory has to simultaneously hold the original question, what was already read, and what still needs to be found. This is where most cognitive energy is spent and why sessions feel exhausting.

**Total: 10 steps · 30–45 minutes per session · 15–20 tab switches**

### Flowchart — Before AI

```
[Need an answer]
       |
       v
[Open 3-5 PDFs in separate tabs]
       |
       v
[Choose starting PDF by intuition]
       |
       v
[Ctrl+F keyword]
       |
    FOUND? ──No──> [Switch tab, try next PDF]
       |                      |
      Yes             [Different keyword?]
       |               Yes /       \ No
       v              /              \
[Read paragraph] <──          [Mark as "no info"]
       |
[Does it answer the question?]
    Yes / No
     /       \
[Note source]  [Try synonym / different section]
     |
[All PDFs checked?]
    Yes / No
     /       \
[Compile answer]  [Loop back]
       |
[Verify source page]
       |
    [Done]
```

---

## Step 3 — Design the AI Solution

### System Thinking

**Architecture Chosen: Pipeline System**

| Option | Why Not |
|--------|---------|
| Single Prompt | Cannot handle raw PDFs — token limits exceeded immediately |
| Agent System | Overkill — adds latency and complexity for a well-defined problem |
| **Pipeline** ✅ | Sequential, deterministic stages — each with clear input and output |

### Full Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-PDF AGENTIC CHATBOT                    │
└─────────────────────────────────────────────────────────────────┘

  PDFs Uploaded
       │
       ▼
┌─────────────┐
│  PyPDF2     │  Extract text page by page
│  Extractor  │  → {text, source, page} per page
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Chunker   │  RecursiveCharacterTextSplitter
│  chunk=500  │  chunk_size=500, chunk_overlap=50
│  overlap=50 │  → List of chunks + metadata
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Embeddings │  HuggingFace all-MiniLM-L6-v2
│  MiniLM-L6  │  → 384-dim float vectors
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  ChromaDB   │  In-memory vector store
│ Vector Store│  → Searchable index
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│           AGENT LOOP                │
│                                     │
│  Question In                        │
│       │                             │
│       ▼                             │
│  [Greeting check] ──Yes──> Done     │
│       │                             │
│       ▼                             │
│  [Analyze: Simple or Complex?]      │
│       │                             │
│   Simple ──────────────────────┐   │
│       │                        │   │
│   Complex                      │   │
│       │                        │   │
│       ▼                        ▼   │
│  [Break into              [Direct  │
│   sub-questions]           Search] │
│       │                        │   │
│       ▼                        │   │
│  [Search each              k=6     │
│   sub-question]            chunks  │
│       │                        │   │
│       ▼                        │   │
│  [Combine answers]             │   │
│       │                        │   │
│       └──────────┬─────────────┘   │
│                  ▼                  │
│         [Gap Detection]             │
│          Found / Not Found          │
│                  │                  │
│                  ▼                  │
│       [Generate Answer]             │
│       Groq LLaMA 3.3 70B           │
│                  │                  │
│                  ▼                  │
│    [Follow-up Suggestions]          │
│                  │                  │
│                  ▼                  │
│      [Web Search Option]            │
│       Yes ──> SerpAPI               │
│       No  ──> Done                  │
└─────────────────────────────────────┘
       │
       ▼
  Final Answer with Source Citations
  (Source: filename.pdf, Page N)
```

### Data Layer

| Stage | Input | Output |
|-------|-------|--------|
| PDF Extraction (PyPDF2) | Raw .pdf file bytes | List of {text, source, page} dicts |
| Chunking | Page text strings | Chunk strings + metadata |
| Embedding (all-MiniLM-L6-v2) | Chunk strings | 384-dim float vectors |
| Vector Store (ChromaDB) | Vectors + metadata | Searchable in-memory index |
| Retrieval | Question string, k=6 | Top 6 (chunk, score) pairs |
| Generation (Groq LLaMA 3.3 70B) | Question + context | Answer with citations |

**Why chunk_size=500, chunk_overlap=50?**
- 500 characters ≈ 3–5 sentences — large enough for context, small enough for precision
- 50-character overlap ensures sentences at chunk boundaries are not lost
- Smaller chunks (200) risk splitting sentences; larger chunks (1000) embed too broad a topic

### Edge Cases

**Edge Case 1: Scanned PDF (image-based, no selectable text)**
- Current handling: PyPDF2 returns empty string, `if text and text.strip()` guard skips silently
- Impact if unhandled: User gets "no answer found" with no explanation — actively misleading

**Edge Case 2: Answer spans chunk boundary**
- Current handling: 50-character overlap partially mitigates this
- Impact if unhandled: LLM receives half a definition and may hallucinate the missing half

**Edge Case 3: Question has no relevant content in any PDF**
- Current handling: Gap detection checks answer quality and returns clear "not available" message
- Impact if unhandled: LLM generates confident-sounding answer from low-relevance chunks

### Failure Simulation

**Scenario: Groq API rate limit hit mid-session**

1. User uploads 4 PDFs and asks 10 rapid questions on free Groq tier
2. `generate_answer()` raises `RateLimitError` from Groq SDK
3. User sees unhandled Python exception — no friendly message, no retry
4. Root cause: Free tier enforces tokens-per-minute limits; no try/except around API call
5. Fix: Wrap in try/except, catch `groq.RateLimitError`, show friendly message with retry option

### Trade-offs

**Trade-off 1: chunk_size=500 vs chunk_size=1000**
- Chose 500 because: Smaller chunks produce more precise embeddings — one concept per chunk
- Sacrificed: Multi-paragraph answers may be split across more chunks than k=6 retrieves
- Worth it: Most questions are factual ("What is X?") — precision beats breadth

**Trade-off 2: HuggingFace local embeddings vs OpenAI embeddings**
- Chose all-MiniLM-L6-v2 (local) because: Zero API cost, no rate limits, user data stays local
- Sacrificed: OpenAI text-embedding-3-small produces higher quality embeddings
- Worth it: For a student-use tool with cost sensitivity, "good enough" retrieval + strong LLM works

---

## Step 4 — Proof of Concept

### Before vs After

| Metric | Before (Manual) | After (AI Tool) |
|--------|----------------|-----------------|
| Time to find answer | 30–45 min per session | 8–15 seconds per question |
| Steps required | 10 steps with loops | 3 steps: upload → process → ask |
| Accuracy | Hit or miss — keyword guessing | Source-cited, grounded in documents |
| Context switching | 15–20 tab switches | Zero |
| Cross-document synthesis | Manual note-taking | Automatic — k=6 pulls from all PDFs |
| Source traceability | Remember which tab had what | Every answer shows (Source: file.pdf, Page N) |

### Agentic Features Added

| Feature | What It Does |
|---------|-------------|
| Decision Making | Classifies question as simple or complex before answering |
| Multi-Step Execution | Breaks complex questions into sub-questions, answers each separately |
| Workflow Orchestration | Follows fixed sequence: analyze → plan → execute → combine → answer |
| Adaptive Behavior | Greetings handled separately; simple vs complex routed differently |
| Auto PDF Summarization | Generates 3–4 line summary per PDF shown in sidebar on upload |
| Follow-up Suggestions | Suggests 3 clickable related questions after every answer |
| Gap Detection | Clearly says "not in documents" instead of hallucinating |
| Web Search Integration | Offers Google web search via SerpAPI when answer not found or user wants more |

### Sample Prompt Sent to Groq

```
You are a helpful and concise assistant. The user has uploaded these PDF documents:
- Intern_Operating_System_V2.pdf
- AI_Departement.pdf

Relevant excerpts from the documents:
--- Chunk 1 from: Intern_Operating_System_V2.pdf, Page 3 ---
[chunk text...]

Question: What is the role of AI according to the playbook?

Instructions:
- Answer in maximum 4-5 lines only
- Be direct and simple, no unnecessary explanation
- Mention source like this: (Source: filename.pdf, Page 3)
- If answer is not in the documents say: "This information is not available in the uploaded documents."

Answer:
```

---

## Final Reflection

**Q1: What is the weakest part of your solution?**  
Scanned PDFs. If a PDF is image-based with no selectable text, PyPDF2 returns empty strings and the system silently skips those pages with no user warning. Also, answers requiring synthesis across long continuous passages may be incomplete because content is split across more chunks than k=6 retrieves.

**Q2: What single failure mode would break it completely?**  
Groq API unavailability. Every other component — PyPDF2, ChromaDB, HuggingFace embeddings — runs locally. But without Groq returning a response, answer generation fails entirely. There is no fallback model and no offline generation.

**Q3: If AI were removed, what would still be valuable?**  
Three things: (1) The multi-PDF interface — all documents in one place, better than juggling tabs. (2) The source citation system — every chunk tagged with filename and page number. (3) The semantic search — even without generation, returning the top 6 most relevant chunks is more useful than Ctrl+F.

---

## Tech Stack

```
Frontend     : Streamlit
LLM          : Groq LLaMA 3.3 70B (llama-3.3-70b-versatile)
Embeddings   : HuggingFace all-MiniLM-L6-v2
Vector Store : ChromaDB
PDF Parsing  : PyPDF2
Chunking     : LangChain RecursiveCharacterTextSplitter
Web Search   : SerpAPI (Google Search)
Agent Logic  : Custom Python (agent.py)
```

## What We Evaluate

- ✅ Real-world thinking
- ✅ Problem understanding
- ✅ Practical AI application
- ✅ Honesty and self-reflection

---

## Live Demo

Try it here: https://huggingface.co/spaces/artistica-004/multi-pdf-chatbot

