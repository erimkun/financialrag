"""
🇹🇷 Turkish Prompt Optimizer
Advanced prompt engineering for Turkish language RAG systems
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class DocumentType(Enum):
    """Document types for context-aware prompting"""
    ECONOMIC_REPORT = "economic_report"
    BUDGET_ANALYSIS = "budget_analysis"
    FINANCIAL_BULLETIN = "financial_bulletin"
    GENERAL_DOCUMENT = "general_document"

class QueryType(Enum):
    """Query types for optimized responses"""
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    STATISTICAL = "statistical"
    EXPLANATORY = "explanatory"

@dataclass
class PromptContext:
    """Context information for prompt optimization"""
    document_type: DocumentType
    query_type: QueryType
    confidence_threshold: float = 0.7
    max_context_length: int = 2000
    include_citations: bool = True
    include_confidence: bool = True

class TurkishPromptOptimizer:
    """Advanced Turkish prompt optimization system"""
    
    def __init__(self):
        self.base_system_prompt = self._create_base_system_prompt()
        self.query_patterns = self._load_query_patterns()
        self.domain_vocabulary = self._load_domain_vocabulary()
        
    def _create_base_system_prompt(self) -> str:
        """Create optimized base system prompt for Turkish"""
        return """Sen Türkiye'deki ekonomi ve finans konularında uzman bir analistin. 
Türkçe PDF dokümanlarını analiz ederek kullanıcıların sorularına detaylı, doğru ve yararlı yanıtlar veriyorsun.

🎯 TEMEL PRENSİPLER:
• Sadece verilen bağlam bilgilerini kullan
• Türkçe dilbilgisi kurallarına uygun yaz
• Teknik terimleri açıkla
• Sayısal verileri net şekilde sun
• Kaynakları belirt

🔍 YANITLAMA STRATEJİSİ:
• Önce soruyu tam olarak anla
• Bağlamdan ilgili bilgileri seç
• Mantıklı sırayla organize et
• Emojiler ile görsel zenginlik kat
• Güven düzeyini belirt"""

    def _load_query_patterns(self) -> Dict[str, List[str]]:
        """Load Turkish query patterns for better understanding"""
        return {
            "budget": [
                "bütçe", "harcama", "gelir", "gider", "tahsis", "ödenek", 
                "mali", "finansal", "kaynak", "denge", "açık", "fazla"
            ],
            "inflation": [
                "enflasyon", "fiyat", "artış", "yükseliş", "tüfe", "üfe",
                "pahalılık", "hayat", "maliye", "merkez bankası"
            ],
            "economic": [
                "ekonomi", "büyüme", "gsyh", "üretim", "istihdam", "işsizlik",
                "yatırım", "ihracat", "ithalat", "dış ticaret"
            ],
            "financial": [
                "finans", "para", "kredi", "banka", "faiz", "kur", "döviz",
                "borsa", "hisse", "tahvil", "yatırım"
            ],
            "statistical": [
                "istatistik", "veri", "oran", "yüzde", "artış", "azalış",
                "değişim", "trend", "grafik", "tablo"
            ]
        }
    
    def _load_domain_vocabulary(self) -> Dict[str, str]:
        """Load domain-specific vocabulary with explanations"""
        return {
            "TÜFE": "Tüketici Fiyat Endeksi - Hanehalkının satın aldığı mal ve hizmetlerin fiyat değişimini ölçer",
            "ÜFE": "Üretici Fiyat Endeksi - Üreticilerin sattığı mal ve hizmetlerin fiyat değişimini ölçer",
            "GSYH": "Gayri Safi Yurt İçi Hasıla - Bir ülkenin belirli dönemde ürettiği mal ve hizmetlerin toplam değeri",
            "TCMB": "Türkiye Cumhuriyet Merkez Bankası - Türkiye'nin merkez bankası",
            "Bütçe Dengesi": "Devlet gelirlerinin giderlerden fazla (fazla) veya az (açık) olması durumu",
            "Cari Açık": "Bir ülkenin ithalatının ihracatından fazla olması durumu",
            "Enflasyon": "Genel fiyat seviyesindeki sürekli artış",
            "Deflasyon": "Genel fiyat seviyesindeki sürekli azalış"
        }
    
    def detect_query_type(self, question: str) -> QueryType:
        """Detect query type from question"""
        question_lower = question.lower()
        
        # Analytical queries
        if any(word in question_lower for word in ["neden", "nasıl", "sebep", "analiz", "değerlendirme"]):
            return QueryType.ANALYTICAL
            
        # Comparative queries
        if any(word in question_lower for word in ["karşılaştır", "fark", "arasında", "hangisi", "daha"]):
            return QueryType.COMPARATIVE
            
        # Statistical queries
        if any(word in question_lower for word in ["kaç", "ne kadar", "yüzde", "oran", "istatistik"]):
            return QueryType.STATISTICAL
            
        # Explanatory queries
        if any(word in question_lower for word in ["açıkla", "anlat", "nedir", "ne demek", "tanımla"]):
            return QueryType.EXPLANATORY
            
        # Default to factual
        return QueryType.FACTUAL
    
    def detect_document_type(self, context: str) -> DocumentType:
        """Detect document type from context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["bütçe", "mali", "gelir", "gider", "ödenek"]):
            return DocumentType.BUDGET_ANALYSIS
            
        if any(word in context_lower for word in ["ekonomi", "gsyh", "büyüme", "üretim"]):
            return DocumentType.ECONOMIC_REPORT
            
        if any(word in context_lower for word in ["günlük", "haftalık", "aylık", "bülten"]):
            return DocumentType.FINANCIAL_BULLETIN
            
        return DocumentType.GENERAL_DOCUMENT
    
    def create_optimized_prompt(self, question: str, context: str, 
                              prompt_context: Optional[PromptContext] = None) -> str:
        """Create optimized prompt based on context and query type"""
        
        if prompt_context is None:
            query_type = self.detect_query_type(question)
            doc_type = self.detect_document_type(context)
            prompt_context = PromptContext(
                document_type=doc_type,
                query_type=query_type
            )
        
        # Create context-aware instructions
        instructions = self._create_context_instructions(prompt_context)
        
        # Add domain-specific vocabulary if needed
        vocab_section = self._create_vocabulary_section(context)
        
        # Create the final prompt
        prompt = f"""{self.base_system_prompt}

{instructions}

{vocab_section}

BAĞLAM BİLGİLERİ:
{context}

KULLANICI SORUSU:
{question}

YANITLAMA KURALLARI:
✅ Türkçe dilbilgisi kurallarına uy
✅ Teknik terimleri açıkla
✅ Sayısal verileri vurgula
✅ Kaynakları belirt
✅ Güven düzeyini ekle
✅ Emojiler ile zenginleştir

YANIT:"""
        
        return prompt
    
    def _create_context_instructions(self, prompt_context: PromptContext) -> str:
        """Create context-specific instructions"""
        
        doc_instructions = {
            DocumentType.ECONOMIC_REPORT: "📊 Ekonomik göstergeleri analiz et ve trendleri açıkla",
            DocumentType.BUDGET_ANALYSIS: "💰 Bütçe kalemlerini detaylandır ve mali durumu değerlendir",
            DocumentType.FINANCIAL_BULLETIN: "📈 Güncel finansal gelişmeleri özetle ve önemli noktaları vurgula",
            DocumentType.GENERAL_DOCUMENT: "📋 Genel bilgileri düzenli şekilde sun"
        }
        
        query_instructions = {
            QueryType.FACTUAL: "🔍 Somut bilgileri net şekilde sun",
            QueryType.ANALYTICAL: "🧠 Sebep-sonuç ilişkilerini açıkla ve analiz et",
            QueryType.COMPARATIVE: "⚖️ Karşılaştırmaları tablo halinde göster",
            QueryType.STATISTICAL: "📊 Sayısal verileri vurgula ve yorumla",
            QueryType.EXPLANATORY: "💡 Kavramları basit dille açıkla"
        }
        
        return f"""🎯 ÖZEL TALİMATLAR:
{doc_instructions.get(prompt_context.document_type, "")}
{query_instructions.get(prompt_context.query_type, "")}"""
    
    def _create_vocabulary_section(self, context: str) -> str:
        """Create vocabulary section based on context"""
        relevant_terms = []
        context_lower = context.lower()
        
        for term, explanation in self.domain_vocabulary.items():
            if term.lower() in context_lower:
                relevant_terms.append(f"• **{term}**: {explanation}")
        
        if relevant_terms:
            return f"""📚 TEMEL KAVRAMLAR:
{chr(10).join(relevant_terms)}"""
        
        return ""
    
    def optimize_response_format(self, response: str, confidence: float) -> str:
        """Optimize response format with confidence and structure"""
        
        # Add confidence indicator
        confidence_emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
        confidence_text = f"{confidence_emoji} **Güven Düzeyi**: {confidence:.1%}"
        
        # Structure the response
        structured_response = f"""{response}

---
{confidence_text}

💡 **Not**: Bu yanıt sadece verilen bağlam bilgilerine dayanmaktadır."""
        
        return structured_response

def test_prompt_optimizer():
    """Test the prompt optimizer"""
    optimizer = TurkishPromptOptimizer()
    
    # Test cases
    test_cases = [
        {
            "question": "Türkiye'nin bütçe dengesi nasıl?",
            "context": "2025 yılı bütçe dengesi açığı 500 milyar TL olarak gerçekleşti. Gelirler 2.1 trilyon TL, giderler 2.6 trilyon TL oldu.",
            "expected_type": QueryType.FACTUAL
        },
        {
            "question": "Enflasyon neden yükseliyor?",
            "context": "TÜFE yıllık %65 arttı. Gıda fiyatları %80, enerji fiyatları %90 yükseldi.",
            "expected_type": QueryType.ANALYTICAL
        }
    ]
    
    print("🧪 Turkish Prompt Optimizer Test")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}:")
        print(f"Soru: {test_case['question']}")
        
        detected_type = optimizer.detect_query_type(test_case['question'])
        print(f"Tespit edilen tür: {detected_type}")
        
        optimized_prompt = optimizer.create_optimized_prompt(
            test_case['question'], 
            test_case['context']
        )
        
        print(f"Optimized prompt uzunluğu: {len(optimized_prompt)} karakter")
        print("-" * 30)

if __name__ == "__main__":
    test_prompt_optimizer() 