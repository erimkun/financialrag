"""
🧪 Memory Optimized RAG Test
Test memory-optimized version vs regular version
"""

import time
import psutil
import os
from memory_optimized_groq_rag import MemoryOptimizedGroqRAG

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_memory_optimized_rag():
    """Test memory optimized RAG system"""
    print("🧪 Memory Optimized RAG Test")
    print("="*50)
    
    api_key = "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"
    
    # Test both lite and full modes
    modes = [
        ("Lite Mode (No ML)", True),
        ("Full Mode (With ML)", False)
    ]
    
    for mode_name, lite_mode in modes:
        print(f"\n🔄 Testing {mode_name}")
        print("-" * 30)
        
        # Memory before initialization
        memory_before = get_memory_usage()
        print(f"📊 Memory before init: {memory_before:.1f} MB")
        
        try:
            # Initialize system
            start_time = time.time()
            rag = MemoryOptimizedGroqRAG(api_key, lite_mode=lite_mode)
            init_time = time.time() - start_time
            
            # Memory after initialization
            memory_after = get_memory_usage()
            memory_increase = memory_after - memory_before
            
            print(f"✅ Initialization: {init_time:.2f}s")
            print(f"📊 Memory after init: {memory_after:.1f} MB (+{memory_increase:.1f} MB)")
            print(f"📄 Loaded chunks: {len(rag.chunks)}")
            print(f"🔍 FAISS available: {rag.faiss_index is not None}")
            
            # Test query
            test_queries = [
                "BIST-100 endeksi nasıl performans gösterdi?",
                "Mamul mal stoku ne durumda?",
                "Enflasyon hakkında ne bilgiler var?"
            ]
            
            for i, query in enumerate(test_queries[:2]):  # Test first 2 queries
                print(f"\n📝 Query {i+1}: {query}")
                
                # Memory before query
                memory_before_query = get_memory_usage()
                
                # Execute query
                query_start = time.time()
                result = rag.retrieve_and_generate(query, k=3)
                query_time = time.time() - query_start
                
                # Memory after query
                memory_after_query = get_memory_usage()
                
                print(f"⚡ Query time: {query_time:.2f}s")
                print(f"📊 Memory usage: {memory_after_query:.1f} MB")
                print(f"📝 Answer preview: {result[:100]}...")
                
                if query_time > 10:  # If query takes too long, break
                    print("⚠️ Query taking too long, stopping test")
                    break
            
            return {
                'mode': mode_name,
                'success': True,
                'init_time': init_time,
                'memory_increase': memory_increase,
                'chunks': len(rag.chunks),
                'has_faiss': rag.faiss_index is not None
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'mode': mode_name,
                'success': False,
                'error': str(e)
            }

def test_memory_comparison():
    """Compare memory usage with different approaches"""
    print("\n💾 Memory Usage Comparison")
    print("="*50)
    
    results = []
    
    # Test memory optimized versions
    result = test_memory_optimized_rag()
    results.append(result)
    
    # Summary
    print("\n📋 Test Summary")
    print("="*50)
    
    for result in results:
        if result['success']:
            print(f"✅ {result['mode']}")
            print(f"   Init time: {result['init_time']:.2f}s")
            print(f"   Memory increase: {result['memory_increase']:.1f} MB")
            print(f"   Chunks loaded: {result['chunks']}")
            print(f"   FAISS enabled: {result['has_faiss']}")
        else:
            print(f"❌ {result['mode']}: {result.get('error', 'Unknown error')}")
    
    print(f"\n💡 Recommendations:")
    print(f"   - Use Lite Mode for low memory environments")
    print(f"   - Use Full Mode when memory is sufficient") 
    print(f"   - Lite Mode uses keyword search (faster, less accurate)")
    print(f"   - Full Mode uses semantic search (slower, more accurate)")

if __name__ == "__main__":
    test_memory_comparison()
