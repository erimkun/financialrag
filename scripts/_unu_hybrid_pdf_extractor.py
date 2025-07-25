import pdfplumber
import pdf2image
from pathlib import Path
import json
from PIL import Image
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Dict, List, Optional, Tuple, Any
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridPDFExtractor:
    """
    Hybrid PDF Extraction System - Context7 Best Practice
    Çoklu araç kullanarak cross-validation ve consensus-based extraction
    """
    
    def __init__(self, pdf_path: str, output_dir: str = "extracted_data"):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Performance metrics
        self.performance_stats = {
            'pdfplumber': {'time': 0.0, 'success': 0, 'errors': 0},
            'pdf2image': {'time': 0.0, 'success': 0, 'errors': 0},
            'alternative': {'time': 0.0, 'success': 0, 'errors': 0}
        }
        
        logger.info(f"🚀 Hybrid PDF Extractor başlatıldı: {self.pdf_path}")
    
    def extract_text_pdfplumber(self) -> List[Dict]:
        """pdfplumber ile metin çıkarımı"""
        start_time = time.time()
        try:
            text_data = []
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    text_data.append({
                        "sayfa": i + 1,
                        "metin": text,
                        "paragraflar": [p.strip() for p in text.split('\n') if p.strip()],
                        "kaynak": "pdfplumber"
                    })
            
            self.performance_stats['pdfplumber']['time'] = time.time() - start_time
            self.performance_stats['pdfplumber']['success'] += 1
            logger.info(f"✅ pdfplumber metin çıkarımı: {len(text_data)} sayfa")
            return text_data
            
        except Exception as e:
            self.performance_stats['pdfplumber']['errors'] += 1
            logger.error(f"❌ pdfplumber hata: {e}")
            return []
    
    def extract_text_alternative(self) -> List[Dict]:
        """Alternatif metin çıkarımı (pdfplumber ile farklı yöntem)"""
        start_time = time.time()
        try:
            text_data = []
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # Alternatif: karakterleri de çıkar
                    text = page.extract_text() or ""
                    chars = page.chars
                    
                    # Karakterlerden ek bilgi çıkar
                    if chars:
                        font_sizes = [c.get('size', 0) for c in chars if c.get('size')]
                        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
                    else:
                        avg_font_size = 12
                    
                    text_data.append({
                        "sayfa": i + 1,
                        "metin": text,
                        "paragraflar": [p.strip() for p in text.split('\n') if p.strip()],
                        "ortalama_font_boyutu": avg_font_size,
                        "kaynak": "pdfplumber_alternative"
                    })
            
            self.performance_stats['alternative']['time'] = time.time() - start_time
            self.performance_stats['alternative']['success'] += 1
            logger.info(f"✅ Alternatif metin çıkarımı: {len(text_data)} sayfa")
            return text_data
            
        except Exception as e:
            self.performance_stats['alternative']['errors'] += 1
            logger.error(f"❌ Alternatif metin hatası: {e}")
            return []
    
    def extract_tables_pdfplumber(self) -> List[Dict]:
        """pdfplumber ile tablo çıkarımı"""
        try:
            tables_data = []
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    for j, table in enumerate(tables):
                        if table:
                            tables_data.append({
                                "sayfa": i + 1,
                                "tablo_id": j + 1,
                                "data": {"rows": table},
                                "kaynak": "pdfplumber"
                            })
            
            logger.info(f"✅ pdfplumber tablo çıkarımı: {len(tables_data)} tablo")
            return tables_data
            
        except Exception as e:
            logger.error(f"❌ pdfplumber tablo hatası: {e}")
            return []
    
    def extract_images_pdf2image(self) -> List[Dict]:
        """pdf2image + poppler ile görsel çıkarımı"""
        start_time = time.time()
        try:
            images_data = []
            # PDF'i yüksek çözünürlükte görsele çevir
            pages = pdf2image.convert_from_path(
                str(self.pdf_path),  # Path'i string'e çevir
                dpi=300,  # Yüksek kalite
                fmt='PNG'
            )
            
            for page_num, page_image in enumerate(pages):
                img_path = self.output_dir / f"page_{page_num + 1}_hq.png"
                page_image.save(img_path, optimize=True)
                
                images_data.append({
                    "sayfa": page_num + 1,
                    "görsel_path": str(img_path),
                    "çözünürlük": "300dpi",
                    "kaynak": "pdf2image"
                })
            
            self.performance_stats['pdf2image']['time'] = time.time() - start_time
            self.performance_stats['pdf2image']['success'] += 1
            logger.info(f"✅ pdf2image görsel çıkarımı: {len(images_data)} görsel")
            return images_data
            
        except Exception as e:
            self.performance_stats['pdf2image']['errors'] += 1
            logger.error(f"❌ pdf2image hata: {e}")
            return []
    
    def extract_images_pdfplumber(self) -> List[Dict]:
        """pdfplumber ile görsel çıkarımı (fallback)"""
        try:
            images_data = []
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    img_path = self.output_dir / f"page_{page_num + 1}_standard.png"
                    page_img = page.to_image(resolution=150)
                    page_img.save(img_path)
                    
                    images_data.append({
                        "sayfa": page_num + 1,
                        "görsel_path": str(img_path),
                        "çözünürlük": "150dpi",
                        "kaynak": "pdfplumber"
                    })
            
            logger.info(f"✅ pdfplumber görsel çıkarımı: {len(images_data)} görsel")
            return images_data
            
        except Exception as e:
            logger.error(f"❌ pdfplumber görsel hatası: {e}")
            return []
    
    def consensus_text_extraction(self, texts_pdfplumber: List[Dict], texts_alternative: List[Dict]) -> List[Dict]:
        """Cross-validation ile metin consensus"""
        consensus_texts = []
        
        for i in range(max(len(texts_pdfplumber), len(texts_alternative))):
            page_num = i + 1
            
            # Her iki kaynaktan da veri al
            text_plumber = texts_pdfplumber[i] if i < len(texts_pdfplumber) else None
            text_alternative = texts_alternative[i] if i < len(texts_alternative) else None
            
            if text_plumber and text_alternative:
                # İki kaynağı karşılaştır
                plumber_text = text_plumber.get('metin', '')
                alternative_text = text_alternative.get('metin', '')
                
                # Uzun olan metni seç (genellikle daha doğru)
                if len(plumber_text) > len(alternative_text):
                    final_text = text_plumber.copy()
                    final_text['confidence'] = 'high'
                    final_text['validation'] = 'both_sources'
                else:
                    final_text = text_alternative.copy()
                    final_text['confidence'] = 'high'
                    final_text['validation'] = 'both_sources'
                    
            elif text_plumber:
                final_text = text_plumber.copy()
                final_text['confidence'] = 'medium'
                final_text['validation'] = 'pdfplumber_only'
                
            elif text_alternative:
                final_text = text_alternative.copy()
                final_text['confidence'] = 'medium'
                final_text['validation'] = 'alternative_only'
                
            else:
                final_text = {
                    "sayfa": page_num,
                    "metin": "",
                    "paragraflar": [],
                    "confidence": 'low',
                    "validation": 'no_source'
                }
            
            consensus_texts.append(final_text)
        
        logger.info(f"🔄 Consensus metin çıkarımı: {len(consensus_texts)} sayfa")
        return consensus_texts
    
    def extract_titles_from_text(self, text_data: List[Dict]) -> Dict[int, str]:
        """Metinden başlık çıkarımı"""
        titles = {}
        
        for page_data in text_data:
            page_num = page_data['sayfa']
            paragraphs = page_data.get('paragraflar', [])
            
            # Başlık heuristics
            for para in paragraphs:
                if (len(para) < 100 and 
                    len(para) > 10 and 
                    para[0].isupper() and
                    not para.endswith('.') and
                    not para.startswith('•') and
                    not para.isdigit() and
                    'tablo' not in para.lower() and
                    'grafik' not in para.lower()):
                    titles[page_num] = para
                    break
            
            if page_num not in titles:
                titles[page_num] = f"Sayfa {page_num}"
        
        return titles
    
    def parallel_extraction(self) -> Dict[str, Any]:
        """Parallel processing ile tüm çıkarım işlemlerini yap"""
        logger.info("🔄 Parallel extraction başlatılıyor...")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Parallel tasks
            futures = {
                'text_pdfplumber': executor.submit(self.extract_text_pdfplumber),
                'text_alternative': executor.submit(self.extract_text_alternative),
                'tables': executor.submit(self.extract_tables_pdfplumber),
                'images_pdf2image': executor.submit(self.extract_images_pdf2image),
            }
            
            # Sonuçları topla
            for task_name, future in futures.items():
                try:
                    results[task_name] = future.result(timeout=30)
                except Exception as e:
                    logger.error(f"❌ {task_name} task hatası: {e}")
                    results[task_name] = []
        
        # Fallback: pdf2image başarısız olursa pdfplumber kullan
        if not results.get('images_pdf2image'):
            logger.info("🔄 pdf2image fallback: pdfplumber kullanılıyor...")
            results['images_pdfplumber'] = self.extract_images_pdfplumber()
        
        return results
    
    def build_final_output(self, extraction_results: Dict[str, Any]) -> List[Dict]:
        """Final JSON çıktısını oluştur"""
        
        # Consensus text extraction
        consensus_texts = self.consensus_text_extraction(
            extraction_results.get('text_pdfplumber', []),
            extraction_results.get('text_alternative', [])
        )
        
        # Başlık çıkarımı
        titles = self.extract_titles_from_text(consensus_texts)
        
        # Görseller (pdf2image öncelikli)
        images = extraction_results.get('images_pdf2image') or extraction_results.get('images_pdfplumber', [])
        
        # Sayfa bazlı birleştirme
        final_pages = []
        
        for page_data in consensus_texts:
            page_num = page_data['sayfa']
            
            # Sayfa için tabloları bul
            page_tables = [t for t in extraction_results.get('tables', []) if t['sayfa'] == page_num]
            
            # Sayfa için görseli bul
            page_images = [img for img in images if img['sayfa'] == page_num]
            
            final_page = {
                "sayfa": page_num,
                "başlık": titles.get(page_num, f"Sayfa {page_num}"),
                "paragraflar": page_data.get('paragraflar', []),
                "tablolar": [t['data'] for t in page_tables],
                "grafikler": [{
                    "başlık": titles.get(page_num, f"Sayfa {page_num}"),
                    "görsel_path": img['görsel_path'],
                    "çözünürlük": img.get('çözünürlük', 'unknown'),
                    "kaynak": img.get('kaynak', 'unknown'),
                    "çıkarılan_veri": None
                } for img in page_images],
                "confidence": page_data.get('confidence', 'unknown'),
                "validation": page_data.get('validation', 'unknown')
            }
            
            final_pages.append(final_page)
        
        return final_pages
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Performance raporu oluştur"""
        total_time = sum(stats['time'] for stats in self.performance_stats.values())
        
        report = {
            "toplam_süre": f"{total_time:.2f}s",
            "araç_performansı": {},
            "başarı_oranı": {},
            "öneriler": []
        }
        
        for tool, stats in self.performance_stats.items():
            report["araç_performansı"][tool] = {
                "süre": f"{stats['time']:.2f}s",
                "başarı": stats['success'],
                "hata": stats['errors']
            }
            
            success_rate = stats['success'] / (stats['success'] + stats['errors']) if (stats['success'] + stats['errors']) > 0 else 0
            report["başarı_oranı"][tool] = f"{success_rate:.1%}"
            
            if stats['errors'] > 0:
                report["öneriler"].append(f"{tool}: {stats['errors']} hata tespit edildi")
        
        return report
    
    def run_hybrid_extraction(self) -> Dict[str, Any]:
        """Ana hybrid extraction pipeline"""
        logger.info("🚀 Hybrid PDF Extraction başlatılıyor...")
        
        # Parallel extraction
        extraction_results = self.parallel_extraction()
        
        # Final output
        final_pages = self.build_final_output(extraction_results)
        
        # Performance report
        performance_report = self.generate_performance_report()
        
        # JSON çıktısı
        output_data = {
            "pdf_dosyası": str(self.pdf_path),
            "çıkarım_tarihi": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sayfa_sayısı": len(final_pages),
            "sayfalar": final_pages,
            "performans_raporu": performance_report,
            "hybrid_extraction": True
        }
        
        # Dosyaya kaydet
        output_file = self.output_dir / "hybrid_extracted_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Hybrid extraction tamamlandı: {output_file}")
        return output_data

# Ana çalıştırma
if __name__ == "__main__":
    pdf_path = "2025_07_16_Haziran Ayı Bütce Dengesi.pdf"
    
    print("🚀 Hybrid PDF Extraction System")
    print("=" * 50)
    
    extractor = HybridPDFExtractor(pdf_path)
    result = extractor.run_hybrid_extraction()
    
    print("\n📊 Özet:")
    print(f"📄 Sayfa sayısı: {result['sayfa_sayısı']}")
    print(f"⏱️ Toplam süre: {result['performans_raporu']['toplam_süre']}")
    print(f"🎯 Hybrid extraction: {result['hybrid_extraction']}")
    
    print("\n🔧 Araç Performansı:")
    for tool, perf in result['performans_raporu']['araç_performansı'].items():
        print(f"  {tool}: {perf['süre']} - Başarı: {perf['başarı']}, Hata: {perf['hata']}")
    
    print(f"\n✅ Çıktı: {extractor.output_dir}/hybrid_extracted_data.json")
    print(f"🖼️ Görseller: {extractor.output_dir}/ klasöründe") 