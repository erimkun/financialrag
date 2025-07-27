"""
🔧 Memory Optimized Groq RAG System
Lightweight version with memory optimizations
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from groq import Groq
import numpy as np

# Lightweight imports - avoid heavy ML libraries if possible
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from turkish_prompt_optimizer import TurkishPromptOptimizer, PromptContext, DocumentType, QueryType
    PROMPT_OPTIMIZER_AVAILABLE = True
except ImportError:
    PROMPT_OPTIMIZER_AVAILABLE = False

class MemoryOptimizedGroqRAG:
    """Memory optimized Groq RAG system"""
    
    def __init__(self, groq_api_key: str, specific_analysis_file: Optional[str] = None, lite_mode: bool = True):
        self.groq_client = Groq(api_key=groq_api_key)
        self.lite_mode = lite_mode
        
        # Initialize components based on availability and lite mode
        self.embedding_model = None
        self.faiss_index = None
        self.prompt_optimizer = None
        
        if not lite_mode and SENTENCE_TRANSFORMERS_AVAILABLE:
            print("🔄 Loading embedding model (may take time)...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Smaller model
            print("✅ Embedding model loaded")
        
        if PROMPT_OPTIMIZER_AVAILABLE:
            self.prompt_optimizer = TurkishPromptOptimizer()
        
        # Load data
        self.chunks = []
        self.specific_analysis_file = specific_analysis_file
        self._load_extracted_data_lightweight()
        
        # Create index only if not in lite mode
        if not lite_mode and self.chunks and FAISS_AVAILABLE and self.embedding_model:
            self._create_lightweight_faiss_index()
        
        # Performance tracking
        self.query_stats = {
            'total_queries': 0,
            'total_time': 0,
            'confidence_scores': []
        }
    
    def _load_extracted_data_lightweight(self):
        """Load data with memory optimizations"""
        try:
            # Get analysis directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            analysis_dir = os.path.join(project_root, "analysis_output")
            
            if not os.path.exists(analysis_dir):
                print(f"❌ Analysis directory not found: {analysis_dir}")
                return
            
            # Find latest analysis file
            analysis_files = [f for f in os.listdir(analysis_dir) if f.endswith('.json')]
            if not analysis_files:
                print(f"❌ No analysis files found")
                return
            
            latest_file = max(analysis_files, key=lambda f: os.path.getmtime(os.path.join(analysis_dir, f)))
            analysis_path = os.path.join(analysis_dir, latest_file)
            
            print(f"📄 Loading analysis from: {latest_file}")
            
            with open(analysis_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract only essential content
            self.chunks = []
            
            # Load chunks with size limit for memory optimization
            MAX_CHUNKS = 50  # Limit number of chunks
            MAX_CHUNK_SIZE = 800  # Limit chunk size
            chunk_count = 0
            
            # Get PDF content
            pdf_content = data.get('pdf_content', {})
            pages = pdf_content.get('pages', [])
            
            print(f"🔍 Found {len(pages)} pages in PDF content")
            
            # Add page content
            for page in pages[:5]:  # Limit to 5 pages
                if chunk_count >= MAX_CHUNKS:
                    break
                    
                # Get paragraphs from page
                paragraphs = page.get('paragraflar', [])
                if paragraphs:
                    # Combine paragraphs into chunks
                    page_text = ' '.join(paragraphs)
                    if page_text.strip():
                        # Split into smaller chunks if too long
                        if len(page_text) > MAX_CHUNK_SIZE:
                            text_chunks = self._split_text(page_text, MAX_CHUNK_SIZE)
                            for chunk_text in text_chunks:
                                if chunk_count >= MAX_CHUNKS:
                                    break
                                self.chunks.append({
                                    'content': chunk_text,
                                    'type': 'text',
                                    'page': page.get('sayfa', 0),
                                    'metadata': {'type': 'page_content'}
                                })
                                chunk_count += 1
                        else:
                            self.chunks.append({
                                'content': page_text,
                                'type': 'text', 
                                'page': page.get('sayfa', 0),
                                'metadata': {'type': 'page_content'}
                            })
                            chunk_count += 1
            
            # Add content from 'content' section if available
            content = data.get('content', {})
            
            # Add table data (limited)
            tables = content.get('tables', [])
            for i, table in enumerate(tables[:3]):  # Limit to 3 tables
                if chunk_count >= MAX_CHUNKS:
                    break
                if isinstance(table, dict):
                    table_text = json.dumps(table, ensure_ascii=False)[:MAX_CHUNK_SIZE]
                    self.chunks.append({
                        'content': table_text,
                        'type': 'table',
                        'page': i,
                        'metadata': {'type': 'table', 'table_id': i}
                    })
                    chunk_count += 1
            
            # Add chart analysis
            chart_analysis = data.get('chart_analysis', {})
            if chart_analysis:
                print(f"🔍 Found chart analysis with {len(chart_analysis)} items")
                for key, value in list(chart_analysis.items())[:5]:  # Limit to 5 chart items
                    if chunk_count >= MAX_CHUNKS:
                        break
                    if isinstance(value, dict):
                        # Extract text from chart analysis
                        chart_text_parts = []
                        if 'chart_type' in value:
                            chart_text_parts.append(f"Grafik türü: {value['chart_type']}")
                        if 'extracted_text' in value and value['extracted_text']:
                            text_list = value['extracted_text']
                            if isinstance(text_list, list):
                                chart_text_parts.extend(text_list[:10])  # Limit text elements
                        
                        if chart_text_parts:
                            chart_text = ' '.join(chart_text_parts)[:MAX_CHUNK_SIZE]
                            self.chunks.append({
                                'content': chart_text,
                                'type': 'chart',
                                'page': 0,
                                'metadata': {'type': 'chart_analysis', 'chart_key': key}
                            })
                            chunk_count += 1
            
            print(f"✅ Loaded {len(self.chunks)} chunks (memory optimized)")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def _split_text(self, text: str, max_size: int) -> List[str]:
        """Split text into chunks of maximum size"""
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > max_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_size = len(word)
                else:
                    # Single word longer than max_size
                    chunks.append(word[:max_size])
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _create_lightweight_faiss_index(self):
        """Create lightweight FAISS index"""
        try:
            print("🔄 Creating lightweight FAISS index...")
            
            # Use smaller batches to reduce memory usage
            batch_size = 10
            contents = [chunk['content'] for chunk in self.chunks]
            
            embeddings = []
            for i in range(0, len(contents), batch_size):
                batch = contents[i:i+batch_size]
                batch_embeddings = self.embedding_model.encode(batch, convert_to_numpy=True)
                embeddings.append(batch_embeddings)
                print(f"   Processed batch {i//batch_size + 1}/{(len(contents)-1)//batch_size + 1}")
            
            # Combine embeddings
            all_embeddings = np.vstack(embeddings)
            
            # Create FAISS index
            dimension = all_embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.faiss_index.add(all_embeddings.astype('float32'))
            
            print(f"✅ FAISS index created with {len(self.chunks)} vectors")
            
        except Exception as e:
            print(f"❌ Error creating FAISS index: {e}")
            self.faiss_index = None
    
    def search_simple(self, query: str, k: int = 3) -> List[Dict]:
        """Simple search without FAISS (keyword based)"""
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        scored_chunks = []
        for i, chunk in enumerate(self.chunks):
            content_lower = chunk['content'].lower()
            
            # Simple scoring based on term frequency
            score = 0
            for term in query_terms:
                score += content_lower.count(term)
            
            if score > 0:
                scored_chunks.append({
                    'chunk': chunk,
                    'score': score,
                    'rank': 0
                })
        
        # Sort by score and return top k
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # Assign ranks
        for i, item in enumerate(scored_chunks[:k]):
            item['rank'] = i + 1
        
        return scored_chunks[:k]
    
    def search_faiss(self, query: str, k: int = 3) -> List[Dict]:
        """FAISS-based search"""
        if not self.faiss_index or not self.embedding_model:
            return self.search_simple(query, k)
        
        try:
            # Encode query
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            
            # Search FAISS index
            scores, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.chunks):
                    results.append({
                        'chunk': self.chunks[idx],
                        'score': float(score),
                        'rank': i + 1
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ FAISS search error: {e}")
            return self.search_simple(query, k)
    
    def retrieve_and_generate(self, query: str, k: int = 3) -> str:
        """Generate response with retrieved context"""
        try:
            start_time = time.time()
            
            # Search for relevant chunks
            if self.lite_mode or not self.faiss_index:
                search_results = self.search_simple(query, k)
                search_method = "keyword"
            else:
                search_results = self.search_faiss(query, k)
                search_method = "faiss"
            
            search_time = time.time() - start_time
            
            if not search_results:
                return "Üzgünüm, sorunuzla ilgili bilgi bulamadım."
            
            # Prepare context
            context_parts = []
            for result in search_results:
                chunk = result['chunk']
                content = chunk['content'][:500]  # Limit context size
                context_parts.append(f"[{chunk['type']}] {content}")
            
            context = "\n\n".join(context_parts)
            
            # Create prompt
            if self.prompt_optimizer:
                # Use a simple method that exists
                prompt = f"""Aşağıdaki finansal belgelerden yararlanarak soruyu Türkçe olarak yanıtlayın.

Soru: {query}

Belgeler:
{context}

Yanıt:"""
            else:
                prompt = f"""Soru: {query}

Bağlam:
{context}

Lütfen yukarıdaki bağlamı kullanarak soruyu Türkçe olarak yanıtlayın."""
            
            # Generate response
            generation_start = time.time()
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            generation_time = time.time() - generation_start
            
            total_time = time.time() - start_time
            
            # Update stats
            self.query_stats['total_queries'] += 1
            self.query_stats['total_time'] += total_time
            
            answer = response.choices[0].message.content or "Yanıt alınamadı."
            
            print(f"📊 Query processed in {total_time:.2f}s (search: {search_time:.2f}s, generation: {generation_time:.2f}s)")
            print(f"🔍 Search method: {search_method}, found {len(search_results)} results")
            
            return answer
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"Bir hata oluştu: {str(e)}"
