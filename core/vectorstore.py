import chromadb
from core.embeddings import embed_text

# One persistent client for the whole app
client = chromadb.PersistentClient(path="./chroma_db")

def get_collection(name: str):
    """Get or create a named collection."""
    return client.get_or_create_collection(name=name)

def add_documents(collection_name: str, docs: list[str], ids: list[str], metadata: list[dict] = None):
    """Embed and store documents in a collection."""
    collection = get_collection(collection_name)
    embeddings = [embed_text(doc) for doc in docs]
    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadata or [{} for _ in docs]
    )
    print(f"✅ Added {len(docs)} documents to '{collection_name}'")

def query(collection_name: str, query_text: str, n_results: int = 3) -> list[dict]:
    """Find the most similar documents to a query."""
    collection = get_collection(collection_name)
    embedding = embed_text(query_text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]