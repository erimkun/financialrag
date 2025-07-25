"""
🚀 Simplified Groq RAG Pipeline
===============================
Simplified, working Groq integration for Turkish RAG system.
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from groq import Groq
from faiss_vector_store import FAISSVectorStore
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SimpleRAGResponse:
    """Simple RAG response"""
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    relevance_scores: List[float]
    response_time: float
    confidence_score: float

class SimpleGroqRAG:
    """Simplified Groq RAG Pipeline"""
    
    def __init__(self, 
                 groq_api_key: str,
                 vector_store_path: str = "vector_store",
                 model_name: str = "llama-3.1-8b-instant"):
        """
        Initialize Simple Groq RAG
        
        Args:
            groq_api_key: Groq API key
            vector_store_path: Path to FAISS vector store
            model_name: Groq model name
        """
        self.groq_client = Groq(api_key=groq_api_key)
        self.model_name = model_name
        
        # Initialize FAISS vector store
        logger.info("🔄 Loading FAISS vector store...")
        self.faiss_store = FAISSVectorStore(vector_store_path=vector_store_path)
        
        # Try to load existing vector store
        if not self.faiss_store.load_vector_store():
            logger.warning("⚠️ No existing vector store found. Creating new one...")
            self._create_vector_store()
        
        # Performance stats
        self.stats = {
            'total_queries': 0,
            'avg_response_time': 0.0,
            'successful_responses': 0,
            'failed_responses': 0,
            'avg_confidence': 0.0
        }
        
        logger.info("🚀 Simple Groq RAG initialized successfully")
    
    def _create_vector_store(self):
        """Create vector store from analysis files"""
        analysis_dir = Path("analysis_output")
        if analysis_dir.exists():
            analysis_files = list(analysis_dir.glob("*_complete_analysis.json"))
            if analysis_files:
                with open(analysis_files[0], 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                
                logger.info(f"📄 Processing: {analysis['document_info']['filename']}")
                self.faiss_store.add_pdf_content(analysis)
                self.faiss_store.save_vector_store()
                logger.info("✅ Vector store created")
            else:
                raise ValueError("No analysis files found")
        else:
            raise ValueError("No analysis_output directory found")
    
    def _create_context(self, search_results: List) -> str:
        """Create context from search results"""
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            chunk = result.chunk
            context_parts.append(f"""
KAYNAK {i}:
Dosya: {chunk.source}
Sayfa: {chunk.page_number}
Tür: {chunk.chunk_type}
İçerik: {chunk.text}
""")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create optimized Turkish prompt"""
        return f"""Sen Türkçe PDF dokümanlarını analiz eden uzman bir asistansın. Verilen bağlam bilgilerini kullanarak kullanıcının sorusuna detaylı ve doğru yanıt ver.

BAĞLAM BİLGİLERİ:
{context}

KULLANICI SORUSU: {question}

YANIT KURALLARI:
1. 📋 Sadece verilen bağlam bilgilerini kullan
2. 🇹🇷 Türkçe olarak net ve anlaşılır yanıt ver
3. 📊 Sayısal verileri ve oranları belirt
4. 📄 Kaynak sayfa numaralarını belirt (örn: "Sayfa 2'ye göre...")
5. 📈 Grafik ve tablo bilgilerini dahil et
6. ⚠️ Bağlamda yeterli bilgi yoksa açıkça belirt
7. 🔗 Birden fazla kaynak varsa bunları birleştir
8. 💡 Mümkünse trend ve analiz yap

YANIT FORMATI:
- Ana bilgiyi özetle
- Detayları madde madde yaz
- Kaynak referansları ver
- Gerekirse ek açıklama yap

YANIT:"""
    
    def query(self, question: str, k: int = 7) -> SimpleRAGResponse:
        """
        Process query through Groq RAG
        
        Args:
            question: User question
            k: Number of chunks to retrieve
            
        Returns:
            SimpleRAGResponse
        """
        logger.info(f"🔍 Processing query: {question}")
        start_time = time.time()
        
        try:
            # 1. Retrieve relevant chunks
            search_results = self.faiss_store.search(question, k=k)
            
            if not search_results:
                return SimpleRAGResponse(
                    query=question,
                    answer="Üzgünüm, bu konuyla ilgili yeterli bilgi bulunamadı.",
                    sources=[],
                    relevance_scores=[],
                    response_time=time.time() - start_time,
                    confidence_score=0.0
                )
            
            # 2. Create context
            context = self._create_context(search_results)
            
            # 3. Create prompt
            prompt = self._create_prompt(question, context)
            
            # 4. Call Groq API
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Sen Türkçe konuşan, PDF dokümanlarını analiz eden uzman bir asistansın. Verilen bağlama dayanarak doğru ve yararlı yanıtlar ver."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            answer = response.choices[0].message.content
            
            # 5. Prepare response data
            sources = []
            relevance_scores = []
            
            for result in search_results:
                chunk = result.chunk
                sources.append({
                    'text': chunk.text[:300] + "..." if len(chunk.text) > 300 else chunk.text,
                    'source': chunk.source,
                    'page_number': chunk.page_number,
                    'chunk_type': chunk.chunk_type,
                    'score': result.score
                })
                relevance_scores.append(result.score)
            
            # 6. Calculate confidence
            confidence_score = float(np.mean(relevance_scores)) if relevance_scores else 0.0
            response_time = time.time() - start_time
            
            # 7. Update stats
            self.stats['total_queries'] += 1
            self.stats['successful_responses'] += 1
            self.stats['avg_response_time'] = (
                (self.stats['avg_response_time'] * (self.stats['total_queries'] - 1) + response_time) /
                self.stats['total_queries']
            )
            self.stats['avg_confidence'] = (
                (self.stats['avg_confidence'] * (self.stats['total_queries'] - 1) + confidence_score) /
                self.stats['total_queries']
            )
            
            logger.info(f"✅ Query processed in {response_time:.2f}s (Confidence: {confidence_score:.3f})")
            
            return SimpleRAGResponse(
                query=question,
                answer=answer,
                sources=sources,
                relevance_scores=relevance_scores,
                response_time=response_time,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            self.stats['failed_responses'] += 1
            
            return SimpleRAGResponse(
                query=question,
                answer=f"Üzgünüm, sorunuzu işlerken bir hata oluştu: {str(e)}",
                sources=[],
                relevance_scores=[],
                response_time=time.time() - start_time,
                confidence_score=0.0
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        vector_stats = self.faiss_store.get_statistics()
        return {
            'pipeline_stats': self.stats,
            'vector_stats': vector_stats,
            'model': self.model_name
        }
    
    def interactive_chat(self):
        """Interactive chat interface"""
        print("🤖 Groq-Powered Turkish RAG Chat")
        print("=" * 50)
        print("🚀 Hızlı ve akıllı Türkçe PDF analizi")
        print("Sorularınızı yazın (çıkmak için 'quit' yazın)")
        print("Komutlar: 'stats' (istatistikler), 'help' (yardım)")
        print()
        
        while True:
            try:
                question = input("📝 Soru: ").strip()
                
                if question.lower() in ['quit', 'exit', 'çıkış', 'q']:
                    print("👋 Görüşürüz!")
                    break
                
                if question.lower() == 'stats':
                    stats = self.get_stats()
                    print(f"\n📊 Pipeline İstatistikleri:")
                    print(f"   🔢 Toplam sorgu: {stats['pipeline_stats']['total_queries']}")
                    print(f"   ⏱️ Ortalama süre: {stats['pipeline_stats']['avg_response_time']:.2f}s")
                    print(f"   ✅ Başarılı: {stats['pipeline_stats']['successful_responses']}")
                    print(f"   ❌ Başarısız: {stats['pipeline_stats']['failed_responses']}")
                    print(f"   🎯 Ortalama güven: {stats['pipeline_stats']['avg_confidence']:.3f}")
                    print(f"   📚 Toplam chunk: {stats['vector_stats']['total_chunks']}")
                    print(f"   🤖 Model: {stats['model']}")
                    continue
                
                if question.lower() == 'help':
                    print("\n🆘 Yardım:")
                    print("   • Türkçe sorular sorun")
                    print("   • 'stats' - İstatistikleri göster")
                    print("   • 'quit' - Çıkış")
                    print("   • Örnek: 'Bütçe dengesi nasıl?'")
                    continue
                
                if not question:
                    continue
                
                print("🔄 İşleniyor...")
                response = self.query(question)
                
                print(f"\n🤖 Yanıt:")
                print(f"{response.answer}")
                
                print(f"\n📊 Metadata:")
                print(f"   ⏱️ Süre: {response.response_time:.2f}s")
                print(f"   🎯 Güven: {response.confidence_score:.3f}")
                print(f"   📚 Kaynak sayısı: {len(response.sources)}")
                
                if response.sources:
                    print(f"\n📚 Kaynaklar:")
                    for i, source in enumerate(response.sources, 1):
                        print(f"   {i}. {source['source']} - Sayfa {source['page_number']} (Skor: {source['score']:.3f})")
                        print(f"      {source['text'][:100]}...")
                
                print("\n" + "="*50)
                
            except KeyboardInterrupt:
                print("\n👋 Görüşürüz!")
                break
            except Exception as e:
                print(f"❌ Hata: {e}")

def main():
    """Test Simple Groq RAG"""
    print("🚀 Simple Groq RAG Pipeline Test")
    print("=" * 50)
    
    # API key
    api_key = "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"
    
    try:
        # Initialize pipeline
        rag = SimpleGroqRAG(
            groq_api_key=api_key,
            model_name="llama-3.1-8b-instant"
        )
        
        # Test queries
        test_queries = [
            "Bütçe dengesi hakkında detaylı bilgi ver",
            "Enflasyon oranları ve trend analizi",
            "Grafiklerdeki ekonomik göstergeler neler?",
            "Türkiye'nin ekonomik durumu nasıl?",
            "ABD ekonomisindeki gelişmeler neler?"
        ]
        
        print("📋 Test Sorular:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. {query}")
            response = rag.query(query)
            print(f"   🤖 {response.answer[:200]}...")
            print(f"   📊 Güven: {response.confidence_score:.3f} | Kaynak: {len(response.sources)} | Süre: {response.response_time:.2f}s")
        
        # Show statistics
        stats = rag.get_stats()
        print(f"\n📊 Pipeline İstatistikleri:")
        print(f"   Toplam sorgu: {stats['pipeline_stats']['total_queries']}")
        print(f"   Ortalama süre: {stats['pipeline_stats']['avg_response_time']:.2f}s")
        print(f"   Ortalama güven: {stats['pipeline_stats']['avg_confidence']:.3f}")
        print(f"   Model: {stats['model']}")
        
        # Interactive mode
        print(f"\n🎮 İnteraktif moda geçmek için 'i' yazın, çıkmak için Enter'a basın")
        choice = input().strip().lower()
        
        if choice == 'i':
            rag.interactive_chat()
        
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        print("💡 Önce integrated_analyzer.py çalıştırarak analiz dosyaları oluşturun")

if __name__ == "__main__":
    main() 