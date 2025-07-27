#!/usr/bin/env python3
import requests
import json

def reload_rag_system():
    try:
        print("🔄 Reloading RAG System...")
        response = requests.post("http://localhost:8000/api/reload")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"🔥 Exception: {e}")

def test_after_reload():
    print("\n" + "="*50)
    print("📊 Testing after reload...")
    
    # Test documents
    try:
        response = requests.get("http://localhost:8000/api/documents")
        if response.status_code == 200:
            docs = response.json()
            print(f"📄 Documents Count: {len(docs)}")
        else:
            print(f"❌ Documents Error: {response.text}")
    except Exception as e:
        print(f"🔥 Documents Exception: {e}")
    
    # Test query
    try:
        query_data = {
            "question": "Mamul mal stoku temmuzda artış mı gösterdi azaldı mı?"
        }
        response = requests.post("http://localhost:8000/api/query", json=query_data)
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 Answer: {result['answer'][:200]}...")
            print(f"📈 Confidence: {result['confidence']}")
        else:
            print(f"❌ Query Error: {response.text}")
    except Exception as e:
        print(f"🔥 Query Exception: {e}")

if __name__ == "__main__":
    reload_rag_system()
    test_after_reload()
