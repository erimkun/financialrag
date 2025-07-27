#!/usr/bin/env python3
"""
Frontend Connection Test Script
Tests frontend connectivity and error handling scenarios
"""

import requests
import time
import json

API_BASE_URL = "http://localhost:8000"

def test_frontend_api_connection():
    """Test all API endpoints that frontend uses"""
    
    print("🌐 TESTING FRONTEND API CONNECTIVITY")
    print("="*50)
    
    # Test health endpoint (for connection status)
    print("\n1. 🏥 Testing /api/health (Connection Status)")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Connection successful - Status: {data.get('status')}")
            print(f"   📊 RAG System: {data.get('rag_system')}")
        else:
            print(f"   ❌ Connection failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test documents endpoint
    print("\n2. 📄 Testing /api/documents (Document List)")
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents", timeout=10)
        if response.status_code == 200:
            docs = response.json()
            print(f"   ✅ Documents loaded - Count: {len(docs)}")
            print(f"   📋 First document: {docs[0]['filename'] if docs else 'None'}")
        else:
            print(f"   ❌ Failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test query endpoint
    print("\n3. 💬 Testing /api/query (Chat Functionality)")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json={"question": "Test frontend connection", "language": "tr"},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Query successful - Response time: {data.get('response_time', 0):.2f}s")
            print(f"   🎯 Confidence: {data.get('confidence', 0):.2%}")
        else:
            print(f"   ❌ Failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test stats endpoint
    print("\n4. 📊 Testing /api/stats (System Metrics)")
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Stats loaded - Documents: {stats.get('total_documents', 0)}")
            print(f"   📈 Queries: {stats.get('total_queries', 0)}")
        else:
            print(f"   ❌ Failed - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_error_scenarios():
    """Test error handling scenarios"""
    
    print("\n\n🚨 TESTING ERROR HANDLING SCENARIOS")
    print("="*50)
    
    # Test invalid endpoint
    print("\n1. 🔍 Testing Invalid Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/api/invalid-endpoint", timeout=5)
        print(f"   📊 Status: {response.status_code} (Expected: 404)")
        if response.status_code == 404:
            print("   ✅ Correct error handling")
        else:
            print("   ⚠️ Unexpected response")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test invalid query data
    print("\n2. 📝 Testing Invalid Query Data")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json={"invalid": "data"},
            timeout=10
        )
        print(f"   📊 Status: {response.status_code}")
        if response.status_code in [400, 422]:
            print("   ✅ Correct validation error")
        else:
            print("   ⚠️ Unexpected response")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test empty query
    print("\n3. ❓ Testing Empty Query")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json={"question": "", "language": "tr"},
            timeout=10
        )
        print(f"   📊 Status: {response.status_code}")
        if response.status_code in [400, 422]:
            print("   ✅ Correct validation for empty query")
        else:
            print("   ⚠️ Unexpected response")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_performance_scenarios():
    """Test performance under different conditions"""
    
    print("\n\n⚡ TESTING PERFORMANCE SCENARIOS")
    print("="*50)
    
    # Test multiple concurrent queries
    print("\n1. 🔄 Testing Response Time Consistency")
    queries = [
        "BIST-100 hakkında bilgi ver",
        "Ekonomik göstergeler nasıl?",
        "Banka sektörü performansı"
    ]
    
    response_times = []
    for i, query in enumerate(queries, 1):
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/api/query",
                json={"question": query, "language": "tr"},
                timeout=20
            )
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Query {i}: ✅ {response_time:.2f}s (Confidence: {data.get('confidence', 0):.2%})")
            else:
                print(f"   Query {i}: ❌ Failed ({response.status_code})")
                
        except Exception as e:
            print(f"   Query {i}: ❌ Error: {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"\n   📊 Average Response Time: {avg_time:.2f}s")
        if avg_time < 5.0:
            print("   ✅ Excellent performance")
        elif avg_time < 10.0:
            print("   👍 Good performance")
        else:
            print("   ⚠️ Performance could be improved")

def main():
    """Run all frontend tests"""
    print("🎯 FRONTEND CONNECTIVITY & ERROR HANDLING TESTS")
    print("="*60)
    
    test_frontend_api_connection()
    test_error_scenarios()
    test_performance_scenarios()
    
    print("\n" + "="*60)
    print("🎉 FRONTEND TESTING COMPLETE!")
    print("💡 Next: Test the actual frontend in browser")
    print("   - Open http://localhost:3000 (or your frontend port)")
    print("   - Test file upload functionality")
    print("   - Test chat with suggestion buttons")
    print("   - Test error scenarios (network issues)")
    print("   - Test on mobile devices")

if __name__ == "__main__":
    main()
