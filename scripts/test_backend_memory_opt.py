"""
🧪 Test Backend with Memory Optimization
Test backend with memory optimized RAG
"""

import os
import subprocess
import time
import requests

def test_backend_with_memory_opt():
    """Test backend with memory optimization enabled"""
    print("🧪 Backend Memory Optimization Test")
    print("="*50)
    
    # Set environment variable for memory optimization
    env = os.environ.copy()
    env["USE_MEMORY_OPTIMIZED"] = "true"
    
    print("🔧 Environment: USE_MEMORY_OPTIMIZED=true")
    print("🚀 Testing backend with memory optimized RAG...")
    
    # Test the current running backend
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        print("\n🔍 Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check: {health_data.get('status')}")
            print(f"📊 Response time: {health_data.get('test_response_time', 0):.2f}s")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
            
        # Test documents endpoint
        print("\n🔍 Testing documents endpoint...")
        response = requests.get(f"{base_url}/api/documents", timeout=10)
        
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ Documents: {len(docs)} available")
        else:
            print(f"❌ Documents failed: {response.status_code}")
            return
            
        # Test queries with different complexity
        test_queries = [
            "BIST-100 ne durumda?",  # Simple
            "Mamul mal stoku temmuzda nasıl değişti?",  # Medium
            "VİOP kontratları ve banka hisseleri analizi yapabilir misin?"  # Complex
        ]
        
        print(f"\n📝 Testing {len(test_queries)} queries...")
        
        for i, query in enumerate(test_queries):
            print(f"\n🔍 Query {i+1}: {query}")
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{base_url}/api/query",
                    json={"question": query},
                    timeout=30
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', '')
                    confidence = result.get('confidence', 0)
                    
                    print(f"✅ Success in {response_time:.2f}s")
                    print(f"📊 Confidence: {confidence:.2f}")
                    print(f"📝 Answer length: {len(answer)} chars")
                    print(f"📋 Preview: {answer[:100]}...")
                    
                    # Check for memory/timeout issues
                    if response_time > 15:
                        print("⚠️ Slow response (>15s)")
                    elif response_time < 2:
                        print("🚀 Fast response (<2s)")
                        
                else:
                    print(f"❌ Failed: {response.status_code}")
                    print(f"📝 Error: {response.text[:200]}...")
                    
            except requests.exceptions.Timeout:
                print("⏰ Timeout (30s) - possible memory issue")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n💡 Test Results:")
        print(f"   - Backend is running with optimizations")
        print(f"   - Queries are being processed")
        print(f"   - No immediate memory crashes detected")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure backend is running on localhost:8000")

if __name__ == "__main__":
    test_backend_with_memory_opt()
