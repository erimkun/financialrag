"""
Fast Backend for Turkish Financial PDF RAG System
Simple backend that works with existing RAG system
"""

import os
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sys

# Load environment variables
load_dotenv()

# Add scripts directory to path
script_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, os.path.abspath(script_dir))

try:
    from groq_optimized_simple_rag import GroqOptimizedSimpleRAG
    print("✅ Successfully imported GroqOptimizedSimpleRAG")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"📁 Script directory: {os.path.abspath(script_dir)}")
    print(f"🔍 Available files: {os.listdir(script_dir) if os.path.exists(script_dir) else 'Directory not found'}")
    # Fallback - create minimal class
    class GroqOptimizedSimpleRAG:
        def __init__(self, groq_api_key: str):
            self.groq_api_key = groq_api_key
            print("⚠️ Using fallback RAG class")
        
        def query(self, question: str) -> dict:
            return {
                "answer": "System temporarily unavailable. Please check configuration.",
                "confidence": 0.0,
                "sources": []
            }

app = FastAPI(title="Turkish Financial PDF RAG API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
rag_system: Optional[GroqOptimizedSimpleRAG] = None

# Request models
class QueryRequest(BaseModel):
    question: str
    language: str = "tr"

# Performance monitoring
performance_stats = {
    "total_queries": 0,
    "total_query_time": 0.0,
    "avg_query_time": 0.0
}

def initialize_rag_system():
    """Initialize RAG system"""
    global rag_system
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            print("❌ GROQ_API_KEY not found")
            return False
            
        rag_system = GroqOptimizedSimpleRAG(groq_api_key=groq_api_key)
        print("✅ RAG system initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize systems on startup"""
    print("🚀 Starting Turkish Financial PDF RAG API...")
    success = initialize_rag_system()
    if not success:
        print("⚠️ Warning: RAG system failed to initialize")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "rag_system": "operational" if rag_system else "not initialized",
        "version": "1.0.0"
    }

@app.get("/api/documents")
async def get_documents():
    """Get list of processed documents"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Return available documents from the system
        documents = []
        
        # Check documents directory
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "documents")
        if os.path.exists(docs_dir):
            for file in os.listdir(docs_dir):
                if file.endswith('.pdf'):
                    documents.append({
                        "filename": file,
                        "status": "processed"
                    })
        
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@app.post("/api/query")
async def query_documents(request: QueryRequest):
    """Query documents using RAG system"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    start_time = time.time()
    
    try:
        # Process query
        result = rag_system.query(request.question)
        
        query_time = time.time() - start_time
        
        # Update performance stats
        performance_stats["total_queries"] += 1
        performance_stats["total_query_time"] += query_time
        performance_stats["avg_query_time"] = (
            performance_stats["total_query_time"] / performance_stats["total_queries"]
        )
        
        return {
            **result,
            "response_time": query_time
        }
        
    except Exception as e:
        query_time = time.time() - start_time
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file endpoint (simplified)"""
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file
        upload_path = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        
        with open(upload_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "status": "uploaded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    
    # Count documents
    total_docs = 0
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "documents")
    if os.path.exists(docs_dir):
        total_docs = len([f for f in os.listdir(docs_dir) if f.endswith('.pdf')])
    
    return {
        "total_documents": total_docs,
        "total_queries": performance_stats["total_queries"],
        "avg_query_time": round(performance_stats["avg_query_time"], 2) if performance_stats["total_queries"] > 0 else 0
    }

@app.post("/api/optimize")
async def optimize_system():
    """Manual system optimization"""
    try:
        import gc
        
        # Force garbage collection
        collected = gc.collect()
        
        # Clear performance stats if needed
        optimization_time = datetime.now()
        
        return {
            "message": "System optimization completed",
            "garbage_collected": collected,
            "optimization_time": optimization_time.isoformat(),
            "performance_stats": {
                "total_queries": performance_stats["total_queries"],
                "avg_query_time": performance_stats["avg_query_time"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
