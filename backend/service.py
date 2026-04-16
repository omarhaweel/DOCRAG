# creating Fast API service to interact with each question
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from assistant import get_answer
from assistant import embed_new_files
from assistant import load_pdf_files
app = FastAPI(title="RAG Ask API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str




@app.post("/ask")
async def ask(body: AskRequest):
    q = body.question.strip()
    if q.lower() == "exit":
        return {"answer": "Goodbye!"}
    answer = get_answer(q)
    return {"answer": answer}


if __name__ == "__main__":
    embed_new_files(load_pdf_files())
    uvicorn.run(app, host="0.0.0.0", port=8000)
