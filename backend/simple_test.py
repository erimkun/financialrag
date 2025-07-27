#!/usr/bin/env python3
import requests
import json

def test_api():
    try:
        print("🔍 Testing RAG API...")
        url = "http://localhost:8000/api/query"
        query = "BIST 100 endeksi hakkında bilgi ver"
        
        response = requests.post(url, json={"question": query})
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"📝 Query: {query}")
            print(f"🤖 Answer: {result['answer'][:500]}...")
            if len(result['answer']) > 500:
                print(f"[... {len(result['answer']) - 500} more characters]")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"🔥 Exception: {e}")

if __name__ == "__main__":
    test_api()
