# creating Fast API service to interact with each question
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from assistant import get_answer
from assistant import embed_new_files
from assistant import load_pdf_files
import os
from contextlib import asynccontextmanager


ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", "http://localhost:5173"
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    embed_new_files(load_pdf_files())
    yield


app = FastAPI(title="RAG Ask API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0", port=8000)

