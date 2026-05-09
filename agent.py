import os
from dotenv import load_dotenv
from groq import Groq
from rag_engine import (
    search_relevant_chunks,
    generate_answer,
    generate_followup_questions
)

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_question(question):
    prompt = f"""Analyze this question.
Question: {question}

Reply in this exact format only:
TYPE: [simple/complex]
NEEDS_COMPARISON: [yes/no]"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50
        )
        return response.choices[0].message.content
    except Exception:
        return "TYPE: simple"


def break_into_subquestions(question):
    prompt = f"""Break this question into 2-3 smaller sub-questions
    that can be answered from a PDF document.
    Only ask questions that can be found in documents.
    Do not ask personal questions.


Question: {question}

Reply with only the sub-questions, one per line. Nothing else."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200
        )
        subquestions = response.choices[0].message.content.strip().split('\n')
        return [q.strip() for q in subquestions if q.strip()]
    except Exception:
        return [question]


def check_answer_quality(answer):
    prompt = f"""Does this answer contain actual information or does it say information is not available?

Answer: {answer}

Reply with only: FOUND or NOT_FOUND"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "FOUND"


def run_agent(vector_store, question, pdf_names):

    # Step 1 — Adaptive behavior
    greetings = ["hi", "hello", "hey", "thanks", "thank you", "okay", "ok"]
    if question.lower().strip() in greetings:
        return "Please ask a question related to your uploaded PDFs!", [], []

    try:
        # Step 2 — Decision making
        analysis = analyze_question(question)
        is_complex = "complex" in analysis.lower()

        if is_complex:
            # Step 3 — Break into sub-questions
            subquestions = break_into_subquestions(question)

            all_chunks = []
            all_answers = []

            # Step 4 — Multi-step execution
            for subq in subquestions:
                chunks = search_relevant_chunks(vector_store, subq, k=6)
                all_chunks.extend(chunks)
                answer, _ = generate_answer(subq, chunks, pdf_names)
                all_answers.append(f"**{subq}**\n{answer}")

            # Step 5 — Combine
            combined = "\n\n".join(all_answers)

            # Step 6 — Gap detection
            quality = check_answer_quality(combined)
            if quality == "NOT_FOUND":
                return "This information is not available in the uploaded documents.", all_chunks, []

            # Step 7 — Follow-up questions
            followups = generate_followup_questions(question, combined)

            return combined, all_chunks, followups

        else:
            # Simple question
            chunks = search_relevant_chunks(vector_store, question, k=6)
            answer, _ = generate_answer(question, chunks, pdf_names)

            # Gap detection
            quality = check_answer_quality(answer)
            if quality == "NOT_FOUND":
                return "This information is not available in the uploaded documents.", chunks, []

            # Follow-up questions
            followups = generate_followup_questions(question, answer)

            return answer, chunks, followups

    except Exception as e:
        return f"Something went wrong: {str(e)}", [], []