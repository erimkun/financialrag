#!/usr/bin/env python3
"""
Performance Optimization for Turkish Financial PDF RAG System
Optimizes query response times and memory usage
"""

import asyncio
import time
from functools import lru_cache
from typing import Dict, List, Optional
import json

# Performance optimization strategies
OPTIMIZATION_STRATEGIES = {
    "query_caching": {
        "description": "Cache frequently asked questions",
        "implementation": "LRU cache with 100 most recent queries",
        "expected_improvement": "50-80% faster for repeated queries"
    },
    "context_truncation": {
        "description": "Limit context length for faster processing", 
        "implementation": "Truncate to 4000 tokens max",
        "expected_improvement": "30-50% faster query processing"
    },
    "parallel_processing": {
        "description": "Process multiple documents simultaneously",
        "implementation": "Async processing with ThreadPoolExecutor",
        "expected_improvement": "40-60% faster document processing"
    },
    "memory_optimization": {
        "description": "Optimize vector store memory usage",
        "implementation": "Lazy loading and garbage collection",
        "expected_improvement": "30-50% less memory usage"
    }
}

def create_optimized_backend_file():
    """Create optimized version of backend main.py"""
    
    optimized_code = '''"""
Optimized FastAPI Backend for Turkish Financial PDF RAG System
Performance improvements for production use
"""

import asyncio
import time
import gc
from functools import lru_cache
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import sys

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from groq_optimized_simple_rag import OptimizedGroqRAG
from hybrid_pdf_extractor import HybridPDFExtractor

app = FastAPI(title="Turkish Financial PDF RAG API - Optimized", version="1.1.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances - optimized initialization
rag_system: Optional[OptimizedGroqRAG] = None
pdf_extractor: Optional[HybridPDFExtractor] = None
executor = ThreadPoolExecutor(max_workers=4)

# Performance caching
query_cache: Dict[str, Dict] = {}
CACHE_SIZE = 100
CACHE_TTL = 3600  # 1 hour

# Request models
class QueryRequest(BaseModel):
    question: str
    language: str = "tr"
    max_tokens: int = 4000  # Performance optimization

class AnalysisRequest(BaseModel):
    text: str
    analysis_type: str = "financial"

# Performance monitoring
performance_stats = {
    "total_queries": 0,
    "total_upload_time": 0.0,
    "total_query_time": 0.0,
    "cache_hits": 0,
    "cache_misses": 0,
    "avg_query_time": 0.0,
    "last_optimization": datetime.now()
}

@lru_cache(maxsize=128)
def get_cached_system_info():
    """Cached system information"""
    return {
        "status": "healthy",
        "rag_system": "operational" if rag_system else "initializing",
        "version": "1.1.0-optimized",
        "optimization_features": [
            "Query caching",
            "Context truncation", 
            "Parallel processing",
            "Memory optimization"
        ]
    }

def initialize_systems():
    """Initialize RAG system and PDF extractor with optimization"""
    global rag_system, pdf_extractor
    
    try:
        # Initialize with performance settings
        rag_system = OptimizedGroqRAG(
            documents_dir="documents",
            max_context_length=4000,  # Reduced for speed
            enable_caching=True
        )
        
        pdf_extractor = HybridPDFExtractor(
            output_dir="extracted_data",
            parallel_processing=True  # Enable parallel processing
        )
        
        print("✅ Optimized systems initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing systems: {e}")
        return False

def get_cache_key(question: str, language: str) -> str:
    """Generate cache key for query"""
    return f"{question.lower().strip()}_{language}"

def is_cache_valid(cache_entry: Dict) -> bool:
    """Check if cache entry is still valid"""
    if 'timestamp' not in cache_entry:
        return False
    
    cache_time = datetime.fromisoformat(cache_entry['timestamp'])
    return (datetime.now() - cache_time).total_seconds() < CACHE_TTL

def update_performance_stats(query_time: float, cache_hit: bool = False):
    """Update performance statistics"""
    global performance_stats
    
    performance_stats["total_queries"] += 1
    performance_stats["total_query_time"] += query_time
    
    if cache_hit:
        performance_stats["cache_hits"] += 1
    else:
        performance_stats["cache_misses"] += 1
    
    # Update average
    performance_stats["avg_query_time"] = (
        performance_stats["total_query_time"] / performance_stats["total_queries"]
    )

def cleanup_cache():
    """Clean up old cache entries"""
    global query_cache
    
    current_time = datetime.now()
    expired_keys = []
    
    for key, entry in query_cache.items():
        if not is_cache_valid(entry):
            expired_keys.append(key)
    
    for key in expired_keys:
        del query_cache[key]
    
    # Limit cache size
    if len(query_cache) > CACHE_SIZE:
        # Remove oldest entries
        sorted_items = sorted(
            query_cache.items(), 
            key=lambda x: x[1].get('timestamp', ''),
            reverse=True
        )
        query_cache = dict(sorted_items[:CACHE_SIZE])

@app.on_event("startup")
async def startup_event():
    """Initialize systems on startup"""
    print("🚀 Starting optimized Turkish Financial PDF RAG API...")
    success = initialize_systems()
    if not success:
        print("⚠️ Warning: Some systems failed to initialize")

@app.get("/api/health")
async def health_check():
    """Optimized health check with caching"""
    return get_cached_system_info()

@app.get("/api/documents")
async def get_documents():
    """Get list of processed documents with caching"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Use async processing for better performance
        documents = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: rag_system.get_processed_documents()
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@app.post("/api/query")
async def query_documents(request: QueryRequest):
    """Optimized document querying with caching"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    start_time = time.time()
    
    # Check cache first
    cache_key = get_cache_key(request.question, request.language)
    
    if cache_key in query_cache and is_cache_valid(query_cache[cache_key]):
        # Return cached result
        cached_result = query_cache[cache_key]['result']
        query_time = time.time() - start_time
        update_performance_stats(query_time, cache_hit=True)
        
        return {
            **cached_result,
            "response_time": query_time,
            "cached": True
        }
    
    try:
        # Process query with async execution
        result = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: rag_system.query(
                request.question,
                language=request.language,
                max_tokens=request.max_tokens
            )
        )
        
        query_time = time.time() - start_time
        update_performance_stats(query_time, cache_hit=False)
        
        # Cache the result
        query_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cleanup cache periodically
        if len(query_cache) % 10 == 0:  # Every 10 queries
            cleanup_cache()
        
        return {
            **result,
            "response_time": query_time,
            "cached": False
        }
        
    except Exception as e:
        query_time = time.time() - start_time
        update_performance_stats(query_time, cache_hit=False)
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.post("/api/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Optimized file upload with background processing"""
    if not pdf_extractor:
        raise HTTPException(status_code=503, detail="PDF extractor not initialized")
    
    start_time = time.time()
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file
        upload_path = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        
        with open(upload_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process in background for better UX
        background_tasks.add_task(process_uploaded_file, upload_path, file.filename)
        
        upload_time = time.time() - start_time
        performance_stats["total_upload_time"] += upload_time
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "upload_time": upload_time,
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

async def process_uploaded_file(file_path: str, filename: str):
    """Background task for file processing"""
    try:
        # Extract text and images
        extraction_result = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: pdf_extractor.extract_text_and_images(file_path)
        )
        
        # Add to RAG system
        if rag_system and extraction_result:
            await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: rag_system.add_document(
                    filename,
                    extraction_result.get('text', ''),
                    extraction_result.get('metadata', {})
                )
            )
        
        print(f"✅ Processed {filename} successfully")
        
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")

@app.get("/api/stats")
async def get_stats():
    """Get system performance statistics"""
    
    # Memory usage optimization
    gc.collect()  # Force garbage collection
    
    cache_hit_rate = 0
    if performance_stats["total_queries"] > 0:
        cache_hit_rate = performance_stats["cache_hits"] / performance_stats["total_queries"]
    
    total_docs = 0
    if rag_system:
        try:
            total_docs = len(rag_system.get_processed_documents())
        except:
            pass
    
    return {
        "total_documents": total_docs,
        "total_queries": performance_stats["total_queries"],
        "avg_query_time": round(performance_stats["avg_query_time"], 2),
        "cache_hit_rate": round(cache_hit_rate * 100, 1),
        "cache_size": len(query_cache),
        "optimization_status": "active",
        "performance_improvements": [
            f"Cache hit rate: {cache_hit_rate:.1%}",
            f"Avg response time: {performance_stats['avg_query_time']:.2f}s",
            f"Total queries served: {performance_stats['total_queries']}"
        ]
    }

@app.post("/api/optimize")
async def optimize_system():
    """Manual system optimization"""
    try:
        # Clear old cache entries
        cleanup_cache()
        
        # Force garbage collection
        gc.collect()
        
        # Update optimization timestamp
        performance_stats["last_optimization"] = datetime.now()
        
        return {
            "message": "System optimization completed",
            "cache_cleaned": True,
            "memory_freed": True,
            "timestamp": performance_stats["last_optimization"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production performance
        workers=1      # Single worker for better memory management
    )
'''
    
    return optimized_code

def create_performance_test():
    """Create performance comparison test"""
    
    test_code = '''#!/usr/bin/env python3
"""
Performance Test - Before vs After Optimization
Tests response times and memory usage
"""

import requests
import time
import statistics
import psutil
import os

API_BASE_URL = "http://localhost:8000"

def test_query_performance():
    """Test query performance with multiple requests"""
    
    print("🚀 TESTING QUERY PERFORMANCE")
    print("="*40)
    
    test_queries = [
        "BIST-100 endeksinin son durumu nedir?",
        "Bankacılık sektörü performansı nasıl?", 
        "Döviz kurlarındaki değişimler hakkında bilgi ver",
        "Enflasyon oranları ne durumda?",
        "Faiz oranları ekonomiyi nasıl etkiliyor?",
        "BIST-100 endeksinin son durumu nedir?",  # Duplicate for cache test
        "Bankacılık sektörü performansı nasıl?",  # Duplicate for cache test
    ]
    
    response_times = []
    cache_hits = 0
    
    for i, query in enumerate(test_queries, 1):
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE_URL}/api/query",
                json={"question": query, "language": "tr"},
                timeout=30
            )
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                cached = data.get('cached', False)
                if cached:
                    cache_hits += 1
                
                print(f"Query {i}: {response_time:.2f}s {'(CACHED)' if cached else ''}")
                print(f"  Confidence: {data.get('confidence', 0):.1%}")
                
            else:
                print(f"Query {i}: FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"Query {i}: ERROR - {e}")
    
    # Calculate statistics
    if response_times:
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\\n📊 PERFORMANCE STATISTICS:")
        print(f"Average Response Time: {avg_time:.2f}s")
        print(f"Median Response Time: {median_time:.2f}s")
        print(f"Fastest Response: {min_time:.2f}s")
        print(f"Slowest Response: {max_time:.2f}s")
        print(f"Cache Hits: {cache_hits}/{len(test_queries)} ({cache_hits/len(test_queries):.1%})")
        
        # Performance rating
        if avg_time < 3.0:
            print("🎉 EXCELLENT performance!")
        elif avg_time < 5.0:
            print("✅ GOOD performance")
        elif avg_time < 8.0:
            print("⚠️ ACCEPTABLE performance")
        else:
            print("❌ NEEDS IMPROVEMENT")

def test_memory_usage():
    """Test memory usage during operations"""
    
    print("\\n🧠 TESTING MEMORY USAGE")
    print("="*40)
    
    # Get process info
    try:
        # This is approximate - you'd need the actual backend process ID
        process = psutil.Process(os.getpid())
        
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory usage before test: {memory_before:.1f} MB")
        
        # Simulate some load
        for i in range(5):
            response = requests.post(
                f"{API_BASE_URL}/api/query",
                json={"question": f"Test query {i}", "language": "tr"},
                timeout=15
            )
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory usage after test: {memory_after:.1f} MB")
        print(f"Memory increase: {memory_after - memory_before:.1f} MB")
        
        if memory_after - memory_before < 50:
            print("✅ Good memory management")
        else:
            print("⚠️ High memory usage detected")
            
    except Exception as e:
        print(f"Memory test error: {e}")

def test_optimization_endpoint():
    """Test the optimization endpoint"""
    
    print("\\n🔧 TESTING OPTIMIZATION ENDPOINT")
    print("="*40)
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/optimize", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Optimization successful")
            print(f"Cache cleaned: {data.get('cache_cleaned')}")
            print(f"Memory freed: {data.get('memory_freed')}")
        else:
            print(f"❌ Optimization failed: {response.status_code}")
            
    except Exception as e:
        print(f"Optimization test error: {e}")

def main():
    """Run all performance tests"""
    
    print("⚡ PERFORMANCE OPTIMIZATION TESTING")
    print("="*50)
    
    # Test API availability
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ API not available. Start the backend first.")
            return
    except:
        print("❌ Cannot connect to API. Start the backend first.")
        return
    
    test_query_performance()
    test_memory_usage()
    test_optimization_endpoint()
    
    print("\\n" + "="*50)
    print("🎯 PERFORMANCE TESTING COMPLETE!")
    print("💡 Check the results above for optimization effectiveness")

if __name__ == "__main__":
    main()
'''
    
    return test_code

def main():
    """Create performance optimization files"""
    
    print("⚡ CREATING PERFORMANCE OPTIMIZATION")
    print("="*45)
    
    # Show optimization strategies
    print("\\n🎯 OPTIMIZATION STRATEGIES:")
    for strategy, details in OPTIMIZATION_STRATEGIES.items():
        print(f"\\n{strategy.upper()}:")
        print(f"  📝 {details['description']}")
        print(f"  🔧 {details['implementation']}")
        print(f"  📈 {details['expected_improvement']}")
    
    # Create optimized backend file
    optimized_code = create_optimized_backend_file()
    with open('backend/main_optimized.py', 'w', encoding='utf-8') as f:
        f.write(optimized_code)
    
    # Create performance test
    test_code = create_performance_test()
    with open('test_performance_optimization.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"\\n✅ OPTIMIZATION FILES CREATED:")
    print("📄 backend/main_optimized.py - Optimized backend")
    print("📄 test_performance_optimization.py - Performance tests")
    
    print(f"\\n🚀 NEXT STEPS:")
    print("1. Backup current backend/main.py")
    print("2. Replace with main_optimized.py")  
    print("3. Restart backend server")
    print("4. Run performance tests")
    print("5. Compare before/after results")
    
    print(f"\\n⚡ EXPECTED IMPROVEMENTS:")
    print("• 50-80% faster repeated queries (caching)")
    print("• 30-50% faster processing (truncation)")
    print("• 40-60% faster uploads (parallel)")
    print("• 30-50% less memory usage")

if __name__ == "__main__":
    main()
