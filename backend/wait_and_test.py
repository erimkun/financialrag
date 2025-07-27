#!/usr/bin/env python3
import requests
import time

def wait_and_test():
    print("⏳ Waiting 10 seconds for backend to start...")
    time.sleep(10)
    
    print("🔍 Testing system...")
    
    # Test health
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"💓 Health: {response.status_code}")
    except Exception as e:
        print(f"💔 Health failed: {e}")
        return
    
    # Test documents
    try:
        response = requests.get("http://localhost:8000/api/documents", timeout=5)
        if response.status_code == 200:
            docs = response.json()
            print(f"📄 Documents: {len(docs)} found")
            for doc in docs[:3]:
                print(f"  - {doc.get('filename', 'Unknown')}")
        else:
            print(f"📄 Documents error: {response.status_code}")
    except Exception as e:
        print(f"📄 Documents failed: {e}")
        return
    
    # Test query with document summary
    try:
        query_data = {"question": "Bu belgeyi özetler misin? Ana konular nelerdir?"}
        response = requests.post("http://localhost:8000/api/query", json=query_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            confidence = result.get('confidence', 0)
            print(f"🤖 Query success!")
            print(f"📝 Answer: {answer[:300]}...")
            print(f"📊 Confidence: {confidence}")
            
            # Check if response contains meaningful financial content
            answer_lower = answer.lower()
            financial_keywords = ['temmuz', 'güven', 'endeks', 'sektör', 'ekonomi', 'analiz', 'bulten', 'tcmb', 'kapasite', 'üretim', 'imalat']
            found_keywords = [kw for kw in financial_keywords if kw in answer_lower]
            
            if found_keywords:
                print(f"✅ SUCCESS: Response contains relevant financial content!")
                print(f"🎯 Found keywords: {', '.join(found_keywords)}")
            else:
                print(f"⚠️ WARNING: Response may not be specific to the document")
                
        else:
            print(f"❌ Query failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"🔥 Query failed: {e}")

if __name__ == "__main__":
    wait_and_test()
