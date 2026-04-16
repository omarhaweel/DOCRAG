import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_classic.chains import RetrievalQA
from chunker import chunk_pdfs
from Embedder import upsert_embeddings
from pathlib import Path

# Folder containing your PDF documents
DATA_FOLDER = Path("./documnets")
PDF_GLOB = "*.pdf"
ALREADY_EMBEDDED_FILE = Path("already_embedded.txt")


def load_pdf_files(data_folder: Path = DATA_FOLDER) -> list[str]:
    if not data_folder.exists():
        return []
    return sorted(str(p) for p in data_folder.glob(PDF_GLOB) if p.is_file())


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

INDEX_NAME = "new-index"

embeddings = OpenAIEmbeddings(
    model = "text-embedding-3-small"
)

llm = ChatOpenAI(
    model = "gpt-4o-mini",
    temperature = 0
)

vectorstore = PineconeVectorStore(
    index_name = INDEX_NAME,
    embedding = embeddings,
    pinecone_api_key = PINECONE_API_KEY
)

retriever = vectorstore.as_retriever(
    search_kwargs = {
        "k": 5
    }
)

qa_chain = RetrievalQA.from_chain_type(
    llm = llm,
    chain_type = "stuff",
    retriever = retriever
)


def get_answer(query: str) -> str:
    out = qa_chain.invoke({"query": query})
    if isinstance(out, dict):
        r = out.get("result")
        if r is not None:
            return str(r)
    return str(out)

def load_already_embedded() -> set[str]:
    if not ALREADY_EMBEDDED_FILE.exists():
        return set()
    lines = ALREADY_EMBEDDED_FILE.read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip()}

def save_already_embedded(embedded_files: set[str]) -> None:
    content = "\n".join(sorted(embedded_files))
    ALREADY_EMBEDDED_FILE.write_text(content + ("\n" if content else ""), encoding="utf-8")

def embed_new_files(pdf_paths: list[str]) -> None:
    embedded_files = load_already_embedded()
    for pdf_file_path in pdf_paths:
        if pdf_file_path in embedded_files:
            print(f"Skipping already embedded: {pdf_file_path}")
            continue

        print(f"Embedding new file: {pdf_file_path}")
        chunks = chunk_pdfs(pdf_file_path)
        if not chunks:
            print(f"No chunks extracted: {pdf_file_path}")
            continue

        upsert_embeddings(chunks, source_file=pdf_file_path)
        embedded_files.add(pdf_file_path)
        save_already_embedded(embedded_files)


def main(): 
    embed_new_files(load_pdf_files())
    while True:
        query = input("Enter your question: ")
        if query.lower() == "exit":
            break
        answer = get_answer(query)
        print(answer)
        print("--------------------------------")

if __name__ == "__main__":
    main()


# now we can ask questions about the documents
# e.g. "What is the main topic of the document?"
# "What is the main topic of the document?"