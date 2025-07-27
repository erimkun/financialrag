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
import time
from datetime import datetime
import asyncio
import logging
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_path = os.path.join(project_root, 'scripts')
sys.path.insert(0, project_root)
sys.path.insert(0, scripts_path)

# Import our existing RAG system
try:
    from scripts.groq_optimized_simple_rag import GroqOptimizedSimpleRAG  # type: ignore
    ORIGINAL_RAG_AVAILABLE = True
except ImportError:
    try:
        from groq_optimized_simple_rag import GroqOptimizedSimpleRAG  # type: ignore
        ORIGINAL_RAG_AVAILABLE = True
    except ImportError:
        ORIGINAL_RAG_AVAILABLE = False
        GroqOptimizedSimpleRAG = None  # type: ignore

try:
    from scripts.memory_optimized_groq_rag import MemoryOptimizedGroqRAG  # type: ignore
    MEMORY_RAG_AVAILABLE = True
except ImportError:
    try:
        from memory_optimized_groq_rag import MemoryOptimizedGroqRAG  # type: ignore
        MEMORY_RAG_AVAILABLE = True
    except ImportError:
        MEMORY_RAG_AVAILABLE = False
        MemoryOptimizedGroqRAG = None  # type: ignore
        MEMORY_RAG_AVAILABLE = False
        MemoryOptimizedGroqRAG = None

from scripts.hybrid_pdf_extractor import HybridPDFExtractor  # type: ignore
# Additional modules imported at startup

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# Environment Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")

# RAG System Configuration
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "../vector_store")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

# Validate required environment variables
if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
    logger.error("❌ GROQ_API_KEY is not configured!")
    logger.error("📝 Please follow these steps:")
    logger.error("   1. Copy backend/.env.example to backend/.env")
    logger.error("   2. Get your API key from: https://console.groq.com/keys")
    logger.error("   3. Update GROQ_API_KEY in backend/.env file")
    logger.error("   4. Restart the backend server")
    raise ValueError("GROQ_API_KEY environment variable is required")

logger.info(f"🔑 API Key configured: {GROQ_API_KEY[:10]}...")
logger.info(f"🌐 Server will run on {SERVER_HOST}:{SERVER_PORT}")
logger.info(f"🎯 CORS origins: {CORS_ORIGINS}")
logger.info(f"🤖 Groq model: {GROQ_MODEL}")

# Ensure uploads directory exists
os.makedirs(UPLOADS_DIR, exist_ok=True)

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
    allow_origins=[origin.strip() for origin in CORS_ORIGINS],  # From environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components  
rag_system = None  # Will be initialized based on available modules
USE_MEMORY_OPTIMIZED = os.getenv("USE_MEMORY_OPTIMIZED", "false").lower() == "true"

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

# Utility Functions
async def load_existing_documents():
    """Load existing documents from analysis output directory."""
    global documents_store
    
    analysis_dir = "analysis_output"
    if not os.path.exists(analysis_dir):
        logger.info("📁 No analysis directory found")
        return
    
    analysis_files = [f for f in os.listdir(analysis_dir) if f.endswith('_complete_analysis.json')]
    logger.info(f"📄 Found {len(analysis_files)} analysis files")
    
    for analysis_file in analysis_files:
        try:
            analysis_path = os.path.join(analysis_dir, analysis_file)
            with open(analysis_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract document info
            doc_info = data.get('document_info', {})
            filename = doc_info.get('filename', data.get('filename', analysis_file.replace('_complete_analysis.json', '.pdf')))
            
            # Create document ID from filename or use analysis file prefix
            if analysis_file.startswith(('20250', 'analysis_')):
                doc_id = analysis_file.replace('_complete_analysis.json', '')
            else:
                # UUID format: extract UUID part
                doc_id = analysis_file.split('_')[0] if '_' in analysis_file else analysis_file.replace('.json', '')
            
            # Get file stats
            file_stats = os.stat(analysis_path)
            processed_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
            
            # Get pages count from correct field
            pages_count = data.get('pages', doc_info.get('total_pages', 0))
            
            # Add to documents store
            documents_store[doc_id] = {
                "id": doc_id,
                "filename": filename,
                "size": file_stats.st_size,
                "pages": pages_count,
                "uploaded_at": processed_at,
                "processed_at": processed_at,
                "status": "processed",
                "analysis_file": analysis_path
            }
            
            logger.info(f"📄 Loaded document: {filename} ({doc_id})")
            
        except Exception as e:
            logger.error(f"❌ Failed to load analysis file {analysis_file}: {e}")
    
    logger.info(f"✅ Loaded {len(documents_store)} documents from analysis files")

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system components on startup."""
    global rag_system, documents_store
    
    logger.info("🚀 Starting Turkish Financial PDF RAG System...")
    
    try:
        # Initialize RAG system with API key
        # Type assertion since we validated GROQ_API_KEY above
        assert GROQ_API_KEY is not None, "GROQ_API_KEY should be validated above"
        
        # Load existing documents from analysis output
        await load_existing_documents()
        
        # Check if there are existing analysis files and load the latest one
        analysis_dir = "analysis_output"
        latest_path = None
        
        if os.path.exists(analysis_dir):
            analysis_files = [f for f in os.listdir(analysis_dir) if f.endswith('_complete_analysis.json')]
            if analysis_files:
                # Get the latest file by modification time
                latest_file = max(analysis_files, key=lambda f: os.path.getmtime(os.path.join(analysis_dir, f)))
                latest_path = os.path.join(analysis_dir, latest_file)
                logger.info(f"🔄 Loading existing analysis file: {latest_file}")
        
        # Choose RAG system based on configuration and availability
        if USE_MEMORY_OPTIMIZED and MEMORY_RAG_AVAILABLE:
            logger.info("🔧 Using Memory Optimized RAG System")
            rag_system = MemoryOptimizedGroqRAG(
                groq_api_key=GROQ_API_KEY, 
                specific_analysis_file=latest_path,
                lite_mode=True  # Start with lite mode for safety
            )
        elif ORIGINAL_RAG_AVAILABLE:
            logger.info("� Using Original RAG System")
            if latest_path:
                rag_system = GroqOptimizedSimpleRAG(groq_api_key=GROQ_API_KEY, specific_analysis_file=latest_path)
            else:
                rag_system = GroqOptimizedSimpleRAG(groq_api_key=GROQ_API_KEY)
        elif MEMORY_RAG_AVAILABLE:
            logger.warning("⚠️ Falling back to Memory Optimized RAG (Original not available)")
            rag_system = MemoryOptimizedGroqRAG(
                groq_api_key=GROQ_API_KEY,
                specific_analysis_file=latest_path,
                lite_mode=True
            )
        else:
            raise ImportError("No RAG system implementation available")
        
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
        if USE_MEMORY_OPTIMIZED:
            test_result = await asyncio.to_thread(
                rag_system.retrieve_and_generate,
                "Test sorgusu"
            )
            response_time = 0  # Memory optimized RAG doesn't return timing
        else:
            test_response = await asyncio.to_thread(
                rag_system.query, 
                "Test sorgusu"
            )
            response_time = test_response.get('query_time', 0) if isinstance(test_response, dict) else 0
        
        return JSONResponse({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "rag_system": "operational",
            "test_response_time": response_time,
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
        
        # Store document info with processing status
        documents_store[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "file_path": file_path,
            "size": len(content),
            "status": "processing",
            "uploaded_at": datetime.now().isoformat(),
            "pages": 0,
            "message": "PDF uploaded successfully. Processing started..."
        }
        
        # Start background processing
        background_tasks.add_task(process_pdf_background, doc_id, file_path)
        
        return JSONResponse({
            "document_id": doc_id,
            "filename": filename,
            "size": len(content),
            "status": "processing",
            "message": "PDF uploaded successfully. Processing started in background."
        })
        
    except Exception as e:
        logger.error(f"PDF upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_pdf_background(doc_id: str, file_path: str):
    """Background task to process uploaded PDF and integrate into RAG system."""
    global rag_system
    
    try:
        logger.info(f"🔄 Processing PDF: {doc_id}")
        
        # Update status
        documents_store[doc_id]["status"] = "processing"
        
        # Extract content from PDF
        logger.info(f"📖 Extracting content from: {file_path}")
        extractor = HybridPDFExtractor(file_path)
        
        # Get text content
        text_data = extractor.extract_text_pdfplumber()
        
        # Calculate pages
        pages_count = len(text_data)
        documents_store[doc_id]["pages"] = pages_count
        
        # Extract all text content
        full_text = ""
        for page_data in text_data:
            full_text += f"\n{page_data.get('metin', '')}"
        
        # Create new RAG system with the uploaded document
        logger.info(f"🤖 Initializing new RAG system with uploaded document...")
        
        # Create analysis output file for the new document
        analysis_file = f"analysis_output/{doc_id}_complete_analysis.json"
        os.makedirs("analysis_output", exist_ok=True)
        
        # Save extracted content
        analysis_data = {
            "document_id": doc_id,
            "filename": documents_store[doc_id]["filename"],
            "processed_at": datetime.now().isoformat(),
            "pages": pages_count,
            "content": {
                "full_text": full_text,
                "pages_data": text_data
            },
            "chunks": []
        }
        
        # Create chunks for RAG system
        chunk_size = 1000
        overlap = 200
        words = full_text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if chunk_text.strip():
                analysis_data["chunks"].append({
                    "chunk_id": f"{doc_id}_chunk_{len(analysis_data['chunks'])}",
                    "text": chunk_text,
                    "metadata": {
                        "document_id": doc_id,
                        "filename": documents_store[doc_id]["filename"],
                        "chunk_index": len(analysis_data["chunks"])
                    }
                })
        
        # Save analysis file
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        # Reinitialize RAG system with new document
        logger.info(f"🔄 Reinitializing RAG system with {len(analysis_data['chunks'])} chunks...")
        
        # Create new RAG instance with specific analysis file
        assert GROQ_API_KEY is not None, "GROQ_API_KEY should be available"
        rag_system = GroqOptimizedSimpleRAG(groq_api_key=GROQ_API_KEY, specific_analysis_file=analysis_file)
        
        # Update document status
        documents_store[doc_id]["status"] = "processed"
        documents_store[doc_id]["processed_at"] = datetime.now().isoformat()
        documents_store[doc_id]["message"] = f"Processing completed successfully. {len(analysis_data['chunks'])} chunks created and integrated into RAG system."
        documents_store[doc_id]["chunks_count"] = len(analysis_data["chunks"])
        
        logger.info(f"✅ PDF processing completed: {doc_id} - {len(analysis_data['chunks'])} chunks")
        
    except Exception as e:
        logger.error(f"❌ PDF processing failed for {doc_id}: {e}")
        documents_store[doc_id]["status"] = "failed"
        documents_store[doc_id]["error"] = str(e)
        documents_store[doc_id]["message"] = f"Processing failed: {str(e)}"

@app.post("/api/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Submit query to RAG system."""
    try:
        if rag_system is None:
            raise HTTPException(status_code=503, detail="RAG system not initialized")
            
        logger.info(f"🔍 Processing query: {request.question[:50]}...")
        
        start_time = datetime.now()
        
        # Query RAG system based on type
        if USE_MEMORY_OPTIMIZED:
            response_text = await asyncio.to_thread(
                rag_system.retrieve_and_generate,
                request.question
            )
            # Memory optimized returns string, convert to dict format
            response = {"answer": response_text, "confidence": 0.8, "context_length": len(response_text)}
        else:
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
