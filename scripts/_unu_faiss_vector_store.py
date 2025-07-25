"""
🗃️ FAISS Vector Store
====================
Local vector database for semantic search with Turkish embeddings support.
Integrates with hybrid PDF extractor and chart analyzer for RAG pipeline.

Features:
- FAISS local vector database
- Turkish sentence-transformers embeddings
- Content chunking for optimal retrieval
- Metadata storage for source tracking
- Semantic search capabilities
"""

import faiss
import numpy as np
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import logging
from sentence_transformers import SentenceTransformer
import time
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Document chunk with metadata"""
    id: str
    text: str
    source: str
    page_number: int
    chunk_type: str  # 'text', 'table', 'chart', 'ocr'
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

@dataclass
class SearchResult:
    """Search result with relevance score"""
    chunk: DocumentChunk
    score: float
    rank: int

class FAISSVectorStore:
    """FAISS-based vector store for semantic search"""
    
    def __init__(self, 
                 model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
                 index_type: str = "flat",
                 vector_store_path: str = "vector_store"):
        """
        Initialize FAISS vector store
        
        Args:
            model_name: Sentence transformer model name
            index_type: FAISS index type ('flat', 'ivf')
            vector_store_path: Path to store vector database
        """
        self.model_name = model_name
        self.index_type = index_type
        self.vector_store_path = Path(vector_store_path)
        self.vector_store_path.mkdir(exist_ok=True)
        
        # Initialize sentence transformer
        logger.info(f"🤖 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"✅ Model loaded, embedding dimension: {self.embedding_dim}")
        
        # Initialize FAISS index
        self._init_faiss_index()
        
        # Document storage
        self.chunks: List[DocumentChunk] = []
        self.chunk_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.performance_stats = {
            'embedding_time': 0,
            'indexing_time': 0,
            'search_time': 0,
            'chunks_processed': 0,
            'searches_performed': 0
        }
        
        logger.info("🚀 FAISS Vector Store initialized")
    
    def _init_faiss_index(self):
        """Initialize FAISS index based on type"""
        if self.index_type == "flat":
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        elif self.index_type == "ivf":
            # IVF index for larger datasets
            quantizer = faiss.IndexFlatIP(self.embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)  # 100 centroids
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
        
        logger.info(f"✅ FAISS index initialized: {self.index_type}")
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Find sentence boundary if possible
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end == -1:
                    sentence_end = text.rfind('!', start, end)
                if sentence_end == -1:
                    sentence_end = text.rfind('?', start, end)
                
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def _generate_chunk_id(self, text: str, source: str, page_number: int) -> str:
        """Generate unique chunk ID"""
        content = f"{source}_{page_number}_{text[:100]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def add_pdf_content(self, pdf_analysis: Dict[str, Any]):
        """
        Add PDF content to vector store
        
        Args:
            pdf_analysis: PDF analysis results from hybrid extractor
        """
        logger.info("📄 Adding PDF content to vector store")
        start_time = time.time()
        
        chunks_to_add = []
        filename = pdf_analysis.get('document_info', {}).get('filename', 'unknown')
        
        # Process text content
        if 'pdf_content' in pdf_analysis:
            for page in pdf_analysis['pdf_content']['pages']:
                page_num = page.get('sayfa', 0)
                
                # Process paragraphs
                for paragraph in page.get('paragraflar', []):
                    if paragraph.strip():
                        text_chunks = self._chunk_text(paragraph)
                        for chunk_text in text_chunks:
                            chunk_id = self._generate_chunk_id(chunk_text, filename, page_num)
                            chunk = DocumentChunk(
                                id=chunk_id,
                                text=chunk_text,
                                source=filename,
                                page_number=page_num,
                                chunk_type='text',
                                metadata={'paragraph': True}
                            )
                            chunks_to_add.append(chunk)
        
        # Process table content
        if 'pdf_content' in pdf_analysis and 'tables' in pdf_analysis['pdf_content']:
            for table in pdf_analysis['pdf_content']['tables']:
                page_num = table.get('sayfa', 0)
                table_text = json.dumps(table, ensure_ascii=False)
                
                chunk_id = self._generate_chunk_id(table_text, filename, page_num)
                chunk = DocumentChunk(
                    id=chunk_id,
                    text=table_text,
                    source=filename,
                    page_number=page_num,
                    chunk_type='table',
                    metadata={'table': True, 'table_data': table}
                )
                chunks_to_add.append(chunk)
        
        # Process chart content
        if 'chart_analysis' in pdf_analysis:
            for chart in pdf_analysis['chart_analysis']['charts']:
                page_num = chart.get('source_page', 0)
                
                # Chart title and labels
                chart_text_parts = []
                if chart.get('title'):
                    chart_text_parts.append(f"Başlık: {chart['title']}")
                if chart.get('x_axis_label'):
                    chart_text_parts.append(f"X Ekseni: {chart['x_axis_label']}")
                if chart.get('y_axis_label'):
                    chart_text_parts.append(f"Y Ekseni: {chart['y_axis_label']}")
                
                # Chart data points
                for point in chart.get('data_points', []):
                    if point.get('label'):
                        chart_text_parts.append(f"Veri: {point['label']}")
                
                # OCR extracted text
                for ocr_text in chart.get('extracted_text', []):
                    if ocr_text.strip():
                        chart_text_parts.append(f"OCR: {ocr_text}")
                
                if chart_text_parts:
                    chart_text = ' | '.join(chart_text_parts)
                    chunk_id = self._generate_chunk_id(chart_text, filename, page_num)
                    chunk = DocumentChunk(
                        id=chunk_id,
                        text=chart_text,
                        source=filename,
                        page_number=page_num,
                        chunk_type='chart',
                        metadata={'chart': True, 'chart_type': chart.get('chart_type'), 'chart_data': chart}
                    )
                    chunks_to_add.append(chunk)
        
        # Add chunks to vector store
        self._add_chunks(chunks_to_add)
        
        processing_time = time.time() - start_time
        self.performance_stats['chunks_processed'] += len(chunks_to_add)
        logger.info(f"✅ PDF content added: {len(chunks_to_add)} chunks in {processing_time:.2f}s")
    
    def _add_chunks(self, chunks: List[DocumentChunk]):
        """Add chunks to vector store with embeddings"""
        if not chunks:
            return
        
        logger.info(f"🔄 Generating embeddings for {len(chunks)} chunks")
        start_time = time.time()
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        
        embedding_time = time.time() - start_time
        self.performance_stats['embedding_time'] += int(embedding_time)
        
        # Add to FAISS index
        start_time = time.time()
        self.index.add(embeddings)  # type: ignore
        
        # Store chunks with embeddings
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
            self.chunks.append(chunk)
            # Don't store embedding in metadata (not JSON serializable)
            metadata = asdict(chunk)
            metadata.pop('embedding', None)
            self.chunk_metadata[chunk.id] = metadata
        
        indexing_time = time.time() - start_time
        self.performance_stats['indexing_time'] += int(indexing_time)
        
        logger.info(f"✅ Embeddings generated: {embedding_time:.2f}s, indexed: {indexing_time:.2f}s")
    
    def search(self, query: str, k: int = 10, filter_type: Optional[str] = None) -> List[SearchResult]:
        """
        Search for similar chunks
        
        Args:
            query: Search query
            k: Number of results to return
            filter_type: Filter by chunk type ('text', 'table', 'chart', 'ocr')
            
        Returns:
            List of search results
        """
        if self.index.ntotal == 0:
            logger.warning("⚠️ Vector store is empty")
            return []
        
        logger.info(f"🔍 Searching: '{query}' (k={k})")
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        
        # Search in FAISS index
        scores, indices = self.index.search(query_embedding, k)  # type: ignore
        
        # Prepare results
        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx >= len(self.chunks):
                continue
                
            chunk = self.chunks[idx]
            
            # Apply filter if specified
            if filter_type and chunk.chunk_type != filter_type:
                continue
            
            result = SearchResult(
                chunk=chunk,
                score=float(score),
                rank=rank
            )
            results.append(result)
        
        search_time = time.time() - start_time
        self.performance_stats['search_time'] += int(search_time)
        self.performance_stats['searches_performed'] += 1
        
        logger.info(f"✅ Search completed: {len(results)} results in {search_time:.2f}s")
        return results
    
    def save_vector_store(self):
        """Save vector store to disk"""
        logger.info("💾 Saving vector store to disk")
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.vector_store_path / "faiss_index.bin"))
        
        # Save chunks and metadata
        with open(self.vector_store_path / "chunks.pkl", 'wb') as f:
            pickle.dump(self.chunks, f)
        
        with open(self.vector_store_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(self.chunk_metadata, f, ensure_ascii=False, indent=2)
        
        # Save configuration
        config = {
            'model_name': self.model_name,
            'index_type': self.index_type,
            'embedding_dim': self.embedding_dim,
            'total_chunks': len(self.chunks),
            'performance_stats': self.performance_stats
        }
        
        with open(self.vector_store_path / "config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Vector store saved: {len(self.chunks)} chunks")
    
    def load_vector_store(self) -> bool:
        """Load vector store from disk"""
        try:
            logger.info("📂 Loading vector store from disk")
            
            # Load configuration
            config_path = self.vector_store_path / "config.json"
            if not config_path.exists():
                logger.warning("⚠️ No saved vector store found")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verify model compatibility
            if config['model_name'] != self.model_name:
                logger.warning(f"⚠️ Model mismatch: {config['model_name']} vs {self.model_name}")
                return False
            
            # Load FAISS index
            index_path = self.vector_store_path / "faiss_index.bin"
            if index_path.exists():
                self.index = faiss.read_index(str(index_path))
            else:
                logger.warning("⚠️ FAISS index not found")
                return False
            
            # Load chunks
            chunks_path = self.vector_store_path / "chunks.pkl"
            if chunks_path.exists():
                with open(chunks_path, 'rb') as f:
                    self.chunks = pickle.load(f)
            else:
                logger.warning("⚠️ Chunks file not found")
                return False
            
            # Load metadata
            metadata_path = self.vector_store_path / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.chunk_metadata = json.load(f)
            
            # Update performance stats
            self.performance_stats.update(config.get('performance_stats', {}))
            
            logger.info(f"✅ Vector store loaded: {len(self.chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load vector store: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_chunks': len(self.chunks),
            'chunk_types': {
                chunk_type: len([c for c in self.chunks if c.chunk_type == chunk_type])
                for chunk_type in ['text', 'table', 'chart', 'ocr']
            },
            'sources': list(set(chunk.source for chunk in self.chunks)),
            'performance_stats': self.performance_stats,
            'index_info': {
                'type': self.index_type,
                'dimension': self.embedding_dim,
                'total_vectors': self.index.ntotal
            }
        }

def main():
    """Test FAISS vector store functionality"""
    print("🚀 FAISS Vector Store Test")
    print("=" * 40)
    
    # Initialize vector store
    vector_store = FAISSVectorStore()
    
    # Test with existing analysis results
    analysis_dir = Path("analysis_output")
    if analysis_dir.exists():
        analysis_files = list(analysis_dir.glob("*_complete_analysis.json"))
        if analysis_files:
            print(f"📁 Found {len(analysis_files)} analysis files")
            
            # Load and process first analysis
            with open(analysis_files[0], 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            
            print(f"📄 Processing: {analysis['document_info']['filename']}")
            vector_store.add_pdf_content(analysis)
            
            # Test search
            test_queries = [
                "bütçe dengesi",
                "enflasyon",
                "grafik",
                "tablo",
                "ekonomik"
            ]
            
            for query in test_queries:
                results = vector_store.search(query, k=3)
                print(f"\n🔍 Query: '{query}' - {len(results)} results")
                for result in results:
                    print(f"  📄 {result.chunk.chunk_type}: {result.chunk.text[:100]}... (score: {result.score:.3f})")
            
            # Save vector store
            vector_store.save_vector_store()
            
            # Print statistics
            stats = vector_store.get_statistics()
            print(f"\n📊 Statistics:")
            print(f"  Total chunks: {stats['total_chunks']}")
            print(f"  Chunk types: {stats['chunk_types']}")
            print(f"  Performance: {stats['performance_stats']}")
            
        else:
            print("⚠️ No analysis files found")
    else:
        print("⚠️ No analysis_output directory found")

if __name__ == "__main__":
    main() 