#!/usr/bin/env python3
"""
End-to-End System Test Script
Tests the complete functionality of the Turkish Financial PDF RAG System
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_DOCUMENT_PATH = "documents/20250716_Gunluk_Bulten.pdf"
TEST_QUERIES = [
    "BIST-100 için teknik yorum nedir?",
    "Hangi hisse senetleri en yüksek getiri sağladı?",
    "Banka hisseleri nasıl performans gösterdi?",
    "VİOP kontratları hakkında ne söyleniyor?",
    "Ekonomik göstergeler nasıl?"
]

def test_health_check():
    """Test API health endpoint"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check Passed - Status: {data.get('status')}")
            print(f"📊 RAG System: {data.get('rag_system', 'unknown')}")
            print(f"⏱️ Test Response Time: {data.get('test_response_time', 0):.2f}s")
            return True
        else:
            print(f"❌ Health Check Failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_documents_api():
    """Test documents listing API"""
    print("\n📄 Testing Documents API...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents")
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Documents API Success - Found {len(documents)} documents")
            for doc in documents[:3]:  # Show first 3
                print(f"  📋 {doc['filename']} ({doc['status']})")
            return True, documents
        else:
            print(f"❌ Documents API Failed - Status: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Documents API Error: {e}")
        return False, []

def test_query_api():
    """Test query API with multiple questions"""
    print("\n🔍 Testing Query API...")
    results = []
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n  {i}. Testing: '{query[:50]}...'")
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/api/query",
                json={
                    "question": query,
                    "language": "tr"
                },
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"     ✅ Response in {response_time:.2f}s")
                print(f"     🎯 Confidence: {data.get('confidence', 0):.2%}")
                print(f"     📝 Answer length: {len(data.get('answer', ''))}")
                
                results.append({
                    "query": query,
                    "success": True,
                    "response_time": response_time,
                    "confidence": data.get('confidence', 0),
                    "answer_length": len(data.get('answer', ''))
                })
            else:
                print(f"     ❌ Failed - Status: {response.status_code}")
                results.append({
                    "query": query,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    return results

def test_upload_api():
    """Test file upload API"""
    print("\n📤 Testing Upload API...")
    
    # Check if test document exists
    if not os.path.exists(TEST_DOCUMENT_PATH):
        print(f"⚠️ Test document not found: {TEST_DOCUMENT_PATH}")
        print("   Using documents from existing analysis...")
        return True
    
    try:
        with open(TEST_DOCUMENT_PATH, 'rb') as file:
            files = {'file': file}
            print(f"  📁 Uploading: {TEST_DOCUMENT_PATH}")
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/api/upload-pdf",
                files=files,
                timeout=120  # 2 minutes for upload
            )
            upload_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Upload successful in {upload_time:.2f}s")
                print(f"  📋 Document ID: {data.get('document_id', 'unknown')}")
                print(f"  📊 Status: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"  ❌ Upload failed - Status: {response.status_code}")
                if response.text:
                    print(f"     Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"  ❌ Upload error: {e}")
        return False

def test_system_stats():
    """Test system statistics API"""
    print("\n📊 Testing System Stats...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats API Success")
            print(f"  📄 Total Documents: {stats.get('total_documents', 0)}")
            print(f"  💬 Total Queries: {stats.get('total_queries', 0)}")
            print(f"  ⏱️ Avg Response Time: {stats.get('avg_response_time', 0):.3f}s")
            print(f"  🎯 Avg Confidence: {stats.get('avg_confidence', 0):.3f}")
            print(f"  🟢 System Status: {stats.get('system_status', 'unknown')}")
            return True
        else:
            print(f"❌ Stats API Failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats API Error: {e}")
        return False

def generate_test_report(test_results):
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("🎯 END-TO-END TEST REPORT")
    print("="*60)
    
    # Query results analysis
    successful_queries = [r for r in test_results['queries'] if r['success']]
    failed_queries = [r for r in test_results['queries'] if not r['success']]
    
    print(f"\n📊 QUERY PERFORMANCE:")
    print(f"  ✅ Successful: {len(successful_queries)}/{len(test_results['queries'])}")
    print(f"  ❌ Failed: {len(failed_queries)}")
    
    if successful_queries:
        avg_response_time = sum(r['response_time'] for r in successful_queries) / len(successful_queries)
        avg_confidence = sum(r['confidence'] for r in successful_queries) / len(successful_queries)
        print(f"  ⏱️ Avg Response Time: {avg_response_time:.2f}s")
        print(f"  🎯 Avg Confidence: {avg_confidence:.2%}")
    
    print(f"\n🔧 SYSTEM HEALTH:")
    print(f"  🏥 Health Check: {'✅ PASS' if test_results['health'] else '❌ FAIL'}")
    print(f"  📄 Documents API: {'✅ PASS' if test_results['documents'] else '❌ FAIL'}")
    print(f"  📤 Upload API: {'✅ PASS' if test_results['upload'] else '❌ FAIL'}")
    print(f"  📊 Stats API: {'✅ PASS' if test_results['stats'] else '❌ FAIL'}")
    
    # Overall assessment
    total_tests = 4 + len(test_results['queries'])
    passed_tests = sum([
        test_results['health'],
        test_results['documents'], 
        test_results['upload'],
        test_results['stats'],
        len(successful_queries)
    ])
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n🎖️ OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! System is production-ready!")
    elif success_rate >= 75:
        print("👍 GOOD! Minor issues to address.")
    else:
        print("⚠️ NEEDS ATTENTION! Several issues found.")
    
    return success_rate

def main():
    """Run complete end-to-end test suite"""
    print("🚀 STARTING END-TO-END SYSTEM TESTS")
    print("="*60)
    
    test_results = {
        'health': False,
        'documents': False,
        'upload': False,
        'stats': False,
        'queries': []
    }
    
    # Run all tests
    test_results['health'] = test_health_check()
    test_results['documents'], documents = test_documents_api()
    test_results['upload'] = test_upload_api()
    test_results['stats'] = test_system_stats()
    test_results['queries'] = test_query_api()
    
    # Generate final report
    success_rate = generate_test_report(test_results)
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = f"test_results_e2e_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'success_rate': success_rate,
            'results': test_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Test results saved to: {report_file}")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
