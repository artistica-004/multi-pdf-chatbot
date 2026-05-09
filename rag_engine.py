import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq

load_dotenv()

def extract_text_from_pdfs(pdf_files):
    all_pages = []
    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                all_pages.append({
                    "text": text,
                    "source": pdf_file.name,
                    "page": page_num + 1
                })
    return all_pages


def split_into_chunks(pages_data):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = []
    metadatas = []
    for page in pages_data:
        splits = splitter.split_text(page["text"])
        for split in splits:
            chunks.append(split)
            metadatas.append({
                "source": page["source"],
                "page": page["page"]
            })
    return chunks, metadatas


def create_vector_store(chunks, metadatas):
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas
    )
    return vector_store


def search_relevant_chunks(vector_store, question, k=6):
    results = vector_store.similarity_search_with_score(question, k=k)
    return results


def generate_answer(question, relevant_chunks, pdf_names):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    context = ""
    for i, (doc, score) in enumerate(relevant_chunks):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")
        context += f"\n--- Chunk {i+1} from: {source}, Page {page} ---\n"
        context += doc.page_content + "\n"

    pdf_list = "\n".join([f"- {name}" for name in pdf_names])

    prompt = f"""You are a helpful and concise assistant. The user has uploaded these PDF documents:
{pdf_list}

Relevant excerpts from the documents:
{context}

Question: {question}

Instructions:
- Answer in maximum 4-5 lines only
- Be direct and simple, no unnecessary explanation
- No repetition at all
- Mention source like this: (Source: filename.pdf, Page 3)
- If answer is not in the documents say: "This information is not available in the uploaded documents."
- Do not say "based on the provided chunks" or "not provided in chunks"

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=512
    )
    return response.choices[0].message.content, []


def generate_pdf_summary(pdf_name, pages_data):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    text = ""
    for page in pages_data:
        if page["source"] == pdf_name:
            text += page["text"][:3000]
            break

    prompt = f"""Summarize this document in exactly 3-4 lines. Be very concise.

Document: {pdf_name}
Content: {text}

Summary:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].message.content


def generate_followup_questions(question, answer):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""Based on this question and answer, suggest exactly 3 short follow-up questions.

Question: {question}
Answer: {answer}

Reply with only 3 questions, one per line. Nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=150
    )
    questions = response.choices[0].message.content.strip().split('\n')
    return [q.strip() for q in questions if q.strip()][:3]


def build_vector_store(pdf_files):
    pages_data = extract_text_from_pdfs(pdf_files)
    if not pages_data:
        return None, None, "No text could be extracted from the uploaded PDFs."

    chunks, metadatas = split_into_chunks(pages_data)
    vector_store = create_vector_store(chunks, metadatas)

    summaries = {}
    pdf_names = list(set([p["source"] for p in pages_data]))
    for pdf_name in pdf_names:
        summaries[pdf_name] = generate_pdf_summary(pdf_name, pages_data)

    return vector_store, summaries, None


def answer_question(vector_store, question, pdf_names):
    relevant_chunks = search_relevant_chunks(vector_store, question, k=6)
    answer, _ = generate_answer(question, relevant_chunks, pdf_names)
    return answer, relevant_chunks