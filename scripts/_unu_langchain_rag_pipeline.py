"""
🔗 LangChain RAG Pipeline
========================
Retrieval-Augmented Generation system for Turkish document Q&A.
Integrates with FAISS vector store and supports multiple LLM providers.

Features:
- RAG pipeline with FAISS vector store
- Turkish language support
- Multiple LLM providers (OpenAI, Ollama, Hugging Face)
- Context-aware response generation
- Source citation and relevance scoring
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore
from langchain.embeddings.base import Embeddings
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

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
class RAGResponse:
    """RAG response with metadata"""
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    relevance_scores: List[float]
    response_time: float
    model_used: str

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
        # Initialize embeddings
        self._embeddings = CustomFAISSEmbeddings(faiss_store.model_name)
    
    @property
    def embeddings(self) -> Embeddings:
        """Get embeddings"""
        return self._embeddings
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None, **kwargs) -> List[str]:
        """Add texts to the vector store"""
        # This would require extending our FAISS store
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

class SimpleLLM(LLM):
    """Simple LLM wrapper for testing without external API"""
    
    model_name: str = "simple_turkish_llm"
    
    def __init__(self, model_name: str = "simple_turkish_llm"):
        super().__init__()
        self.model_name = model_name
    
    @property
    def _llm_type(self) -> str:
        return "simple_turkish_llm"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        """Generate response based on context"""
        # Simple rule-based response generation for testing
        if "bütçe" in prompt.lower():
            return "Bütçe dengesi ile ilgili sağlanan bilgilere göre, haziran ayı verilerinde önemli gelişmeler bulunmaktadır. Detaylar için kaynak dokümanları inceleyebilirsiniz."
        elif "enflasyon" in prompt.lower():
            return "Enflasyon verileri ABD ve Türkiye ekonomisi açısından önemli göstergeler sunmaktadır. Sağlanan kaynaklarda yıllık ve aylık enflasyon oranları detaylandırılmıştır."
        elif "grafik" in prompt.lower() or "chart" in prompt.lower():
            return "Grafik analizine göre, pie chart formatında sunulan veriler ekonomik göstergeleri içermektedir. Detaylı analiz için kaynak sayfa numaralarını kontrol edebilirsiniz."
        else:
            return "Sağlanan kaynaklara göre, sorunuzla ilgili bilgiler bulunmaktadır. Daha detaylı bilgi için kaynak dokümanları inceleyebilirsiniz."

class TurkishRAGPipeline:
    """Turkish RAG Pipeline with FAISS vector store"""
    
    def __init__(self, 
                 vector_store_path: str = "vector_store",
                 llm_provider: str = "simple",
                 llm_config: Optional[Dict[str, Any]] = None):
        """
        Initialize Turkish RAG Pipeline
        
        Args:
            vector_store_path: Path to FAISS vector store
            llm_provider: LLM provider ('simple', 'openai', 'ollama', 'huggingface')
            llm_config: LLM configuration parameters
        """
        self.vector_store_path = vector_store_path
        self.llm_provider = llm_provider
        self.llm_config = llm_config or {}
        
        # Initialize FAISS vector store
        logger.info("🔄 Loading FAISS vector store...")
        self.faiss_store = FAISSVectorStore(vector_store_path=vector_store_path)
        
        # Try to load existing vector store
        if not self.faiss_store.load_vector_store():
            logger.warning("⚠️ No existing vector store found. Creating new one from analysis files...")
            
            # Try to create vector store from existing analysis files
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
        
        # Wrap FAISS store for LangChain
        self.vector_store = CustomFAISSVectorStore(self.faiss_store)
        
        # Initialize LLM
        self.llm = self._init_llm()
        
        # Create Turkish RAG prompt
        self.prompt_template = self._create_turkish_prompt()
        
        # Initialize RAG chain
        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
        
        # Performance tracking
        self.performance_stats = {
            'total_queries': 0,
            'average_response_time': 0,
            'successful_responses': 0,
            'failed_responses': 0
        }
        
        logger.info("🚀 Turkish RAG Pipeline initialized successfully")
    
    def _init_llm(self) -> LLM:
        """Initialize LLM based on provider"""
        if self.llm_provider == "simple":
            return SimpleLLM()
        elif self.llm_provider == "openai":
            try:
                from langchain.llms import OpenAI
                api_key = self.llm_config.get('api_key') or os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                return OpenAI(api_key=api_key, **self.llm_config)
            except ImportError:
                raise ImportError("Install langchain-openai: pip install langchain-openai")
        elif self.llm_provider == "ollama":
            try:
                from langchain.llms import Ollama
                model = self.llm_config.get('model', 'llama2')
                return Ollama(model=model, **self.llm_config)
            except ImportError:
                raise ImportError("Install langchain-ollama: pip install langchain-ollama")
        elif self.llm_provider == "huggingface":
            try:
                from langchain.llms import HuggingFacePipeline
                model_name = self.llm_config.get('model_name', 'microsoft/DialoGPT-medium')
                return HuggingFacePipeline.from_model_id(
                    model_id=model_name,
                    task="text-generation",
                    **self.llm_config
                )
            except ImportError:
                raise ImportError("Install transformers: pip install transformers")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def _create_turkish_prompt(self) -> PromptTemplate:
        """Create Turkish RAG prompt template"""
        template = """
Türkçe PDF dokümanlardaki bilgileri kullanarak soruyu yanıtla.

Bağlam:
{context}

Soru: {question}

Yanıt Kuralları:
1. Sadece verilen bağlamdaki bilgileri kullan
2. Türkçe olarak yanıtla
3. Eğer bağlamda yeterli bilgi yoksa, bunu belirt
4. Kaynak sayfa numaralarını belirt
5. Grafikler ve tablolardan elde edilen bilgileri dahil et

Yanıt:
"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def query(self, question: str, k: int = 5) -> RAGResponse:
        """
        Process a query through the RAG pipeline
        
        Args:
            question: User question in Turkish
            k: Number of relevant chunks to retrieve
            
        Returns:
            RAGResponse with answer and metadata
        """
        logger.info(f"🔍 Processing query: {question}")
        start_time = time.time()
        
        try:
            # Update retriever with k parameter
            self.rag_chain.retriever.search_kwargs = {"k": k}
            
            # Run RAG chain
            result = self.rag_chain({"query": question})
            
            # Extract answer and sources
            answer = result["result"]
            source_documents = result["source_documents"]
            
            # Prepare sources and scores
            sources = []
            relevance_scores = []
            
            for doc in source_documents:
                source_info = {
                    'text': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    'source': doc.metadata.get('source', 'unknown'),
                    'page_number': doc.metadata.get('page_number', 0),
                    'chunk_type': doc.metadata.get('chunk_type', 'text'),
                    'rank': doc.metadata.get('rank', 0)
                }
                sources.append(source_info)
                relevance_scores.append(doc.metadata.get('score', 0.0))
            
            response_time = time.time() - start_time
            
            # Update performance stats
            self.performance_stats['total_queries'] += 1
            self.performance_stats['successful_responses'] += 1
            self.performance_stats['average_response_time'] = int(
                (self.performance_stats['average_response_time'] * (self.performance_stats['total_queries'] - 1) + response_time) /
                self.performance_stats['total_queries']
            )
            
            response = RAGResponse(
                query=question,
                answer=answer,
                sources=sources,
                relevance_scores=relevance_scores,
                response_time=response_time,
                model_used=self.llm_provider
            )
            
            logger.info(f"✅ Query processed in {response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            self.performance_stats['failed_responses'] += 1
            
            # Return error response
            return RAGResponse(
                query=question,
                answer=f"Üzgünüm, sorunuzu işlerken bir hata oluştu: {str(e)}",
                sources=[],
                relevance_scores=[],
                response_time=time.time() - start_time,
                model_used=self.llm_provider
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        vector_stats = self.faiss_store.get_statistics()
        
        return {
            'pipeline_stats': self.performance_stats,
            'vector_store_stats': vector_stats,
            'llm_provider': self.llm_provider,
            'total_chunks': vector_stats['total_chunks'],
            'chunk_types': vector_stats['chunk_types']
        }
    
    def interactive_chat(self):
        """Interactive chat interface"""
        print("🤖 Turkish RAG Chat Interface")
        print("=" * 50)
        print("Türkçe sorularınızı yazın (çıkmak için 'quit' yazın)")
        print()
        
        while True:
            try:
                question = input("📝 Soru: ").strip()
                
                if question.lower() in ['quit', 'exit', 'çıkış', 'q']:
                    print("👋 Görüşürüz!")
                    break
                
                if not question:
                    continue
                
                print("🔄 İşleniyor...")
                response = self.query(question)
                
                print(f"\n🤖 Yanıt: {response.answer}")
                print(f"⏱️ Süre: {response.response_time:.2f}s")
                
                if response.sources:
                    print(f"\n📚 Kaynaklar ({len(response.sources)}):")
                    for i, source in enumerate(response.sources, 1):
                        score = response.relevance_scores[i-1] if i-1 < len(response.relevance_scores) else 0
                        print(f"  {i}. {source['source']} (Sayfa {source['page_number']}) - Score: {score:.3f}")
                        print(f"     {source['text']}")
                
                print("\n" + "="*50)
                
            except KeyboardInterrupt:
                print("\n👋 Görüşürüz!")
                break
            except Exception as e:
                print(f"❌ Hata: {e}")

def main():
    """Test Turkish RAG Pipeline"""
    print("🚀 Turkish RAG Pipeline Test")
    print("=" * 50)
    
    try:
        # Initialize pipeline
        pipeline = TurkishRAGPipeline()
        
        # Test queries
        test_queries = [
            "Bütçe dengesi hakkında ne biliyorsun?",
            "Enflasyon oranları nasıl?",
            "Grafiklerde hangi bilgiler var?",
            "Ekonomik göstergeler neler?",
            "Türkiye'nin ekonomik durumu nasıl?"
        ]
        
        print("📋 Test Sorular:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. {query}")
            response = pipeline.query(query)
            print(f"   🤖 {response.answer}")
            print(f"   📊 Kaynak sayısı: {len(response.sources)}")
            print(f"   ⏱️ Süre: {response.response_time:.2f}s")
        
        # Show statistics
        stats = pipeline.get_statistics()
        print(f"\n📊 Pipeline İstatistikleri:")
        print(f"   Toplam sorgu: {stats['pipeline_stats']['total_queries']}")
        print(f"   Ortalama süre: {stats['pipeline_stats']['average_response_time']:.2f}s")
        print(f"   Başarılı: {stats['pipeline_stats']['successful_responses']}")
        print(f"   Toplam chunk: {stats['total_chunks']}")
        
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