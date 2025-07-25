"""
🚀 Groq-Powered RAG Pipeline
============================
High-performance RAG system using Groq API for fast inference.
Optimized for Turkish language with enhanced prompt engineering.

Features:
- Groq API integration for fast LLM inference
- Optimized Turkish prompts
- Enhanced context handling
- Better source citation
- Performance monitoring
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore
from langchain.embeddings.base import Embeddings
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

# Groq imports
from groq import Groq
import groq

# Import our custom components
from faiss_vector_store import FAISSVectorStore, SearchResult
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedRAGResponse:
    """Enhanced RAG response with detailed metadata"""
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    relevance_scores: List[float]
    response_time: float
    model_used: str
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None
    citations: Optional[List[str]] = None

class GroqLLM(LLM):
    """Groq LLM wrapper for LangChain"""
    
    model_name: str = "llama-3.1-8b-instant"
    client: Any = None
    temperature: float = 0.1
    max_tokens: int = 1024
    
    def __init__(self, 
                 api_key: str,
                 model_name: str = "llama-3.1-8b-instant",
                 temperature: float = 0.1,
                 max_tokens: int = 1024):
        """
        Initialize Groq LLM
        
        Args:
            api_key: Groq API key
            model_name: Model to use (llama-3.1-8b-instant, llama-3.1-70b-versatile, etc.)
            temperature: Response randomness (0.0-1.0)
            max_tokens: Maximum response length
        """
        super().__init__()
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Available models
        self.available_models = [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile", 
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
            "gemma2-9b-it"
        ]
        
        if model_name not in self.available_models:
            logger.warning(f"⚠️ Model {model_name} not in known models. Using anyway...")
        
        logger.info(f"🚀 Groq LLM initialized: {model_name}")
    
    @property
    def _llm_type(self) -> str:
        return "groq"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        """Call Groq API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Sen Türkçe konuşan, PDF dokümanlarını analiz eden bir asistansın. Verilen bağlama dayanarak doğru ve yararlı yanıtlar ver."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=False,
                stop=stop
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Groq API error: {e}")
            return f"Üzgünüm, yanıt oluştururken bir hata oluştu: {str(e)}"

class CustomFAISSEmbeddings(Embeddings):
    """Custom embeddings wrapper for FAISS vector store"""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        embedding = self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        return embedding[0].tolist()

class CustomFAISSVectorStore(VectorStore):
    """Custom LangChain VectorStore wrapper for our FAISS implementation"""
    
    def __init__(self, faiss_store: FAISSVectorStore):
        self.faiss_store = faiss_store
        self._embeddings = CustomFAISSEmbeddings(faiss_store.model_name)
    
    @property
    def embeddings(self) -> Embeddings:
        """Get embeddings"""
        return self._embeddings
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None, **kwargs) -> List[str]:
        """Add texts to the vector store"""
        raise NotImplementedError("Use FAISSVectorStore.add_pdf_content() instead")
    
    def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        """Search for similar documents"""
        results = self.faiss_store.search(query, k=k)
        
        documents = []
        for result in results:
            doc = Document(
                page_content=result.chunk.text,
                metadata={
                    'source': result.chunk.source,
                    'page_number': result.chunk.page_number,
                    'chunk_type': result.chunk.chunk_type,
                    'score': result.score,
                    'rank': result.rank
                }
            )
            documents.append(doc)
        
        return documents
    
    def similarity_search_with_score(self, query: str, k: int = 4, **kwargs) -> List[Tuple[Document, float]]:
        """Search for similar documents with scores"""
        results = self.faiss_store.search(query, k=k)
        
        documents_with_scores = []
        for result in results:
            doc = Document(
                page_content=result.chunk.text,
                metadata={
                    'source': result.chunk.source,
                    'page_number': result.chunk.page_number,
                    'chunk_type': result.chunk.chunk_type,
                    'rank': result.rank
                }
            )
            documents_with_scores.append((doc, result.score))
        
        return documents_with_scores
    
    @classmethod
    def from_texts(cls, texts: List[str], embedding: Embeddings, metadatas: Optional[List[dict]] = None, **kwargs):
        """Create from texts (not implemented for our use case)"""
        raise NotImplementedError("Use FAISSVectorStore.add_pdf_content() instead")

class GroqRAGPipeline:
    """High-performance RAG Pipeline with Groq API"""
    
    def __init__(self, 
                 groq_api_key: str,
                 vector_store_path: str = "vector_store",
                 model_name: str = "llama-3.1-8b-instant",
                 temperature: float = 0.1,
                 max_tokens: int = 1024):
        """
        Initialize Groq RAG Pipeline
        
        Args:
            groq_api_key: Groq API key
            vector_store_path: Path to FAISS vector store
            model_name: Groq model name
            temperature: Response randomness
            max_tokens: Maximum response length
        """
        self.groq_api_key = groq_api_key
        self.vector_store_path = vector_store_path
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize FAISS vector store
        logger.info("🔄 Loading FAISS vector store...")
        self.faiss_store = FAISSVectorStore(vector_store_path=vector_store_path)
        
        # Try to load existing vector store
        if not self.faiss_store.load_vector_store():
            logger.warning("⚠️ No existing vector store found. Creating new one from analysis files...")
            self._create_vector_store_from_analysis()
        
        # Wrap FAISS store for LangChain
        self.vector_store = CustomFAISSVectorStore(self.faiss_store)
        
        # Initialize Groq LLM
        self.llm = GroqLLM(
            api_key=groq_api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Create optimized Turkish RAG prompt
        self.prompt_template = self._create_optimized_turkish_prompt()
        
        # Initialize RAG chain
        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 7}),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
        
        # Performance tracking
        self.performance_stats = {
            'total_queries': 0,
            'average_response_time': 0.0,
            'successful_responses': 0,
            'failed_responses': 0,
            'total_tokens_used': 0,
            'average_confidence': 0.0
        }
        
        logger.info("🚀 Groq RAG Pipeline initialized successfully")
    
    def _create_vector_store_from_analysis(self):
        """Create vector store from existing analysis files"""
        analysis_dir = Path("analysis_output")
        if analysis_dir.exists():
            analysis_files = list(analysis_dir.glob("*_complete_analysis.json"))
            if analysis_files:
                logger.info(f"📁 Found {len(analysis_files)} analysis files")
                
                # Load and process first analysis
                with open(analysis_files[0], 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                
                logger.info(f"📄 Processing: {analysis['document_info']['filename']}")
                self.faiss_store.add_pdf_content(analysis)
                
                # Save the vector store
                self.faiss_store.save_vector_store()
                logger.info("✅ Vector store created and saved")
            else:
                raise ValueError("No analysis files found. Run integrated_analyzer.py first.")
        else:
            raise ValueError("No analysis_output directory found. Run integrated_analyzer.py first.")
    
    def _create_optimized_turkish_prompt(self) -> PromptTemplate:
        """Create optimized Turkish RAG prompt template"""
        template = """Sen Türkçe PDF dokümanlarını analiz eden uzman bir asistansın. Verilen bağlam bilgilerini kullanarak kullanıcının sorusuna detaylı ve doğru yanıt ver.

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
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def query(self, question: str, k: int = 7) -> EnhancedRAGResponse:
        """
        Process a query through the optimized RAG pipeline
        
        Args:
            question: User question in Turkish
            k: Number of relevant chunks to retrieve
            
        Returns:
            EnhancedRAGResponse with answer and metadata
        """
        logger.info(f"🔍 Processing query: {question}")
        start_time = time.time()
        
        try:
            # Update retriever with k parameter
            self.rag_chain.retriever.search_kwargs = {"k": k}
            
            # Run RAG chain
            result = self.rag_chain.invoke({"query": question})
            
            # Extract answer and sources
            answer = result["result"]
            source_documents = result["source_documents"]
            
            # Prepare sources, scores, and citations
            sources = []
            relevance_scores = []
            citations = []
            
            for i, doc in enumerate(source_documents, 1):
                source_info = {
                    'text': doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    'source': doc.metadata.get('source', 'unknown'),
                    'page_number': doc.metadata.get('page_number', 0),
                    'chunk_type': doc.metadata.get('chunk_type', 'text'),
                    'rank': doc.metadata.get('rank', i)
                }
                sources.append(source_info)
                
                score = doc.metadata.get('score', 0.0)
                relevance_scores.append(score)
                
                # Create citation
                citation = f"[{i}] {source_info['source']} - Sayfa {source_info['page_number']} (Skor: {score:.3f})"
                citations.append(citation)
            
            response_time = time.time() - start_time
            
            # Calculate confidence score based on relevance scores
            confidence_score = np.mean(relevance_scores) if relevance_scores else 0.0
            
            # Update performance stats
            self.performance_stats['total_queries'] += 1
            self.performance_stats['successful_responses'] += 1
            self.performance_stats['average_response_time'] = (
                (self.performance_stats['average_response_time'] * (self.performance_stats['total_queries'] - 1) + response_time) /
                self.performance_stats['total_queries']
            )
            self.performance_stats['average_confidence'] = (
                (self.performance_stats['average_confidence'] * (self.performance_stats['total_queries'] - 1) + confidence_score) /
                self.performance_stats['total_queries']
            )
            
            response = EnhancedRAGResponse(
                query=question,
                answer=answer,
                sources=sources,
                relevance_scores=relevance_scores,
                response_time=response_time,
                model_used=self.model_name,
                confidence_score=float(confidence_score),
                citations=citations
            )
            
            logger.info(f"✅ Query processed in {response_time:.2f}s (Confidence: {confidence_score:.3f})")
            return response
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            self.performance_stats['failed_responses'] += 1
            
            # Return error response
            return EnhancedRAGResponse(
                query=question,
                answer=f"Üzgünüm, sorunuzu işlerken bir hata oluştu: {str(e)}",
                sources=[],
                relevance_scores=[],
                response_time=time.time() - start_time,
                model_used=self.model_name,
                confidence_score=0.0,
                citations=[]
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed pipeline statistics"""
        vector_stats = self.faiss_store.get_statistics()
        
        return {
            'pipeline_stats': self.performance_stats,
            'vector_store_stats': vector_stats,
            'model_info': {
                'name': self.model_name,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens
            },
            'total_chunks': vector_stats['total_chunks'],
            'chunk_types': vector_stats['chunk_types']
        }
    
    def interactive_chat(self):
        """Enhanced interactive chat interface"""
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
                    stats = self.get_statistics()
                    print(f"\n📊 Pipeline İstatistikleri:")
                    print(f"   🔢 Toplam sorgu: {stats['pipeline_stats']['total_queries']}")
                    print(f"   ⏱️ Ortalama süre: {stats['pipeline_stats']['average_response_time']:.2f}s")
                    print(f"   ✅ Başarılı: {stats['pipeline_stats']['successful_responses']}")
                    print(f"   ❌ Başarısız: {stats['pipeline_stats']['failed_responses']}")
                    print(f"   🎯 Ortalama güven: {stats['pipeline_stats']['average_confidence']:.3f}")
                    print(f"   📚 Toplam chunk: {stats['total_chunks']}")
                    print(f"   🤖 Model: {stats['model_info']['name']}")
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
                
                if response.citations:
                    print(f"\n📚 Kaynaklar:")
                    for citation in response.citations:
                        print(f"   {citation}")
                
                print("\n" + "="*50)
                
            except KeyboardInterrupt:
                print("\n👋 Görüşürüz!")
                break
            except Exception as e:
                print(f"❌ Hata: {e}")

def main():
    """Test Groq RAG Pipeline"""
    print("🚀 Groq-Powered Turkish RAG Pipeline Test")
    print("=" * 60)
    
    # API key check
    api_key = "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"
    
    if not api_key:
        print("❌ Groq API key not found!")
        print("💡 Set GROQ_API_KEY environment variable or provide key directly")
        return
    
    try:
        # Initialize pipeline
        pipeline = GroqRAGPipeline(
            groq_api_key=api_key,
            model_name="llama-3.1-8b-instant",  # Fast and capable
            temperature=0.1,  # Low for factual responses
            max_tokens=1024
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
            response = pipeline.query(query)
            print(f"   🤖 {response.answer[:150]}...")
            print(f"   📊 Güven: {response.confidence_score:.3f} | Kaynak: {len(response.sources)} | Süre: {response.response_time:.2f}s")
        
        # Show statistics
        stats = pipeline.get_statistics()
        print(f"\n📊 Pipeline İstatistikleri:")
        print(f"   Toplam sorgu: {stats['pipeline_stats']['total_queries']}")
        print(f"   Ortalama süre: {stats['pipeline_stats']['average_response_time']:.2f}s")
        print(f"   Ortalama güven: {stats['pipeline_stats']['average_confidence']:.3f}")
        print(f"   Model: {stats['model_info']['name']}")
        
        # Interactive mode
        print(f"\n🎮 İnteraktif moda geçmek için 'i' yazın, çıkmak için Enter'a basın")
        choice = input().strip().lower()
        
        if choice == 'i':
            pipeline.interactive_chat()
        
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        print("💡 Önce integrated_analyzer.py çalıştırarak analiz dosyaları oluşturun")

if __name__ == "__main__":
    main() 