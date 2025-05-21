from transformers import pipeline
from typing import List

# Load summarizer (free, local HuggingFace model)
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

def synthesize_themes(query: str, chunks: List[str], metadatas: List[dict]) -> List[dict]:
    # Group chunks into batches of 2-3 for better diversity
    chunks_grouped = [chunks[i:i + 3] for i in range(0, len(chunks), 3)]
    themes_output = []

    for idx, group in enumerate(chunks_grouped):
        # Prepare input text (limit to 2000 chars for t5-small)
        input_text = "\n".join(group)[:2000]

        # Run summarization
        try:
            summary = summarizer(input_text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        except Exception as e:
            summary = f"Failed to summarize theme {idx + 1}: {str(e)}"

        # Gather related filenames for this theme
        group_metadatas = metadatas[idx * 3: idx * 3 + len(group)]
        source_files = list({meta["filename"] for meta in group_metadatas})

        # Append theme object
        themes_output.append({
            "title": f"Theme {idx + 1}",
            "summary": summary,
            "documents": source_files
        })

    return themes_output
