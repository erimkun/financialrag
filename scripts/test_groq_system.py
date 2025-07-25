"""
🧪 Test Groq Optimized Simple RAG System
Comprehensive testing with Turkish financial document questions
"""

import os
import json
import time
from groq_optimized_simple_rag import GroqOptimizedSimpleRAG

def test_system_performance():
    """Test the Groq RAG system with various questions"""
    
    print("🚀 Starting Groq Optimized Simple RAG Test")
    print("="*60)
    
    # Initialize system
    api_key = "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"
    
    try:
        print("🔄 Initializing RAG system...")
        rag = GroqOptimizedSimpleRAG(api_key)
        
        print(f"✅ System initialized successfully!")
        print(f"📊 Loaded chunks: {len(rag.chunks)}")
        print(f"🔍 FAISS index ready: {rag.faiss_index is not None}")
        print()
        
        # Test questions - Mix of different types
        test_questions = [
            {
                "question": "Bu rapordaki ana bulgular nelerdir?",
                "type": "summary",
                "expected_topics": ["bulgular", "sonuçlar", "özet"]
            },
            {
                "question": "Finansal performans nasıl değerlendiriliyor?",
                "type": "analysis", 
                "expected_topics": ["finansal", "performans", "değerlendirme"]
            },
            {
                "question": "Raporda hangi riskler belirtiliyor?",
                "type": "risk_analysis",
                "expected_topics": ["risk", "tehlike", "sorun"]
            },
            {
                "question": "Ekonomik göstergeler nasıl?",
                "type": "economic_indicators",
                "expected_topics": ["ekonomik", "gösterge", "oran"]
            },
            {
                "question": "Bütçe dengesi hakkında ne söyleniyor?",
                "type": "budget_analysis",
                "expected_topics": ["bütçe", "denge", "mali"]
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_questions, 1):
            print(f"❓ Test {i}/5: {test_case['question']}")
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
                print(result['answer'][:500] + "..." if len(result['answer']) > 500 else result['answer'])
                print("-" * 40)
                
                if result['sources']:
                    print("📖 Top sources:")
                    for j, source in enumerate(result['sources'][:2], 1):
                        print(f"   {j}. Page {source.get('page', 'N/A')} - {source.get('type', 'text')} ({source.get('similarity', 0):.3f} similarity)")
                
                print("="*60)
                
                # Store results for analysis
                results.append({
                    'question': test_case['question'],
                    'type': test_case['type'],
                    'response_time': response_time,
                    'answer_length': len(result['answer']),
                    'sources_count': len(result['sources']),
                    'confidence': result.get('confidence'),
                    'answer': result['answer']
                })
                
            except Exception as e:
                print(f"❌ Error with question {i}: {e}")
                print("="*60)
                continue
        
        # Performance summary
        if results:
            print("\n📊 PERFORMANCE SUMMARY")
            print("="*60)
            avg_time = sum(r['response_time'] for r in results) / len(results)
            avg_length = sum(r['answer_length'] for r in results) / len(results)
            avg_sources = sum(r['sources_count'] for r in results) / len(results)
            
            print(f"✅ Successful queries: {len(results)}/{len(test_questions)}")
            print(f"⏱️  Average response time: {avg_time:.2f}s")
            print(f"📝 Average answer length: {avg_length:.0f} chars")
            print(f"📚 Average sources per query: {avg_sources:.1f}")
            
            # Check system stats
            if hasattr(rag, 'query_stats'):
                print(f"\n📈 System Stats:")
                print(f"   Total queries: {rag.query_stats['total_queries']}")
                print(f"   Total time: {rag.query_stats['total_time']:.2f}s")
        
        return results
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return None

def analyze_answer_quality(results):
    """Analyze the quality of answers"""
    if not results:
        return
    
    print("\n🔍 ANSWER QUALITY ANALYSIS")
    print("="*60)
    
    for i, result in enumerate(results, 1):
        answer = result['answer'].lower()
        question_type = result['type']
        
        # Check for relevant keywords
        quality_score = 0
        feedback = []
        
        # Check for Turkish language quality
        turkish_indicators = ['ın', 'un', 'ları', 'leri', 'dir', 'dır', 'tır', 'tir']
        if any(indicator in answer for indicator in turkish_indicators):
            quality_score += 2
            feedback.append("✅ Good Turkish language usage")
        
        # Check for specific content based on question type
        if question_type == "summary" and any(word in answer for word in ['rapor', 'bulgular', 'sonuç']):
            quality_score += 2
            feedback.append("✅ Contains summary elements")
        
        if question_type == "analysis" and any(word in answer for word in ['analiz', 'değerlendirme', 'gösterge']):
            quality_score += 2
            feedback.append("✅ Contains analytical content")
        
        # Check answer completeness
        if len(result['answer']) > 100:
            quality_score += 1
            feedback.append("✅ Comprehensive answer")
        
        if result['sources_count'] > 0:
            quality_score += 1
            feedback.append("✅ Backed by sources")
        
        print(f"Test {i} - {question_type}")
        print(f"Quality Score: {quality_score}/8")
        for fb in feedback:
            print(f"   {fb}")
        print()

if __name__ == "__main__":
    results = test_system_performance()
    if results:
        analyze_answer_quality(results)
        
        # Save test results
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("\n💾 Test results saved to test_results.json")
