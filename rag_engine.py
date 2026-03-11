import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq

load_dotenv()

# ── Step 1: Extract text from ALL uploaded PDFs ──
def extract_text_from_pdfs(pdf_files):
    all_pages = []

    for pdf_file in pdf_files:
        print(f"Reading PDF: {pdf_file.name}")  # debug log
        reader = PdfReader(pdf_file)
        print(f"  → {len(reader.pages)} pages found")  # debug log

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()

            if text and text.strip():
                all_pages.append({
                    "text": text,
                    "source": pdf_file.name,
                    "page": page_num + 1
                })

    print(f"Total pages extracted across all PDFs: {len(all_pages)}")  # debug log
    return all_pages


# ── Step 2: Split text into smaller chunks ──
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

    print(f"Total chunks created: {len(chunks)}")  # debug log
    return chunks, metadatas


# ── Step 3: Create vector store from ALL chunks ──
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


# ── Step 4: Search relevant chunks ──
def search_relevant_chunks(vector_store, question, k=6):
    # k=6 so we get chunks from MULTIPLE documents
    results = vector_store.similarity_search_with_score(question, k=k)
    return results


# ── Step 5: Generate answer using Groq ──
def generate_answer(question, relevant_chunks, pdf_names):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Build context — includes ALL retrieved chunks from ALL PDFs
    context = ""
    for i, (doc, score) in enumerate(relevant_chunks):
        source = doc.metadata.get("source", "Unknown")
        page   = doc.metadata.get("page", "?")
        context += f"\n--- Chunk {i+1} from: {source}, Page {page} ---\n"
        context += doc.page_content + "\n"

    # Tell the LLM exactly which PDFs were uploaded
    pdf_list = "\n".join([f"- {name}" for name in pdf_names])

    prompt = f"""You are a helpful assistant. The user has uploaded the following PDF documents:
{pdf_list}

Below are relevant excerpts retrieved from these documents:
{context}

Question: {question}

Instructions:
- Use information from ALL the documents listed above, not just one
- If the question asks to summarise multiple documents, summarise EACH one separately
- After each point mention which document and page it came from like: (Source: filename.pdf, Page 3)
- If information about a specific document is not in the retrieved chunks, say so clearly
- Be thorough and cover all uploaded documents

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2048  # increased so it has room to cover multiple docs
    )

    return response.choices[0].message.content


# ── Build vector store once (called when PDFs are uploaded) ──
def build_vector_store(pdf_files):
    pages_data = extract_text_from_pdfs(pdf_files)

    if not pages_data:
        return None, "No text could be extracted from the uploaded PDFs."

    chunks, metadatas = split_into_chunks(pages_data)
    vector_store = create_vector_store(chunks, metadatas)
    return vector_store, None


# ── Answer question using already-built vector store ──
def answer_question(vector_store, question, pdf_names):
    relevant_chunks = search_relevant_chunks(vector_store, question, k=6)
    answer = generate_answer(question, relevant_chunks, pdf_names)
    return answer, relevant_chunks