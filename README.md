# RAG Document Q&A

A Retrieval-Augmented Generation (RAG) app that lets you ask questions about your PDF documents. PDFs are chunked, embedded via OpenAI, stored in Pinecone, and answers are generated with GPT-4o-mini.

## Architecture

\`\`\`
frontend/          React + TypeScript (Vite) — chat UI
backend/
  service.py       FastAPI — exposes POST /ask
  assistant.py     Orchestrates retrieval + LLM answer
  chunker.py       Splits PDFs into chunks
  Embedder.py      Upserts embeddings to Pinecone
  documnets/       Drop your PDF files here
\`\`\`

**Flow:** User asks question → FastAPI → Pinecone similarity search → top-5 chunks + question → GPT-4o-mini → answer returned to UI.

## Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- Pinecone API key (index name: `new-index`)

## Run Locally

### 1. Backend

\`\`\`bash
cd /path/to/RAG
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
\`\`\`

Create a `.env` file in the project root:

\`\`\`env
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
\`\`\`

Add PDFs to `backend/documnets/`, then start the API:

\`\`\`bash
cd backend
uvicorn service:app --reload --host 0.0.0.0 --port 8000
\`\`\`

### 2. Frontend

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

Open [http://localhost:5173](http://localhost:5173).

## Contributing

1. Branch off `dev`:
   \`\`\`bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   \`\`\`
2. Make your changes and commit:
   \`\`\`bash
   git add .
   git commit -m "feat: describe your change"
   git push origin feature/your-feature-name
   \`\`\`
3. Open a Pull Request from your branch → `dev`.
4. Once reviewed and merged into `dev`, open a separate PR from `dev` → `main` for release.
