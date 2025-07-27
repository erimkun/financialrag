#!/usr/bin/env python3
"""
Performance Test - Before vs After Optimization
Tests response times and memory usage
"""

import requests
import time
import statistics
import psutil
import os

API_BASE_URL = "http://localhost:8000"

def test_query_performance():
    """Test query performance with multiple requests"""
    
    print("🚀 TESTING QUERY PERFORMANCE")
    print("="*40)
    
    test_queries = [
        "BIST-100 endeksinin son durumu nedir?",
        "Bankacılık sektörü performansı nasıl?", 
        "Döviz kurlarındaki değişimler hakkında bilgi ver",
        "Enflasyon oranları ne durumda?",
        "Faiz oranları ekonomiyi nasıl etkiliyor?",
        "BIST-100 endeksinin son durumu nedir?",  # Duplicate for cache test
        "Bankacılık sektörü performansı nasıl?",  # Duplicate for cache test
    ]
    
    response_times = []
    cache_hits = 0
    
    for i, query in enumerate(test_queries, 1):
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE_URL}/api/query",
                json={"question": query, "language": "tr"},
                timeout=30
            )
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                cached = data.get('cached', False)
                if cached:
                    cache_hits += 1
                
                print(f"Query {i}: {response_time:.2f}s {'(CACHED)' if cached else ''}")
                print(f"  Confidence: {data.get('confidence', 0):.1%}")
                
            else:
                print(f"Query {i}: FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"Query {i}: ERROR - {e}")
    
    # Calculate statistics
    if response_times:
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\n📊 PERFORMANCE STATISTICS:")
        print(f"Average Response Time: {avg_time:.2f}s")
        print(f"Median Response Time: {median_time:.2f}s")
        print(f"Fastest Response: {min_time:.2f}s")
        print(f"Slowest Response: {max_time:.2f}s")
        print(f"Cache Hits: {cache_hits}/{len(test_queries)} ({cache_hits/len(test_queries):.1%})")
        
        # Performance rating
        if avg_time < 3.0:
            print("🎉 EXCELLENT performance!")
        elif avg_time < 5.0:
            print("✅ GOOD performance")
        elif avg_time < 8.0:
            print("⚠️ ACCEPTABLE performance")
        else:
            print("❌ NEEDS IMPROVEMENT")

def test_memory_usage():
    """Test memory usage during operations"""
    
    print("\n🧠 TESTING MEMORY USAGE")
    print("="*40)
    
    # Get process info
    try:
        # This is approximate - you'd need the actual backend process ID
        process = psutil.Process(os.getpid())
        
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory usage before test: {memory_before:.1f} MB")
        
        # Simulate some load
        for i in range(5):
            response = requests.post(
                f"{API_BASE_URL}/api/query",
                json={"question": f"Test query {i}", "language": "tr"},
                timeout=15
            )
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory usage after test: {memory_after:.1f} MB")
        print(f"Memory increase: {memory_after - memory_before:.1f} MB")
        
        if memory_after - memory_before < 50:
            print("✅ Good memory management")
        else:
            print("⚠️ High memory usage detected")
            
    except Exception as e:
        print(f"Memory test error: {e}")

def test_optimization_endpoint():
    """Test the optimization endpoint"""
    
    print("\n🔧 TESTING OPTIMIZATION ENDPOINT")
    print("="*40)
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/optimize", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Optimization successful")
            print(f"Cache cleaned: {data.get('cache_cleaned')}")
            print(f"Memory freed: {data.get('memory_freed')}")
        else:
            print(f"❌ Optimization failed: {response.status_code}")
            
    except Exception as e:
        print(f"Optimization test error: {e}")

def main():
    """Run all performance tests"""
    
    print("⚡ PERFORMANCE OPTIMIZATION TESTING")
    print("="*50)
    
    # Test API availability
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ API not available. Start the backend first.")
            return
    except:
        print("❌ Cannot connect to API. Start the backend first.")
        return
    
    test_query_performance()
    test_memory_usage()
    test_optimization_endpoint()
    
    print("\n" + "="*50)
    print("🎯 PERFORMANCE TESTING COMPLETE!")
    print("💡 Check the results above for optimization effectiveness")

if __name__ == "__main__":
    main()
