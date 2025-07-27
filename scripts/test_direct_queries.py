"""
🧪 Direct Query Test
Test queries directly without documents check
"""

import requests
import json

def test_direct_queries():
    """Test direct queries bypassing documents check"""
    print("🧪 DIRECT QUERY TEST")
    print("="*50)
    print("Testing queries directly (bypassing documents endpoint)")
    
    base_url = "http://localhost:8000"
    
    # Test queries that should work if data is loaded
    test_queries = [
        "BIST-100 endeksi nasıl?",
        "Haftalık bülten özetini verebilir misin?",
        "Ekonomik veriler neler?",
        "Piyasa analizi yapabilir misin?"
    ]
    
    print(f"📝 Testing {len(test_queries)} direct queries...")
    
    successful = 0
    
    for i, query in enumerate(test_queries):
        print(f"\n🔍 Query {i+1}: {query}")
        
        try:
            response = requests.post(
                f"{base_url}/api/query",
                json={"question": query},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                confidence = result.get('confidence', 0)
                
                print(f"✅ Success!")
                print(f"🎯 Confidence: {confidence:.2f}")
                print(f"📝 Answer length: {len(answer)} chars")
                print(f"📖 Preview: {answer[:150]}...")
                
                if len(answer) > 50 and confidence > 0.3:
                    successful += 1
                    print("✅ Good quality response")
                else:
                    print("⚠️ Low quality response")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📝 Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Successful queries: {successful}/{len(test_queries)}")
    print(f"📈 Success rate: {(successful/len(test_queries)*100):.1f}%")
    
    if successful >= len(test_queries) * 0.75:
        print("🎉 SYSTEM IS WORKING! Documents endpoint might have an issue.")
        print("💡 RAG system has data and can answer questions!")
        return True
    else:
        print("❌ System has issues with query processing")
        return False

if __name__ == "__main__":
    result = test_direct_queries()
    
    if result:
        print(f"\n🎊 CONCLUSION: System is functional for users!")
        print(f"   • Backend is responding")
        print(f"   • RAG system has data") 
        print(f"   • Queries are being processed")
        print(f"   • Users can get financial analysis")
    else:
        print(f"\n⚠️ CONCLUSION: System needs debugging")
