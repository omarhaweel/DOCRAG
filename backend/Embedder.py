import os
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pinecone_client.Index("new-index")

def embed_chunks(chunks: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    resp = openai_client.embeddings.create(model=model, input=chunks)
    return [item.embedding for item in resp.data]


# upsert the embeddings into pinecone
def upsert_embeddings(
    chunks: list[str],
    source_file: str,
    metadata: list[dict] | None = None,
):
    embeddings = embed_chunks(chunks)
    vectors = []
    source_key = source_file.replace("/", "_")
    for i, emb in enumerate(embeddings):
        base_metadata = {"text": chunks[i]}
        if metadata and i < len(metadata):
            base_metadata.update(metadata[i])
        base_metadata["source"] = source_file
        vectors.append({
            # Include source in the ID so new files don't overwrite old vectors.
            "id": f"{source_key}:{i}",
            "values": emb,
            "metadata": base_metadata,
        })
    index.upsert(vectors=vectors)

