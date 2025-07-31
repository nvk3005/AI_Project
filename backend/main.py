from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os, shutil

load_dotenv()

UPLOAD_FOLDER = "uploads"
VECTOR_FOLDER = "vector_store"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_FOLDER, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load FAISS vector store khi app khởi động
    if os.path.exists(VECTOR_FOLDER) and os.listdir(VECTOR_FOLDER):
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        db = FAISS.load_local(VECTOR_FOLDER, embeddings, allow_dangerous_deserialization=True)
        app.state.db = db
        retriever = db.as_retriever()
        app.state.qa = RetrievalQA.from_chain_type(llm=OpenAI(), retriever=retriever)
    yield
    # Cleanup sau khi shutdown nếu cần

# 👉 Gọi FastAPI chỉ 1 lần, có lifespan
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    try:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(path, "wb") as f:
            f.write(await file.read())

        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif file.filename.endswith(".docx"):
            loader = Docx2txtLoader(path)
        else:
            return {"error": "Unsupported file type"}

        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)

        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        print("OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))  # ✅ chỉ để test

        db = FAISS.from_documents(chunks, embeddings)
        db.save_local(VECTOR_FOLDER)

        retriever = db.as_retriever()
        qa = RetrievalQA.from_chain_type(llm=OpenAI(), retriever=retriever)

        request.app.state.db = db
        request.app.state.qa = qa

        return {"message": f"Đã tải lên và xử lý {file.filename}"}

    except Exception as e:
        return {"error": f"Upload thất bại: {str(e)}"}

class QuestionRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(request: Request, body: QuestionRequest):
    qa = getattr(request.app.state, "qa", None)
    if qa is None:
        return {"error": "Chưa có tài liệu được tải lên"}
    result = qa.run(body.question)
    return {"answer": result}

@app.get("/stats")
async def stats(request: Request):
    db = getattr(request.app.state, "db", None)
    if not db:
        return {"message": "Chưa có dữ liệu"}
    return {
        "total_documents": len(db.docstore._dict),
        "total_chunks": len(db.index_to_docstore_id),
        "vector_store_size": len(db.index_to_docstore_id),
    }

@app.get("/reset")
async def reset():
    if os.path.exists(VECTOR_FOLDER):
        shutil.rmtree(VECTOR_FOLDER, ignore_errors=True)
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    os.makedirs(VECTOR_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    return {"message": "Đã xóa vector store và file tải lên"}
