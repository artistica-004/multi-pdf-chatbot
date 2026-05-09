import streamlit as st
from rag_engine import build_vector_store
from agent import run_agent

st.set_page_config(
    page_title="Multi-PDF Chatbot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Multi-PDF Chatbot")
st.markdown("Upload multiple PDFs and ask questions across all of them.")

st.divider()

# ── Sidebar ──
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

    if uploaded_files:
        if st.button("🔄 Process PDFs", type="primary", use_container_width=True):
            with st.spinner("Processing PDFs and generating summaries..."):
                vector_store, summaries, error = build_vector_store(uploaded_files)

                if error:
                    st.error(error)
                else:
                    st.session_state.vector_store = vector_store
                    st.session_state.pdf_names = [f.name for f in uploaded_files]
                    st.session_state.summaries = summaries
                    st.session_state.chat_history = []
                    st.session_state.followup_question = None
                    st.success("✅ Done! You can now ask questions.")

    if "summaries" in st.session_state:
        st.divider()
        st.markdown("**📋 PDF Summaries:**")
        for pdf_name, summary in st.session_state.summaries.items():
            with st.expander(f"📄 {pdf_name}"):
                st.caption(summary)

# ── Initialize session state ──
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "followup_question" not in st.session_state:
    st.session_state.followup_question = None

if "last_followups" not in st.session_state:
    st.session_state.last_followups = []

# ── Show chat history ──
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Show follow-up buttons OUTSIDE chat ──
if st.session_state.last_followups:
    st.markdown("**💡 You might also want to ask:**")
    cols = st.columns(len(st.session_state.last_followups))
    for i, q in enumerate(st.session_state.last_followups):
        with cols[i]:
            if st.button(q, key=f"fu_{i}", use_container_width=True):
                st.session_state.followup_question = q
                st.session_state.last_followups = []
                st.rerun()

# ── Get question from input or follow-up click ──
question = st.chat_input("Ask a question about your PDFs...")

if st.session_state.followup_question:
    question = st.session_state.followup_question
    st.session_state.followup_question = None

# ── Process question ──
if question:
    if "vector_store" not in st.session_state:
        st.warning("⚠️ Please upload PDFs and click Process PDFs first.")
    else:
        # Show user message
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        # Generate answer
        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent is thinking..."):
                answer, relevant_chunks, followups = run_agent(
                    st.session_state.vector_store,
                    question,
                    st.session_state.pdf_names
                )

            st.markdown(answer)

            # Save follow-ups to session state
            if followups:
                st.session_state.last_followups = followups

            # Show source chunks
            if relevant_chunks:
                with st.expander("📎 View source chunks used"):
                    for i, (doc, score) in enumerate(relevant_chunks):
                        source = doc.metadata.get("source", "Unknown")
                        page = doc.metadata.get("page", "?")
                        st.markdown(f"**Chunk {i+1}** — `{source}` · Page {page}")
                        st.caption(doc.page_content[:300] + "...")
                        st.divider()

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()