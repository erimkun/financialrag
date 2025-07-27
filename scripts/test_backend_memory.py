"""
🧪 Backend Memory Test
Test memory optimized RAG in backend
"""

import requests
import json

def test_backend_with_memory_optimization():
    """Test backend API with regular and memory optimized versions"""
    print("🧪 Backend Memory Optimization Test")
    print("="*50)
    
    base_url = "http://localhost:8000"
    
    # Test queries
    test_queries = [
        "BIST-100 endeksi nasıl performans gösterdi?",
        "Mamul mal stoku ne durumda?",
        "VİOP kontratları hakkında ne var?",
        "Banka hisseleri nasıl performans gösterdi?"
    ]
    
    print(f"🔍 Testing backend at {base_url}")
    
    # Test documents endpoint
    try:
        response = requests.get(f"{base_url}/api/documents")
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ Documents API: {len(docs)} documents available")
        else:
            print(f"❌ Documents API failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test queries
    print(f"\n📝 Testing {len(test_queries)} queries...")
    
    for i, query in enumerate(test_queries):
        print(f"\n🔍 Query {i+1}: {query}")
        
        try:
            query_data = {"question": query}
            response = requests.post(f"{base_url}/api/query", json=query_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                confidence = result.get('confidence', 0)
                
                print(f"✅ Status: 200 OK")
                print(f"📊 Confidence: {confidence:.2f}")
                print(f"📝 Answer preview: {answer[:100]}...")
                
                if len(answer) < 50:
                    print("⚠️ Short answer - possible issue")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📝 Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timeout (30s)")
        except Exception as e:
            print(f"❌ Request error: {e}")
    
    print(f"\n💡 Recommendations:")
    print(f"   - If queries are slow/timing out: Switch to memory optimized version")
    print(f"   - If memory errors occur: Use lite mode")
    print(f"   - Current backend uses: Groq Direct RAG")

if __name__ == "__main__":
    test_backend_with_memory_optimization()
