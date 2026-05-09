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

# 📚 Multi-PDF Agentic Chatbot

Ask questions across multiple PDFs at once. 
Get answers with exact source citations — document name + page number.

## Live Demo
Try it here: https://huggingface.co/spaces/artistica-004/multi-pdf-chatbot

## 🎯 Objective

This project was built as part of Task 2A — Fix My Life with AI.

The goal was to identify a genuine real-world problem, 
design a practical AI solution for it, and demonstrate 
a measurable before vs after improvement.

---

## 😤 Step 1 — The Pain (Why This Was Built)

Every single study session I found myself with 4-5 PDF 
tabs open simultaneously. Finding one answer meant:

- Switching between tabs constantly
- Losing my train of thought every time I switched
- Re-reading the same sections because I forgot 
  which PDF had what
- Using Ctrl+F but not knowing which PDF to search first
- Spending 30-45 minutes just navigating — 
  before even starting to understand the content

**This happened every single day.**

I could not skip it — these were study materials and 
research documents I was required to understand deeply.
I could not delegate it — the comprehension was mine to do.

### Why existing tools failed:

| Tool | Why It Failed |
|------|--------------|
| Ctrl+F | One PDF at a time, exact keyword needed |
| Google | Cannot access private PDFs |
| ChatGPT | No grounding in actual documents, hallucinations |
| Adobe Acrobat | One file at a time, no semantic search |

**The real problem was not volume. 
It was context reconstruction from scattered sources.**

---

## 📋 Step 2 — Workflow Before This Tool

### Old process (10 steps):

1. Formulate the question in my head (~1 min)
2. Open 3-5 PDFs in separate browser tabs (~2 min)
3. Pick starting PDF based on gut feeling (~30 sec)
4. Ctrl+F with a keyword (~1-2 min)
5. Read surrounding context to check relevance (~3-5 min)
6. If not found — switch tab, repeat Ctrl+F (~1-2 min)
7. ⭐ Reconstruct mental context after tab switch (~5-10 min)
8. Cross-reference information across PDFs (~5 min)
9. Manually compile answer from fragments (~5 min)
10. Re-verify source page before using answer (~2 min)

**Total: 30-45 minutes per session**
**Most mentally demanding step: Step 7**
Reconstructing context after every tab switch — 
holding the original question, what was already read, 
and the current document all in working memory at once.

### Flowchart (Before):
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
|               Yes /      \ No
v               /            
[Read paragraph] <──          [Mark as no info]
|
[Does it answer the question?]
|
Yes / No
/      
[Note source] [Try synonym / different section]
|
[All PDFs checked?]
|
Yes / No
/      
[Compile] [Loop back]
|
[Verify source]
|
[Done]

---

## 🧠 Step 3 — AI Solution Design

### System Thinking

**Architecture chosen: Agentic Pipeline System**

| Architecture | Why Not Chosen |
|-------------|----------------|
| Single Prompt | Cannot handle raw PDFs, token limit exceeded |
| Basic Pipeline | No decision making, no adaptive behavior |
| Agent System ✅ | Decision making + multi-step execution + adaptive |

**Why Agent System:**
The bot needs to make decisions — is this question 
simple or complex? Should it search PDFs or the web? 
Does the answer actually exist in the documents?
These decisions require an agent, not just a pipeline.

### Full Architecture:
User Question
|
v
[Analyze Question — simple or complex?]
|
Complex ──────────────> [Break into sub-questions]
|                           |
Simple                [Search each sub-question]
|                           |
[Search PDFs]            [Combine all answers]
|                           |
[Check answer quality] <──────────
|
FOUND ──> [Generate follow-up questions] ──> [Final Answer]
|
NOT_FOUND ──> ["Not available in documents"]

### Data Layer

**Inputs and Outputs:**

| Stage | Input | Output |
|-------|-------|--------|
| PDF Extraction (PyPDF2) | Raw PDF files | Text + source + page per page |
| Chunking | Page text | 500-char chunks with metadata |
| Embedding (all-MiniLM-L6-v2) | Chunk strings | 384-dim vectors |
| Vector Store (ChromaDB) | Vectors + metadata | Searchable index |
| Retrieval | Question + k=6 | Top 6 relevant chunks |
| Generation (Groq LLaMA 3.3 70B) | Question + context | Cited answer |

**Why chunk_size=500, chunk_overlap=50:**
- 500 chars = 3-5 sentences = one focused concept
- Overlap of 50 ensures sentences on boundaries are not lost
- Smaller chunks = more precise embeddings = better retrieval

### Edge Cases

**Edge Case 1: Scanned PDF (image-based)**
- Current handling: PyPDF2 returns empty string, 
  page is skipped silently
- Impact: User gets no answer with no explanation why

**Edge Case 2: Answer spans chunk boundary**
- Current handling: 50-char overlap partially mitigates this
- Impact: LLM may receive incomplete context and 
  generate partial answer

**Edge Case 3: Question not in any PDF**
- Current handling: Agent checks answer quality, 
  returns "not available in documents" clearly
- Impact without handling: LLM halluculates 
  a confident-sounding wrong answer

### Failure Simulation

**Scenario: Groq API rate limit hit**

1. User uploads 4 PDFs and asks 10 rapid questions
2. generate_answer() call raises RateLimitError
3. User sees Python traceback — no friendly message
4. Root cause: Free Groq tier has tokens-per-minute limit
5. Fix: try/except around API call with friendly message
   and retry logic

### Trade-offs

**Trade-off 1: chunk_size=500 vs chunk_size=1000**
- Chose 500 for precise embeddings per concept
- Sacrificed: multi-paragraph argument retrieval
- Worth it: most questions are factual, not analytical

**Trade-off 2: Local embeddings vs OpenAI embeddings**
- Chose all-MiniLM-L6-v2 (local, free)
- Sacrificed: higher quality semantic matching
- Worth it: zero API cost, no data sent externally

---

## ✅ Step 4 — Proof of Concept

### Before vs After

| Metric | Before (Manual) | After (AI Tool) |
|--------|----------------|-----------------|
| Time to find answer | 30-45 min | 8-15 seconds |
| Steps required | 10 steps with loops | 3 steps |
| Accuracy | Keyword dependent | Semantically grounded |
| Context switching | 15-20 tab switches | Zero |
| Source traceability | Manual memory | Auto cited |
| Cross-doc synthesis | Manual notes | Automatic |

### Actual Prompt Sent to Groq:
You are a helpful and concise assistant.
The user has uploaded these PDF documents:

document1.pdf
document2.pdf

Relevant excerpts from the documents:
--- Chunk 1 from: document1.pdf, Page 3 ---
[chunk text]
Question: [user question]
Instructions:

Answer in maximum 4-5 lines only
Be direct and simple
No repetition
Mention source: (Source: filename.pdf, Page 3)
If not in documents say so clearly


### Sample Q&A:

**Example 1:**
- Question: "What is the role of AI in the playbook?"
- Answer: "AI is used to structure thinking, validate 
  decisions and accelerate learning — not to replace 
  thinking entirely. (Source: Intern Operating System V2.pdf, Page 3)"

**Example 2:**
- Question: "What is the salary structure?"
- Answer: "This information is not available 
  in the uploaded documents."

---

## 🔍 Final Reflection

**Q1: What is the weakest part?**
The chunk boundary problem. When an answer spans 
multiple paragraphs, k=6 may not retrieve all 
relevant chunks. Also scanned PDFs are silently 
skipped with no user warning.

**Q2: What single failure would break it completely?**
Groq API going down. Everything else runs locally 
but without Groq, answer generation completely fails. 
No fallback model exists currently.

**Q3: If AI was removed, what would still be valuable?**
Three things:
1. Multi-PDF aggregation in one interface
2. Chunk metadata system with source + page citations
3. Semantic similarity search — still better than Ctrl+F

---

## 🏗️ Architecture
app.py          — Streamlit UI + chat interface
agent.py        — Agentic decision making loop
rag_engine.py   — RAG pipeline + vector store
.env            — API keys
requirements.txt — Dependencies

---

## ⚙️ Agentic Features

- ✅ Decision Making — simple vs complex question handling
- ✅ Multi-Step Execution — complex questions broken into parts
- ✅ Workflow Orchestration — analyze → plan → execute → combine
- ✅ Adaptive Behavior — greetings handled separately
- ✅ Auto PDF Summarization — summary shown on upload
- ✅ Gap Detection — clearly states when answer not found
- ✅ Follow-up Suggestions — 3 related questions after every answer

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| LLM | Groq LLaMA 3.3 70B |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Vector Store | ChromaDB |
| PDF Extraction | PyPDF2 |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Agent Logic | Custom Python |

---

## 🚀 Run Locally

```bash
git clone https://github.com/artistica-004/multi-pdf-chatbot
cd multi-pdf-chatbot
pip install -r requirements.txt
```

Create `.env` file:
GROQ_API_KEY=your_groq_api_key_here

Run:
```bash
streamlit run app.py
```

---

## 📦 Requirements
streamlit
langchain
langchain-community
langchain-text-splitters
PyPDF2
chromadb
sentence-transformers
groq
python-dotenv

---

## 🔗 Links

- **Live Demo:**  https://huggingface.co/spaces/artistica-004/multi-pdf-chatbot
- **GitHub:** https://github.com/artistica-004/multi-pdf-chatbot

---

