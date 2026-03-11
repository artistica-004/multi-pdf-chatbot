import streamlit as st
from rag_engine import build_vector_store, answer_question

# ── Page config ──
st.set_page_config(
    page_title="Multi-PDF Chatbot",
    page_icon="📚",
    layout="wide"
)

# ── Title ──
st.title("📚 Multi-PDF Chatbot")
st.markdown("Upload multiple PDFs and ask questions across all of them. The AI will tell you exactly which document and page each answer came from.")

st.divider()

# ── Sidebar: PDF upload ──
with st.sidebar:
    st.header("📂 Upload Your PDFs")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} PDF(s) uploaded")
        for f in uploaded_files:
            st.caption(f"📄 {f.name}")

    # ── Process button — builds vector store ONCE ──
    if uploaded_files:
        if st.button("🔄 Process PDFs", type="primary", use_container_width=True):
            with st.spinner("Processing all PDFs... please wait"):
                vector_store, error = build_vector_store(uploaded_files)

                if error:
                    st.error(error)
                else:
                    # Save to session state so it persists across questions
                    st.session_state.vector_store  = vector_store
                    st.session_state.pdf_names     = [f.name for f in uploaded_files]
                    st.session_state.chat_history  = []  # reset chat on new upload
                    st.success("✅ All PDFs processed! You can now ask questions.")

    # Show which PDFs are currently loaded
    if "pdf_names" in st.session_state:
        st.divider()
        st.markdown("**📋 Currently loaded:**")
        for name in st.session_state.pdf_names:
            st.caption(f"✅ {name}")

# ── Initialize chat history ──
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Show previous messages ──
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Question input ──
question = st.chat_input("Ask a question about your PDFs...")

if question:
    # Check if PDFs have been processed
    if "vector_store" not in st.session_state:
        st.warning("⚠️ Please upload PDFs and click **Process PDFs** first.")
    else:
        # Show user message
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        # Generate answer using the stored vector store
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching through your documents..."):
                answer, relevant_chunks = answer_question(
                    st.session_state.vector_store,
                    question,
                    st.session_state.pdf_names
                )

            st.markdown(answer)

            # Show source citations
            if relevant_chunks:
                with st.expander("📎 View source chunks used"):
                    for i, (doc, score) in enumerate(relevant_chunks):
                        source = doc.metadata.get("source", "Unknown")
                        page   = doc.metadata.get("page", "?")
                        st.markdown(f"**Chunk {i+1}** — `{source}` · Page {page}")
                        st.caption(doc.page_content[:300] + "...")
                        st.divider()

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })