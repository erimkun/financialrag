"""
🎯 End-to-End User Test Suite
Complete user experience test from frontend to backend
"""

import requests
import time
import json

def test_complete_user_flow():
    """Test complete user flow like a real user"""
    
    print("🎯 KULLANICI GÖZÜYLE KAPSAMLI TEST")
    print("="*60)
    print("Bu test gerçek bir kullanıcının tüm sistemi kullanmasını simüle eder")
    print()
    
    base_url = "http://localhost:8000"
    frontend_url = "http://localhost:5173"
    
    # 1. System Health Check
    print("1️⃣ SİSTEM SAĞLIK KONTROLÜ")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Backend Status: {health.get('status')}")
            print(f"📊 RAG System: {health.get('rag_system')}")
            print(f"⚡ Response Time: {health.get('test_response_time', 0):.2f}s")
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        print("💡 Backend'in çalıştığından emin olun: python main.py")
        return False
    
    # 2. Frontend Connection Test
    print(f"\n2️⃣ FRONTEND BAĞLANTI TESTİ")
    print("-" * 30)
    
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend accessible at {frontend_url}")
        else:
            print(f"⚠️ Frontend status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Frontend connection issue: {e}")
        print("💡 Frontend'in çalıştığından emin olun: npm run dev")
    
    # 3. Documents Check
    print(f"\n3️⃣ DOKÜMAN YÖNETİMİ TESTİ")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/documents", timeout=10)
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ {len(docs)} dokümana erişilebiliyor")
            
            for doc in docs:
                print(f"   📄 {doc.get('filename', 'Unknown')} - {doc.get('status', 'Unknown')}")
                
            if len(docs) == 0:
                print("⚠️ Hiç doküman yüklenmemiş")
                print("💡 PDF yüklemek için frontend'i kullanın")
        else:
            print(f"❌ Documents API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Documents check failed: {e}")
        return False
    
    # 4. Real User Queries Test
    print(f"\n4️⃣ GERÇEK KULLANICI SORGULARI TESTİ")
    print("-" * 30)
    
    user_questions = [
        {
            "question": "BIST-100 endeksi bugün nasıl performans gösterdi?",
            "category": "Borsa/Endeks",
            "expected_keywords": ["BIST", "endeks", "performans"]
        },
        {
            "question": "Dolar kuru ne durumda, artış var mı?",
            "category": "Döviz",
            "expected_keywords": ["dolar", "kur", "USD", "TL"]
        },
        {
            "question": "Mamul mal stoku temmuzda ne kadar değişti?",
            "category": "Ekonomik Gösterge",
            "expected_keywords": ["mamul mal", "stok", "temmuz"]
        },
        {
            "question": "Banka hisseleri hangi yönde hareket etti?",
            "category": "Sektör Analizi",
            "expected_keywords": ["banka", "hisse", "hareket"]
        },
        {
            "question": "VİOP kontratlarında ne gibi gelişmeler var?",
            "category": "Vadeli İşlemler",
            "expected_keywords": ["VİOP", "kontrat", "vadeli"]
        }
    ]
    
    successful_queries = 0
    total_time = 0
    
    for i, query_info in enumerate(user_questions):
        question = query_info["question"]
        category = query_info["category"]
        expected_keywords = query_info["expected_keywords"]
        
        print(f"\n🔍 Soru {i+1} ({category}): {question}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/api/query",
                json={"question": question},
                timeout=30
            )
            query_time = time.time() - start_time
            total_time += query_time
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                confidence = result.get('confidence', 0)
                
                print(f"   ✅ Yanıt alındı ({query_time:.2f}s)")
                print(f"   📊 Güven skoru: {confidence:.2f}")
                print(f"   📝 Yanıt uzunluğu: {len(answer)} karakter")
                
                # Check answer quality
                answer_lower = answer.lower()
                found_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
                
                if found_keywords:
                    print(f"   🎯 Relevant keywords found: {', '.join(found_keywords)}")
                else:
                    print(f"   ⚠️ Expected keywords not found: {', '.join(expected_keywords)}")
                
                # Show answer preview
                preview = answer[:150] + "..." if len(answer) > 150 else answer
                print(f"   💬 Yanıt önizleme: {preview}")
                
                # Quality checks
                if len(answer) < 50:
                    print(f"   ⚠️ Çok kısa yanıt")
                elif confidence < 0.3:
                    print(f"   ⚠️ Düşük güven skoru")
                elif query_time > 10:
                    print(f"   ⚠️ Yavaş yanıt (>10s)")
                else:
                    successful_queries += 1
                    print(f"   🎉 Kaliteli yanıt!")
                    
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   📝 Error: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout (30s)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # 5. Performance Summary
    print(f"\n5️⃣ PERFORMANS ÖZETİ")
    print("-" * 30)
    
    success_rate = (successful_queries / len(user_questions)) * 100
    avg_time = total_time / len(user_questions) if len(user_questions) > 0 else 0
    
    print(f"📊 Başarı oranı: {success_rate:.1f}% ({successful_queries}/{len(user_questions)})")
    print(f"⚡ Ortalama yanıt süresi: {avg_time:.2f}s")
    print(f"⏱️ Toplam test süresi: {total_time:.2f}s")
    
    # 6. User Experience Rating
    print(f"\n6️⃣ KULLANICI DENEYİMİ DEĞERLENDİRMESİ")
    print("-" * 30)
    
    if success_rate >= 80 and avg_time <= 5:
        grade = "🌟 MÜKEMMELLETTİRİLMEL"
        print(f"{grade} - Sistem kullanıcılar için hazır!")
    elif success_rate >= 60 and avg_time <= 10:
        grade = "✅ İYİ"
        print(f"{grade} - Sistem kullanılabilir, küçük iyileştirmeler yapılabilir")
    elif success_rate >= 40:
        grade = "⚠️ ORTA"
        print(f"{grade} - Sistem çalışıyor ama iyileştirmeler gerekli")
    else:
        grade = "❌ YETERSIZ"
        print(f"{grade} - Önemli sorunlar var, düzeltmeler gerekli")
    
    # 7. Recommendations
    print(f"\n7️⃣ KULLANICI ÖNERİLERİ")
    print("-" * 30)
    
    if avg_time > 5:
        print("📈 Performance: Memory optimized RAG kullanımını artırın")
    
    if success_rate < 70:
        print("🎯 Accuracy: Daha fazla doküman yükleyin veya prompt'ları iyileştirin")
    
    if successful_queries < 3:
        print("🔧 System: Backend'i yeniden başlatmayı deneyin")
    
    print(f"\n💡 GENEL DEĞERLENDİRME:")
    print(f"   - Backend: {'✅ Çalışıyor' if success_rate > 0 else '❌ Sorunlu'}")
    print(f"   - RAG System: {'✅ Aktif' if successful_queries > 0 else '❌ Sorunlu'}")
    print(f"   - Response Quality: {grade}")
    print(f"   - Production Ready: {'✅ Evet' if success_rate >= 70 and avg_time <= 10 else '❌ Hayır'}")
    
    return success_rate >= 70

if __name__ == "__main__":
    success = test_complete_user_flow()
    print(f"\n🎯 FINAL RESULT: {'✅ SYSTEM READY' if success else '❌ NEEDS WORK'}")
