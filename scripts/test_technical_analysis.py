"""
🧪 Extended Test - Technical Analysis & Stock Analysis
Test the system with technical analysis and stock market questions
"""

import os
import json
import time
from groq_optimized_simple_rag import GroqOptimizedSimpleRAG

def test_technical_analysis():
    """Test the system with technical analysis and stock questions"""
    
    print("🚀 Testing Technical Analysis & Stock Analysis")
    print("="*60)
    
    # Initialize system
    api_key = "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"
    
    try:
        print("🔄 Initializing RAG system...")
        rag = GroqOptimizedSimpleRAG(api_key)
        
        print(f"✅ System initialized successfully!")
        print(f"📊 Loaded chunks: {len(rag.chunks)}")
        print()
        
        # Technical analysis and stock market questions
        technical_questions = [
            {
                "question": "BIST-100 için teknik yorum nedir?",
                "type": "technical_analysis",
                "expected_topics": ["BIST", "teknik", "yorum", "seviye", "destek", "direnç"]
            },
            {
                "question": "Hangi hisse senetleri en yüksek getiri sağladı?",
                "type": "stock_performance",
                "expected_topics": ["hisse", "getiri", "performans", "yükseldi"]
            },
            {
                "question": "Banka hisseleri nasıl performans gösterdi?",
                "type": "sector_analysis",
                "expected_topics": ["banka", "hisse", "performans", "endeks"]
            },
            {
                "question": "VİOP kontratları hakkında ne söyleniyor?",
                "type": "derivatives_analysis", 
                "expected_topics": ["VİOP", "kontrat", "vadeli", "işlem"]
            },
            {
                "question": "Piyasa hacmi ve işlem hacmi nasıl?",
                "type": "market_volume",
                "expected_topics": ["hacim", "işlem", "piyasa", "değer"]
            },
            {
                "question": "En çok düşen hisse senetleri hangileri?",
                "type": "stock_decliners",
                "expected_topics": ["düşen", "hisse", "negatif", "gerileme"]
            },
            {
                "question": "Teknik analiz açısından destek ve direnç seviyeleri neler?",
                "type": "support_resistance",
                "expected_topics": ["destek", "direnç", "seviye", "teknik", "analiz"]
            },
            {
                "question": "Portföy önerileri var mı? Hangi hisseler öneriliyor?",
                "type": "portfolio_recommendations",
                "expected_topics": ["portföy", "öneri", "hisse", "seçim", "tavsiye"]
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(technical_questions, 1):
            print(f"❓ Test {i}/8: {test_case['question']}")
            print(f"📝 Type: {test_case['type']}")
            
            start_time = time.time()
            
            try:
                # Query the system
                result = rag.query(test_case['question'])
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Display results
                print(f"⏱️  Response time: {response_time:.2f}s")
                print(f"📄 Answer length: {len(result['answer'])} chars")
                print(f"📚 Sources found: {len(result['sources'])}")
                print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
                print()
                print("💬 Answer:")
                print("-" * 40)
                print(result['answer'][:600] + "..." if len(result['answer']) > 600 else result['answer'])
                print("-" * 40)
                
                if result['sources']:
                    print("📖 Top sources:")
                    for j, source in enumerate(result['sources'][:3], 1):
                        content_preview = source.get('content', '')[:50] + "..." if source.get('content') else 'N/A'
                        print(f"   {j}. Page {source.get('page', 'N/A')} - {source.get('type', 'text')} ({source.get('similarity', 0):.3f})")
                        print(f"      Preview: {content_preview}")
                
                print("="*60)
                
                # Store results for analysis
                results.append({
                    'question': test_case['question'],
                    'type': test_case['type'],
                    'response_time': response_time,
                    'answer_length': len(result['answer']),
                    'sources_count': len(result['sources']),
                    'confidence': result.get('confidence'),
                    'answer': result['answer'],
                    'expected_topics': test_case['expected_topics']
                })
                
            except Exception as e:
                print(f"❌ Error with question {i}: {e}")
                print("="*60)
                continue
        
        # Performance summary
        if results:
            print("\n📊 TECHNICAL ANALYSIS TEST SUMMARY")
            print("="*60)
            avg_time = sum(r['response_time'] for r in results) / len(results)
            avg_length = sum(r['answer_length'] for r in results) / len(results)
            avg_sources = sum(r['sources_count'] for r in results) / len(results)
            avg_confidence = sum(r['confidence'] for r in results if r['confidence']) / len([r for r in results if r['confidence']])
            
            print(f"✅ Successful queries: {len(results)}/{len(technical_questions)}")
            print(f"⏱️  Average response time: {avg_time:.2f}s")
            print(f"📝 Average answer length: {avg_length:.0f} chars")
            print(f"📚 Average sources per query: {avg_sources:.1f}")
            print(f"🎯 Average confidence: {avg_confidence:.3f}")
            
            # Analyze topic coverage
            print(f"\n🎯 TOPIC COVERAGE ANALYSIS")
            print("="*40)
            
            for result in results:
                answer_lower = result['answer'].lower()
                expected_topics = result['expected_topics']
                covered_topics = [topic for topic in expected_topics if topic.lower() in answer_lower]
                coverage_rate = len(covered_topics) / len(expected_topics) * 100
                
                print(f"\n{result['type']}:")
                print(f"   Coverage: {coverage_rate:.0f}% ({len(covered_topics)}/{len(expected_topics)})")
                print(f"   Covered: {', '.join(covered_topics)}")
                if len(covered_topics) < len(expected_topics):
                    missed = [topic for topic in expected_topics if topic not in covered_topics]
                    print(f"   Missed: {', '.join(missed)}")
        
        return results
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return None

if __name__ == "__main__":
    results = test_technical_analysis()
    if results:
        # Save detailed test results
        with open('technical_analysis_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Detailed test results saved to technical_analysis_test_results.json")
        
        # Quick quality assessment
        high_quality_answers = [r for r in results if r['confidence'] > 0.7 and r['answer_length'] > 500]
        print(f"\n🏆 High quality answers: {len(high_quality_answers)}/{len(results)}")
        
        fast_responses = [r for r in results if r['response_time'] < 3.0]
        print(f"⚡ Fast responses (<3s): {len(fast_responses)}/{len(results)}")
