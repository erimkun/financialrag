"""
🎯 Complete User Experience Test
End-to-end test simulating real user scenarios
"""

import requests
import json
import time

def test_complete_user_experience():
    """Complete end-to-end user test"""
    print("🎯 COMPLETE USER EXPERIENCE TEST")
    print("="*60)
    print("Testing as if you are a real user of the financial RAG system")
    
    base_url = "http://localhost:8000"
    
    # 1. System Health Check
    print("\n🏥 1. SYSTEM HEALTH CHECK")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ System Status: {health.get('status', 'unknown').upper()}")
            print(f"📊 Response Time: {health.get('test_response_time', 0):.2f}s")
            print(f"🔧 Version: {health.get('version', 'unknown')}")
        else:
            print(f"❌ System unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # 2. Available Documents Check
    print("\n📚 2. AVAILABLE DOCUMENTS")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/documents", timeout=10)
        if response.status_code == 200:
            docs = response.json()
            print(f"📄 Documents Available: {len(docs)}")
            for doc in docs:
                print(f"   • {doc.get('filename', 'Unknown')} ({doc.get('status', 'unknown')})")
            
            if len(docs) == 0:
                print("⚠️ No documents found! Upload a PDF first.")
                return False
        else:
            print(f"❌ Cannot access documents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing documents: {e}")
        return False
    
    # 3. Real User Query Scenarios
    print("\n🧠 3. REAL USER QUERIES")
    print("-" * 30)
    
    # Real-world financial questions a user might ask
    user_scenarios = [
        {
            "scenario": "Market Overview",
            "query": "BIST-100 endeksi bugün nasıl performans gösterdi?",
            "expected_keywords": ["BIST-100", "endeks", "performans"]
        },
        {
            "scenario": "Economic Indicators", 
            "query": "Enflasyon rakamları nasıl? Son veriler neler?",
            "expected_keywords": ["enflasyon", "veri", "rakam"]
        },
        {
            "scenario": "Stock Analysis",
            "query": "Banka hisseleri nasıl gidiyor? Yatırım tavsiyesi var mı?",
            "expected_keywords": ["banka", "hisse", "yatırım"]
        },
        {
            "scenario": "Sectoral Information",
            "query": "Mamul mal stoku temmuzda ne durumda?",
            "expected_keywords": ["mamul", "mal", "stok"]
        },
        {
            "scenario": "Derivatives Market",
            "query": "VİOP kontratları hakkında ne bilgiler var?",
            "expected_keywords": ["VİOP", "kontrat", "vadeli"]
        }
    ]
    
    successful_queries = 0
    total_response_time = 0
    
    for i, scenario in enumerate(user_scenarios):
        print(f"\n📋 Scenario {i+1}: {scenario['scenario']}")
        print(f"❓ User Question: {scenario['query']}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/api/query",
                json={"question": scenario['query']},
                timeout=30
            )
            response_time = time.time() - start_time
            total_response_time += response_time
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                confidence = result.get('confidence', 0)
                
                print(f"✅ Response in {response_time:.2f}s")
                print(f"🎯 Confidence: {confidence:.1%}")
                
                # Check answer quality
                answer_lower = answer.lower()
                keywords_found = sum(1 for keyword in scenario['expected_keywords'] 
                                   if keyword.lower() in answer_lower)
                
                print(f"📝 Answer length: {len(answer)} characters")
                print(f"🔍 Relevant keywords found: {keywords_found}/{len(scenario['expected_keywords'])}")
                
                # Show answer preview
                if len(answer) > 200:
                    print(f"📖 Answer preview: {answer[:200]}...")
                else:
                    print(f"📖 Full answer: {answer}")
                
                # Quality assessment
                if confidence > 0.5 and keywords_found > 0 and len(answer) > 50:
                    print("✅ Good quality answer")
                    successful_queries += 1
                elif confidence > 0.3 and len(answer) > 30:
                    print("⚠️ Acceptable answer")
                    successful_queries += 0.5
                else:
                    print("❌ Poor quality answer")
                    
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"📝 Error: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ Query timeout (30s) - system may be overloaded")
        except Exception as e:
            print(f"❌ Query error: {e}")
    
    # 4. Performance Summary
    print(f"\n📊 4. PERFORMANCE SUMMARY")
    print("-" * 30)
    
    success_rate = (successful_queries / len(user_scenarios)) * 100
    avg_response_time = total_response_time / len(user_scenarios) if len(user_scenarios) > 0 else 0
    
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"⚡ Average Response Time: {avg_response_time:.2f}s")
    print(f"🎯 Total Scenarios Tested: {len(user_scenarios)}")
    print(f"✅ Successful Queries: {successful_queries:.1f}")
    
    # 5. User Experience Assessment
    print(f"\n🎭 5. USER EXPERIENCE ASSESSMENT")
    print("-" * 30)
    
    if success_rate >= 80:
        print("🌟 EXCELLENT - System ready for production use")
        print("   Users will have a great experience")
    elif success_rate >= 60:
        print("✅ GOOD - System functional with minor issues")
        print("   Most users will be satisfied")
    elif success_rate >= 40:
        print("⚠️ FAIR - System works but needs improvement")
        print("   Some users may be frustrated")
    else:
        print("❌ POOR - System needs significant work")
        print("   Users will likely be disappointed")
    
    if avg_response_time <= 2:
        print("🚀 Response time: EXCELLENT (≤2s)")
    elif avg_response_time <= 5:
        print("✅ Response time: GOOD (≤5s)")
    elif avg_response_time <= 10:
        print("⚠️ Response time: ACCEPTABLE (≤10s)")
    else:
        print("❌ Response time: TOO SLOW (>10s)")
    
    # 6. Final Recommendations
    print(f"\n💡 6. RECOMMENDATIONS FOR USER")
    print("-" * 30)
    
    if success_rate >= 70 and avg_response_time <= 5:
        print("🎉 READY TO USE!")
        print("   • System is production-ready")
        print("   • Users can start using it immediately")
        print("   • Financial analysis queries work well")
    else:
        print("🔧 NEEDS TUNING:")
        if success_rate < 70:
            print("   • Improve answer quality and relevance")
            print("   • Add more training data")
        if avg_response_time > 5:
            print("   • Optimize response times")
            print("   • Consider memory optimization")
    
    return success_rate >= 60 and avg_response_time <= 10

if __name__ == "__main__":
    result = test_complete_user_experience()
    if result:
        print(f"\n🎊 OVERALL RESULT: SYSTEM READY FOR USER TESTING!")
    else:
        print(f"\n⚠️ OVERALL RESULT: SYSTEM NEEDS MORE WORK")
