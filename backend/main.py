"""
Turkish Financial PDF RAG System - FastAPI Backend
Main application entry point with API routes and configuration.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import json
import uuid
from datetime import datetime
import asyncio
import logging
from typing import List, Optional, Dict, Any

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_path = os.path.join(project_root, 'scripts')
sys.path.append(project_root)
sys.path.append(scripts_path)

# Import our existing RAG system
from scripts.groq_optimized_simple_rag import GroqOptimizedSimpleRAG
# PDF extractor and prompt optimizer can be imported later when needed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")  # Use existing key as fallback

# Initialize FastAPI app
app = FastAPI(
    title="Turkish Financial PDF RAG API",
    description="Production-ready Turkish financial document analysis with Groq RAG system",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
rag_system: Optional[GroqOptimizedSimpleRAG] = None

# In-memory storage for demo (replace with database in production)
documents_store: Dict[str, Dict[str, Any]] = {}
query_history: List[Dict[str, Any]] = []

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    document_id: Optional[str] = None
    language: str = "tr"
    
class QueryResponse(BaseModel):
    answer: str
    confidence: float
    response_time: float
    document_id: Optional[str] = None
    timestamp: str
    
class DocumentInfo(BaseModel):
    id: str
    filename: str
    size: int
    pages: int
    processed_at: str
    status: str
    
class SystemStats(BaseModel):
    total_documents: int
    total_queries: int
    avg_response_time: float
    avg_confidence: float
    system_status: str

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system components on startup."""
    global rag_system
    
    logger.info("🚀 Starting Turkish Financial PDF RAG System...")
    
    try:
        # Initialize RAG system with API key
        rag_system = GroqOptimizedSimpleRAG(groq_api_key=GROQ_API_KEY)
        
        logger.info("✅ RAG system initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG system: {e}")
        raise

@app.get("/api/health")
async def health_check():
    """System health check endpoint."""
    try:
        if rag_system is None:
            return JSONResponse({
                "status": "unhealthy",
                "error": "RAG system not initialized",
                "timestamp": datetime.now().isoformat()
            }, status_code=503)
            
        # Test RAG system with a simple query
        test_response = await asyncio.to_thread(
            rag_system.query, 
            "Test sorgusu"
        )
        
        return JSONResponse({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "rag_system": "operational",
            "test_response_time": test_response.get('query_time', 0),
            "version": "2.0.0"
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=503)

@app.post("/api/upload-pdf")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process PDF document."""
    
    filename = file.filename or "unknown.pdf"
    if not filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{doc_id}_{filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Store document info
        documents_store[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "file_path": file_path,
            "size": len(content),
            "status": "uploaded",
            "uploaded_at": datetime.now().isoformat(),
            "pages": 0,
            "message": "PDF uploaded successfully. Processing will be available in future versions."
        }
        
        return JSONResponse({
            "document_id": doc_id,
            "filename": filename,
            "size": len(content),
            "status": "uploaded",
            "message": "PDF uploaded successfully. The existing RAG system already has financial documents loaded."
        })
        
    except Exception as e:
        logger.error(f"PDF upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_pdf_background(doc_id: str, file_path: str):
    """Background task to process uploaded PDF (placeholder for future implementation)."""
    try:
        logger.info(f"🔄 Processing PDF: {doc_id}")
        
        # Update status
        documents_store[doc_id]["status"] = "processing"
        
        # TODO: Implement PDF processing integration
        # For now, just mark as completed
        documents_store[doc_id]["status"] = "completed"
        documents_store[doc_id]["processed_at"] = datetime.now().isoformat()
        documents_store[doc_id]["message"] = "Processing completed (demo mode)"
        
        logger.info(f"✅ PDF processing completed: {doc_id}")
        
    except Exception as e:
        logger.error(f"❌ PDF processing failed for {doc_id}: {e}")
        documents_store[doc_id]["status"] = "failed"
        documents_store[doc_id]["error"] = str(e)

@app.post("/api/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Submit query to RAG system."""
    try:
        if rag_system is None:
            raise HTTPException(status_code=503, detail="RAG system not initialized")
            
        logger.info(f"🔍 Processing query: {request.question[:50]}...")
        
        start_time = datetime.now()
        
        # Query RAG system directly (no prompt optimization for now)
        response = await asyncio.to_thread(
            rag_system.query,
            request.question
        )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        # Store query in history
        query_record = {
            "id": str(uuid.uuid4()),
            "question": request.question,
            "answer": response.get("answer", ""),
            "confidence": response.get("confidence", 0.0),
            "response_time": response_time,
            "document_id": request.document_id,
            "timestamp": end_time.isoformat(),
            "language": request.language
        }
        query_history.append(query_record)
        
        return QueryResponse(
            answer=response.get("answer", ""),
            confidence=response.get("confidence", 0.0),
            response_time=response_time,
            document_id=request.document_id,
            timestamp=end_time.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all processed documents."""
    documents = []
    for doc_data in documents_store.values():
        documents.append(DocumentInfo(
            id=doc_data["id"],
            filename=doc_data["filename"],
            size=doc_data["size"],
            pages=doc_data.get("pages", 0),
            processed_at=doc_data.get("processed_at", doc_data["uploaded_at"]),
            status=doc_data["status"]
        ))
    
    return documents

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """Get specific document details."""
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return documents_store[document_id]

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_data = documents_store[document_id]
    
    # Delete file
    try:
        if os.path.exists(doc_data["file_path"]):
            os.remove(doc_data["file_path"])
    except Exception as e:
        logger.warning(f"Failed to delete file: {e}")
    
    # Remove from store
    del documents_store[document_id]
    
    return {"message": "Document deleted successfully"}

@app.get("/api/query/history")
async def get_query_history(limit: int = 50):
    """Get query history."""
    return query_history[-limit:]

@app.get("/api/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system statistics."""
    total_queries = len(query_history)
    
    if total_queries > 0:
        avg_response_time = sum(q["response_time"] for q in query_history) / total_queries
        avg_confidence = sum(q["confidence"] for q in query_history) / total_queries
    else:
        avg_response_time = 0.0
        avg_confidence = 0.0
    
    return SystemStats(
        total_documents=len(documents_store),
        total_queries=total_queries,
        avg_response_time=avg_response_time,
        avg_confidence=avg_confidence,
        system_status="operational"
    )

@app.get("/api/config")
async def get_system_config():
    """Get system configuration."""
    return {
        "version": "2.0.0",
        "model": "llama-3.1-8b-instant",
        "embeddings": "paraphrase-multilingual-mpnet-base-v2",
        "vector_store": "FAISS",
        "supported_languages": ["tr", "en"],
        "max_file_size": "50MB",
        "supported_formats": ["pdf"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
