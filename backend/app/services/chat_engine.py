from transformers import pipeline
from typing import List

# Load HuggingFace generation model
qa_model = pipeline("text2text-generation", model="google/flan-t5-base")

def generate_answer(query: str, chat_history: List[str], chunks: List[str]) -> str:
    # Combine chunks for context
    context = "\n".join(chunks[:3])  # top 3 chunks max

    # Format chat history
    formatted_history = "\n".join([
        f"User: {chat_history[i]}" if i % 2 == 0 else f"Bot: {chat_history[i]}"
        for i in range(len(chat_history))
    ])

    # Build prompt
    prompt = f"""
You are a helpful assistant answering questions based on documents.

{formatted_history}

User: {query}

Relevant information from documents:
{context}

Answer the user's question concisely.
"""

    # Generate answer
    result = qa_model(prompt, max_length=150, do_sample=False)[0]['generated_text']
    return result.strip()
