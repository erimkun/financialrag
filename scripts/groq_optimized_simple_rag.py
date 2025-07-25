"""
🚀 Groq Optimized Simple RAG Pipeline
Advanced Turkish language RAG system with optimized prompts - Simple Version
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from groq import Groq
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
try:
    from .turkish_prompt_optimizer import TurkishPromptOptimizer, PromptContext, DocumentType, QueryType
except ImportError:
    from turkish_prompt_optimizer import TurkishPromptOptimizer, PromptContext, DocumentType, QueryType

class GroqOptimizedSimpleRAG:
    """Simple optimized Groq RAG system with Turkish prompts"""
    
    def __init__(self, groq_api_key: str):
        self.groq_client = Groq(api_key=groq_api_key)
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        
        # Initialize prompt optimizer
        self.prompt_optimizer = TurkishPromptOptimizer()
        
        # Load extracted data
        self.chunks = []
        self.faiss_index = None
        self._load_extracted_data()
        
        # Performance tracking
        self.query_stats = {
            'total_queries': 0,
            'total_time': 0,
            'confidence_scores': [],
            'query_types': [],
            'document_types': []
        }
    
    def _load_extracted_data(self):
        """Load extracted data from integrated analyzer"""
        try:
            # Load from analysis output
            analysis_dir = "analysis_output"
            if not os.path.exists(analysis_dir):
                print(f"❌ Analysis directory not found: {analysis_dir}")
                return
            
            # Find the latest analysis file
            analysis_files = [f for f in os.listdir(analysis_dir) if f.endswith('.json')]
            if not analysis_files:
                print(f"❌ No analysis files found in {analysis_dir}")
                return
            
            latest_file = max(analysis_files)
            analysis_path = os.path.join(analysis_dir, latest_file)
            
            print(f"📄 Loading analysis from: {latest_file}")
            
            with open(analysis_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract chunks from analysis
            self.chunks = []
            
            # Add PDF content pages
            pdf_content = data.get('pdf_content', {})
            pages = pdf_content.get('pages', [])
            
            print(f"🔍 Found {len(pages)} pages in PDF content")
            
            for page in pages:
                page_num = page.get('sayfa', 0)
                print(f"📄 Processing page {page_num}")
                
                # Add title as a chunk
                title = page.get('başlık', '').strip()
                if title:
                    self.chunks.append({
                        'content': title,
                        'type': 'title',
                        'page': page_num,
                        'metadata': {'type': 'title', 'page': page_num}
                    })
                    print(f"   ✅ Added title: {title[:50]}...")
                
                # Add paragraphs as chunks
                paragraphs = page.get('paragraflar', [])
                
                # Handle both string and list formats
                if isinstance(paragraphs, str):
                    try:
                        import ast
                        paragraphs = ast.literal_eval(paragraphs)
                    except:
                        # If it's a string, split by common delimiters
                        paragraphs = [p.strip() for p in paragraphs.split('\n') if p.strip()]
                
                print(f"   📝 Found {len(paragraphs)} paragraphs")
                
                for i, para in enumerate(paragraphs):
                    if isinstance(para, str) and para.strip():
                        self.chunks.append({
                            'content': para.strip(),
                            'type': 'text',
                            'page': page_num,
                            'metadata': {'type': 'text', 'page': page_num, 'paragraph_index': i}
                        })
                        print(f"     ✅ Added paragraph {i+1}: {para[:30]}...")
            
            # Add chart data from charts key
            charts = data.get('charts', [])
            print(f"🔍 Found {len(charts)} charts")
            
            for chart in charts:
                if chart.get('ocr_text', '').strip():
                    self.chunks.append({
                        'content': chart['ocr_text'],
                        'type': 'chart',
                        'page': chart.get('page', 0),
                        'metadata': chart
                    })
                    print(f"   ✅ Added chart OCR: {chart['ocr_text'][:50]}...")
                    
                # Also add chart analysis if available
                if chart.get('analysis', '').strip():
                    self.chunks.append({
                        'content': chart['analysis'],
                        'type': 'chart_analysis',
                        'page': chart.get('page', 0),
                        'metadata': chart
                    })
                    print(f"   ✅ Added chart analysis: {chart['analysis'][:50]}...")
            
            # Add chart analysis from main chart_analysis key
            chart_analysis = data.get('chart_analysis', {})
            if chart_analysis:
                print(f"🔍 Found chart_analysis section")
                for key, value in chart_analysis.items():
                    if isinstance(value, str) and value.strip():
                        self.chunks.append({
                            'content': value,
                            'type': 'chart_analysis',
                            'page': 0,
                            'metadata': {'type': 'chart_analysis', 'section': key}
                        })
                        print(f"   ✅ Added chart analysis section {key}: {value[:50]}...")
            
            print(f"✅ Loaded {len(self.chunks)} chunks")
            
            # Create FAISS index
            if self.chunks:
                self._create_faiss_index()
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def _create_faiss_index(self):
        """Create FAISS index from chunks"""
        try:
            print("🔄 Creating FAISS index...")
            
            # Extract content for embedding
            contents = [chunk['content'] for chunk in self.chunks]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(contents, show_progress_bar=True)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to index
            self.faiss_index.add(embeddings.astype('float32'))
            
            print(f"✅ FAISS index created with {len(self.chunks)} chunks")
            
        except Exception as e:
            print(f"❌ Error creating FAISS index: {e}")
    
    def _search_similar_chunks(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar chunks using FAISS"""
        if self.faiss_index is None or not self.chunks:
            return []
        
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index
            similarities, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
            
            # Prepare results
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if 0 <= idx < len(self.chunks):
                    results.append({
                        'content': self.chunks[idx]['content'],
                        'metadata': self.chunks[idx]['metadata'],
                        'type': self.chunks[idx]['type'],
                        'page': self.chunks[idx]['page'],
                        'similarity': float(similarity),
                        'rank': i + 1
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def _create_context_from_results(self, results: List[Dict]) -> str:
        """Create context string from search results"""
        context_parts = []
        
        for result in results:
            content = result['content']
            page = result['page']
            similarity = result['similarity']
            chunk_type = result['type']
            
            # Format context with metadata
            context_part = f"[Kaynak {result['rank']} - {chunk_type.upper()} - Sayfa {page} - Benzerlik: {similarity:.3f}]\n{content}"
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _calculate_confidence(self, results: List[Dict], response_length: int) -> float:
        """Calculate confidence score based on search results and response"""
        if not results:
            return 0.0
        
        # Average similarity score
        avg_similarity = sum(r['similarity'] for r in results) / len(results)
        
        # Response length factor (longer responses generally more confident)
        length_factor = min(response_length / 500, 1.0)
        
        # Number of sources factor
        source_factor = min(len(results) / 5, 1.0)
        
        # Type diversity factor (different types of content)
        types = set(r['type'] for r in results)
        type_factor = min(len(types) / 3, 1.0)
        
        # Combined confidence
        confidence = (avg_similarity * 0.5) + (length_factor * 0.2) + (source_factor * 0.2) + (type_factor * 0.1)
        
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
                    'sources': [],
                    'sources_count': 0,
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
                'sources': search_results,  # Return the actual results list
                'sources_count': len(search_results),  # Keep the count separate
                'query_time': query_time,
                'query_type': query_type.value,
                'document_type': doc_type.value,
                'search_results': search_results[:3]
            }
            
        except Exception as e:
            return {
                'answer': f'Hata oluştu: {str(e)}',
                'confidence': 0.0,
                'sources': [],
                'sources_count': 0,
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
        print("\n🎮 Groq Optimized Simple RAG - İnteraktif Mod")
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
                    if 'query_type_distribution' in stats:
                        print(f"   Sorgu türü dağılımı: {stats['query_type_distribution']}")
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

def test_optimized_simple_rag():
    """Test the optimized simple RAG system"""
    # Groq API key
    groq_api_key = "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"
    
    # Initialize RAG system
    print("🚀 Groq Optimized Simple RAG başlatılıyor...")
    rag = GroqOptimizedSimpleRAG(groq_api_key)
    
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
    if 'total_queries' in stats:
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
    test_optimized_simple_rag() 