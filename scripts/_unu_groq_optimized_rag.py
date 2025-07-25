"""
🚀 Groq Optimized RAG Pipeline
Advanced Turkish language RAG system with optimized prompts
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from groq import Groq
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from turkish_prompt_optimizer import TurkishPromptOptimizer, PromptContext, DocumentType, QueryType

class GroqOptimizedRAG:
    """Advanced Groq RAG system with optimized Turkish prompts"""
    
    def __init__(self, groq_api_key: str, vector_store_path: str = "vector_store"):
        self.groq_client = Groq(api_key=groq_api_key)
        self.vector_store_path = vector_store_path
        self.embedding_model = None
        self.faiss_index = None
        self.chunks = []
        self.chunk_metadata = []
        
        # Initialize prompt optimizer
        self.prompt_optimizer = TurkishPromptOptimizer()
        
        # Performance tracking
        self.query_stats = {
            'total_queries': 0,
            'total_time': 0,
            'confidence_scores': [],
            'query_types': [],
            'document_types': []
        }
        
        self._load_vector_store()
    
    def _load_vector_store(self):
        """Load FAISS vector store and embeddings"""
        try:
            # Load embedding model
            print("📥 Embedding model yükleniyor...")
            self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
            
            # Load FAISS index
            index_path = os.path.join(self.vector_store_path, "faiss_index.bin")
            self.faiss_index = faiss.read_index(index_path)
            
            # Load chunks and metadata
            chunks_path = os.path.join(self.vector_store_path, "chunks.pkl")
            import pickle
            with open(chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
            
            with open(os.path.join(self.vector_store_path, "metadata.json"), 'r', encoding='utf-8') as f:
                self.chunk_metadata = json.load(f)
            
            print(f"✅ Vector store yüklendi: {len(self.chunks)} chunk")
            
        except Exception as e:
            print(f"❌ Vector store yüklenemedi: {e}")
            raise
    
    def _search_similar_chunks(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar chunks using FAISS"""
        if self.embedding_model is None or self.faiss_index is None:
            return []
            
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in FAISS index
        distances, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
        
        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunks):  # Valid index check
                similarity = float(1 - distance)  # Convert distance to similarity
                results.append({
                    'content': self.chunks[idx],
                    'metadata': self.chunk_metadata[idx],
                    'similarity': similarity,
                    'rank': i + 1
                })
        
        return results
    
    def _create_context_from_results(self, results: List[Dict]) -> str:
        """Create context string from search results"""
        context_parts = []
        
        for result in results:
            content = result['content']
            metadata = result['metadata']
            similarity = result['similarity']
            
            # Format context with metadata
            context_part = f"[Kaynak {result['rank']} - Benzerlik: {similarity:.3f}]\n{content}"
            
            # Add metadata if available
            if metadata.get('page'):
                context_part += f"\n(Sayfa: {metadata['page']})"
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _calculate_confidence(self, results: List[Dict], response_length: int) -> float:
        """Calculate confidence score based on search results and response"""
        if not results:
            return 0.0
        
        # Average similarity score
        avg_similarity = sum(r['similarity'] for r in results) / len(results)
        
        # Response length factor (longer responses generally more confident)
        length_factor = min(response_length / 500, 1.0)  # Normalize to max 1.0
        
        # Number of sources factor
        source_factor = min(len(results) / 5, 1.0)  # Normalize to max 1.0
        
        # Combined confidence
        confidence = (avg_similarity * 0.6) + (length_factor * 0.2) + (source_factor * 0.2)
        
        return min(confidence, 1.0)
    
    def query(self, question: str, max_context_length: int = 2000) -> Dict:
        """Process query with optimized prompts"""
        start_time = time.time()
        
        try:
            # 1. Search for relevant chunks
            search_results = self._search_similar_chunks(question, k=5)
            
            if not search_results:
                return {
                    'answer': 'Üzgünüm, sorunuzla ilgili bilgi bulunamadı.',
                    'confidence': 0.0,
                    'sources': 0,
                    'query_time': time.time() - start_time,
                    'query_type': 'unknown',
                    'document_type': 'unknown'
                }
            
            # 2. Create context
            context = self._create_context_from_results(search_results)
            
            # Limit context length
            if len(context) > max_context_length:
                context = context[:max_context_length] + "..."
            
            # 3. Detect query and document types
            query_type = self.prompt_optimizer.detect_query_type(question)
            doc_type = self.prompt_optimizer.detect_document_type(context)
            
            # 4. Create optimized prompt
            optimized_prompt = self.prompt_optimizer.create_optimized_prompt(
                question, context
            )
            
            # 5. Generate response with Groq
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": optimized_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content or ""
            
            # 6. Calculate confidence
            confidence = self._calculate_confidence(search_results, len(answer))
            
            # 7. Optimize response format
            formatted_answer = self.prompt_optimizer.optimize_response_format(
                answer, confidence
            )
            
            query_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(query_time, confidence, query_type, doc_type)
            
            return {
                'answer': formatted_answer,
                'confidence': confidence,
                'sources': len(search_results),
                'query_time': query_time,
                'query_type': query_type.value,
                'document_type': doc_type.value,
                'search_results': search_results[:3]  # Top 3 for reference
            }
            
        except Exception as e:
            return {
                'answer': f'Hata oluştu: {str(e)}',
                'confidence': 0.0,
                'sources': 0,
                'query_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _update_stats(self, query_time: float, confidence: float, 
                     query_type: QueryType, doc_type: DocumentType):
        """Update performance statistics"""
        self.query_stats['total_queries'] += 1
        self.query_stats['total_time'] += query_time
        self.query_stats['confidence_scores'].append(confidence)
        self.query_stats['query_types'].append(query_type.value)
        self.query_stats['document_types'].append(doc_type.value)
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        if self.query_stats['total_queries'] == 0:
            return {'message': 'Henüz sorgu yapılmamış'}
        
        avg_time = self.query_stats['total_time'] / self.query_stats['total_queries']
        avg_confidence = sum(self.query_stats['confidence_scores']) / len(self.query_stats['confidence_scores'])
        
        # Query type distribution
        query_type_dist = {}
        for qt in self.query_stats['query_types']:
            query_type_dist[qt] = query_type_dist.get(qt, 0) + 1
        
        # Document type distribution
        doc_type_dist = {}
        for dt in self.query_stats['document_types']:
            doc_type_dist[dt] = doc_type_dist.get(dt, 0) + 1
        
        return {
            'total_queries': self.query_stats['total_queries'],
            'average_time': avg_time,
            'average_confidence': avg_confidence,
            'query_type_distribution': query_type_dist,
            'document_type_distribution': doc_type_dist,
            'confidence_distribution': {
                'high (>0.8)': len([c for c in self.query_stats['confidence_scores'] if c > 0.8]),
                'medium (0.6-0.8)': len([c for c in self.query_stats['confidence_scores'] if 0.6 <= c <= 0.8]),
                'low (<0.6)': len([c for c in self.query_stats['confidence_scores'] if c < 0.6])
            }
        }
    
    def interactive_mode(self):
        """Interactive query mode"""
        print("\n🎮 Groq Optimized RAG - İnteraktif Mod")
        print("=" * 50)
        print("Çıkmak için 'exit' yazın")
        print("İstatistikleri görmek için 'stats' yazın")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n❓ Sorunuz: ").strip()
                
                if question.lower() in ['exit', 'çık', 'quit']:
                    print("👋 Güle güle!")
                    break
                
                if question.lower() == 'stats':
                    stats = self.get_performance_stats()
                    print(f"\n📊 Performans İstatistikleri:")
                    print(f"   Toplam sorgu: {stats.get('total_queries', 0)}")
                    print(f"   Ortalama süre: {stats.get('average_time', 0):.2f}s")
                    print(f"   Ortalama güven: {stats.get('average_confidence', 0):.3f}")
                    continue
                
                if not question:
                    continue
                
                print("\n🔍 Aranıyor...")
                result = self.query(question)
                
                print(f"\n💬 Yanıt:")
                print(result['answer'])
                
                print(f"\n📊 Güven: {result['confidence']:.3f} | Kaynak: {result['sources']} | Süre: {result['query_time']:.2f}s")
                print(f"🔖 Tür: {result.get('query_type', 'unknown')} | Doküman: {result.get('document_type', 'unknown')}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Güle güle!")
                break
            except Exception as e:
                print(f"\n❌ Hata: {e}")

def test_optimized_rag():
    """Test the optimized RAG system"""
    # Groq API key
    groq_api_key = "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"
    
    # Initialize RAG system
    print("🚀 Groq Optimized RAG başlatılıyor...")
    rag = GroqOptimizedRAG(groq_api_key)
    
    # Test queries with different types
    test_queries = [
        "Türkiye'nin bütçe dengesi nasıl?",  # Factual
        "Enflasyon neden yükseliyor?",       # Analytical
        "TÜFE ile ÜFE arasındaki fark nedir?",  # Explanatory
        "Bu ay ile geçen ay arasındaki fark nedir?",  # Comparative
        "Enflasyon oranı yüzde kaç?"         # Statistical
    ]
    
    print(f"\n🧪 {len(test_queries)} test sorusu çalıştırılıyor...")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        result = rag.query(query)
        
        print(f"💬 {result['answer'][:200]}...")
        print(f"📊 Güven: {result['confidence']:.3f} | Kaynak: {result['sources']} | Süre: {result['query_time']:.2f}s")
        print(f"🔖 Tür: {result.get('query_type', 'unknown')} | Doküman: {result.get('document_type', 'unknown')}")
    
    # Show overall statistics
    print(f"\n📊 Genel İstatistikler:")
    stats = rag.get_performance_stats()
    print(f"   Toplam sorgu: {stats['total_queries']}")
    print(f"   Ortalama süre: {stats['average_time']:.2f}s")
    print(f"   Ortalama güven: {stats['average_confidence']:.3f}")
    print(f"   Sorgu türü dağılımı: {stats['query_type_distribution']}")
    print(f"   Güven dağılımı: {stats['confidence_distribution']}")
    
    # Interactive mode option
    print(f"\n🎮 İnteraktif moda geçmek için 'i' yazın, çıkmak için Enter'a basın")
    choice = input().strip().lower()
    
    if choice == 'i':
        rag.interactive_mode()

if __name__ == "__main__":
    test_optimized_rag() 