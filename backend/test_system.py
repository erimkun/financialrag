#!/usr/bin/env python3
import requests
import json

def test_documents():
    try:
        print("🔍 Testing Documents API...")
        response = requests.get("http://localhost:8000/api/documents")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            docs = response.json()
            print(f"📄 Documents Count: {len(docs)}")
            for doc in docs:
                print(f"- {doc['filename']} ({doc['status']})")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"🔥 Exception: {e}")

def test_query():
    try:
        print("\n🔍 Testing Query API...")
        query_data = {
            "question": "Mamul mal stoku temmuzda artış mı gösterdi azaldı mı?"
        }
        response = requests.post("http://localhost:8000/api/query", json=query_data)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"🤖 Answer: {result['answer'][:200]}...")
            print(f"📈 Confidence: {result['confidence']}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"🔥 Exception: {e}")

if __name__ == "__main__":
    test_documents()
    test_query()
