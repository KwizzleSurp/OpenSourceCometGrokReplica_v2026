"""agent/memory/chroma_store.py - Chroma RAG wrapper"""
import chromadb

def get_collection(project_id: str, persist_dir: str):
    client = chromadb.PersistentClient(path=persist_dir)
    return client.get_or_create_collection(
        name=project_id.replace("-","_"),
        metadata={"hnsw:space": "cosine"}
    )

def upsert_memory(collection, doc_id, text, metadata):
    collection.upsert(documents=[text], ids=[doc_id], metadatas=[metadata])

def query_memory(collection, query_text, n_results=5):
    return collection.query(query_texts=[query_text], n_results=n_results)

def delete_memory(collection, doc_id):
    collection.delete(ids=[doc_id])

def list_memories(collection, n=20):
    return collection.peek(limit=n)
