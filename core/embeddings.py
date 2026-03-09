import ollama

def embed_text(text: str) -> list[float]:
    """Convert text to embedding vector using local Ollama model."""
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response["embedding"]

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Embed a list of text chunks."""
    return [embed_text(chunk) for chunk in chunks]