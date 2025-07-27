#!/usr/bin/env python3
import requests

def test_documents():
    try:
        print("🔍 Testing Documents API...")
        r = requests.get('http://localhost:8000/api/documents')
        print(f"📊 Status: {r.status_code}")
        
        if r.status_code == 200:
            docs = r.json()
            print(f"📋 Documents Count: {len(docs)}")
            
            for doc in docs:
                print(f"  📄 {doc['filename']} ({doc['status']})")
                if 'pages' in doc:
                    print(f"      Pages: {doc['pages']}")
                if 'size' in doc:
                    print(f"      Size: {doc['size']} bytes")
        else:
            print(f"❌ Error: {r.text}")
            
    except Exception as e:
        print(f"🔥 Exception: {e}")

if __name__ == "__main__":
    test_documents()
