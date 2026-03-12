---
title: Multi Pdf Chatbot
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: Streamlit template space
license: mit
---

# Welcome to Streamlit!

Edit `/src/streamlit_app.py` to customize this app to your heart's desire. :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

# 📚 Multi-PDF Chatbot with Source Citations

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://shivani-multi-pdf-chatbot.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green)
![Groq](https://img.shields.io/badge/Groq-Llama3.3--70B-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

A Generative AI application that lets you upload multiple PDFs and ask questions across all of them simultaneously. The AI answers your questions and tells you **exactly which document and which page** the answer came from.

---

## 🚀 Live Demo

👉 **[Try it here → shivani-multi-pdf-chatbot.streamlit.app](https://shivani-multi-pdf-chatbot.streamlit.app/)**

---

## ✨ Features

- 📂 Upload **multiple PDFs** at once (up to 10 files)
- 💬 Ask questions **across all documents** simultaneously
- 📎 **Source citations** — see exactly which PDF and page number answered your question
- 🧠 Powered by **Llama 3.3 70B** via Groq API (free)
- ⚡ Fast semantic search using **ChromaDB** vector database
- 🔒 Secure API key handling with environment variables

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Core programming language |
| Streamlit | Frontend UI |
| LangChain | RAG pipeline framework |
| ChromaDB | Vector database for semantic search |
| HuggingFace Embeddings | Convert text to embeddings (all-MiniLM-L6-v2) |
| Groq API (Llama 3.3 70B) | LLM for generating answers |
| PyPDF2 | PDF text extraction |

---

## 📸 How It Works

```
Upload PDFs → Extract Text → Split into Chunks → Create Embeddings
→ Store in ChromaDB → Ask Question → Semantic Search
→ Retrieve Relevant Chunks → Generate Answer with Citations
```

---

## 🏃 Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/artistica-004/multi-pdf-chatbot.git
cd multi-pdf-chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free API key at [console.groq.com](https://console.groq.com)

### 5. Run the app
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 📋 Usage

1. **Upload PDFs** using the sidebar file uploader
2. Click **"Process PDFs"** button — waits for all files to be processed
3. **Ask any question** in the chat input at the bottom
4. View the answer with **source citations** showing which PDF and page was used
5. Click **"View source chunks"** to see the exact text used

---

## 📁 Project Structure

```
multi-pdf-chatbot/
│
├── app.py              # Streamlit UI and chat interface
├── rag_engine.py       # RAG pipeline (PDF extraction, embeddings, search, answer)
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore file
└── README.md           # This file
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key from console.groq.com |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 👩‍💻 Built By

**Shivani Chaudhary**
- GitHub: [@artistica-004](https://github.com/artistica-004)
- LinkedIn: [Shivani Chaudhary](https://linkedin.com/in/your-linkedin)

---

## 📄 License

This project is licensed under the MIT License.