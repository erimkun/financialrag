"""
🚀 Integrated PDF & Chart Analyzer
==================================
Complete PDF analysis system combining text, table, image, and chart extraction.
Integrates hybrid PDF extraction with advanced chart analysis.

Features:
- Hybrid PDF text/table extraction
- High-quality image extraction
- Chart type detection and analysis
- Numerical data extraction from charts
- Comprehensive JSON output
- Performance benchmarking
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import sys

# Import our modules
from hybrid_pdf_extractor import HybridPDFExtractor
from chart_analyzer import ChartAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

class IntegratedAnalyzer:
    """Integrated PDF and Chart Analyzer"""
    
    def __init__(self, output_dir: str = "analysis_output"):
        """
        Initialize integrated analyzer
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.chart_analyzer = ChartAnalyzer()
        
        # Performance tracking
        self.performance_stats = {
            'total_time': 0,
            'pdf_extraction_time': 0,
            'chart_analysis_time': 0,
            'integration_time': 0
        }
        
        logger.info("🚀 Integrated Analyzer başlatıldı")
    
    def analyze_pdf_complete(self, pdf_path: str) -> Dict[str, Any]:
        """
        Complete PDF analysis with charts
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Complete analysis results
        """
        start_time = time.time()
        
        try:
            print(f"🚀 Tam PDF Analizi: {Path(pdf_path).name}")
            print("=" * 60)
            
            # Step 1: Extract PDF content
            print("📄 1. PDF İçerik Çıkarımı...")
            pdf_start = time.time()
            
            # Create PDF extractor for this file
            pdf_extractor = HybridPDFExtractor(pdf_path)
            pdf_data = pdf_extractor.run_hybrid_extraction()
            
            pdf_time = time.time() - pdf_start
            self.performance_stats['pdf_extraction_time'] = int(pdf_time)
            
            if not pdf_data:
                logger.error("❌ PDF çıkarımı başarısız")
                return self._create_error_result("PDF extraction failed")
            
            print(f"✅ PDF çıkarımı tamamlandı: {pdf_time:.2f}s")
            
            # Step 2: Analyze charts in extracted images
            print("\n📊 2. Grafik Analizi...")
            chart_start = time.time()
            
            chart_results = self._analyze_extracted_charts(pdf_data)
            
            chart_time = time.time() - chart_start
            self.performance_stats['chart_analysis_time'] = int(chart_time)
            
            print(f"✅ Grafik analizi tamamlandı: {chart_time:.2f}s")
            
            # Step 3: Integrate results
            print("\n🔗 3. Sonuçları Birleştirme...")
            integration_start = time.time()
            
            integrated_result = self._integrate_results(pdf_data, chart_results)
            
            integration_time = time.time() - integration_start
            self.performance_stats['integration_time'] = int(integration_time)
            
            # Step 4: Save results
            output_file = self.output_dir / f"{Path(pdf_path).stem}_complete_analysis.json"
            self._save_results(integrated_result, output_file)
            
            # Calculate total time
            total_time = time.time() - start_time
            self.performance_stats['total_time'] = int(total_time)
            
            # Print summary
            self._print_summary(integrated_result, total_time)
            
            return integrated_result
            
        except Exception as e:
            logger.error(f"❌ Integrated analysis error: {str(e)}")
            return self._create_error_result(str(e))
    
    def _analyze_extracted_charts(self, pdf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze charts from extracted images"""
        try:
            # Get image paths from PDF data
            image_paths = []
            
            # Handle Turkish field names from hybrid extractor
            for page_data in pdf_data.get('sayfalar', []):
                for image_info in page_data.get('grafikler', []):
                    if 'görsel_path' in image_info:
                        image_paths.append(image_info['görsel_path'])
            
            if not image_paths:
                logger.info("📊 Analiz edilecek görsel bulunamadı")
                return {'charts': [], 'summary': {'total_charts': 0, 'chart_types': {}}}
            
            logger.info(f"📊 {len(image_paths)} görsel analiz ediliyor")
            
            # Analyze charts in parallel
            chart_results = self.chart_analyzer.analyze_batch(image_paths)
            
            # Process results
            charts = []
            chart_types = {}
            
            for image_path, chart_data in chart_results.items():
                if chart_data:
                    chart_info = {
                        'image_path': image_path,
                        'chart_type': chart_data.chart_type,
                        'title': chart_data.title,
                        'x_axis_label': chart_data.x_axis_label,
                        'y_axis_label': chart_data.y_axis_label,
                        'data_points': chart_data.data_points,
                        'confidence': chart_data.confidence,
                        'extracted_text': chart_data.extracted_text
                    }
                    charts.append(chart_info)
                    
                    # Count chart types
                    chart_type = chart_data.chart_type
                    chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
            
            return {
                'charts': charts,
                'summary': {
                    'total_charts': len(charts),
                    'chart_types': chart_types,
                    'analyzed_images': len(image_paths),
                    'successful_detections': len(charts)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Chart analysis error: {str(e)}")
            return {'charts': [], 'summary': {'error': str(e)}}
    
    def _integrate_results(self, pdf_data: Dict[str, Any], chart_results: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate PDF and chart analysis results"""
        try:
            # Create comprehensive result structure
            integrated_result = {
                'document_info': {
                    'filename': pdf_data.get('pdf_dosyası', 'unknown'),
                    'total_pages': pdf_data.get('sayfa_sayısı', 0),
                    'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'analysis_type': 'complete_pdf_chart_analysis'
                },
                'pdf_content': {
                    'pages': pdf_data.get('sayfalar', []),
                    'summary': {
                        'total_pages': pdf_data.get('sayfa_sayısı', 0),
                        'total_text_blocks': sum(len(page.get('paragraflar', [])) for page in pdf_data.get('sayfalar', [])),
                        'total_tables': sum(len(page.get('tablolar', [])) for page in pdf_data.get('sayfalar', [])),
                        'total_images': sum(len(page.get('grafikler', [])) for page in pdf_data.get('sayfalar', []))
                    }
                },
                'chart_analysis': chart_results,
                'performance_stats': self.performance_stats,
                'extraction_methods': pdf_data.get('extraction_methods', {}),
                'tools_used': {
                    'pdf_extraction': ['pdfplumber', 'pdf2image', 'consensus_algorithm'],
                    'chart_analysis': ['opencv', 'contour_detection', 'hough_transforms'],
                    'integration': ['hybrid_extraction', 'parallel_processing']
                }
            }
            
            # Add page-level chart associations
            self._associate_charts_with_pages(integrated_result)
            
            return integrated_result
            
        except Exception as e:
            logger.error(f"❌ Integration error: {str(e)}")
            return self._create_error_result(str(e))
    
    def _associate_charts_with_pages(self, result: Dict[str, Any]) -> None:
        """Associate charts with their source pages"""
        try:
            charts = result.get('chart_analysis', {}).get('charts', [])
            pages = result.get('pdf_content', {}).get('pages', [])
            
            # Create mapping from image paths to page numbers
            image_to_page = {}
            for page_idx, page_data in enumerate(pages):
                for image_info in page_data.get('grafikler', []):
                    if 'görsel_path' in image_info:
                        image_to_page[image_info['görsel_path']] = page_idx + 1
            
            # Add page associations to charts
            for chart in charts:
                image_path = chart.get('image_path', '')
                if image_path in image_to_page:
                    chart['source_page'] = image_to_page[image_path]
                else:
                    chart['source_page'] = None
            
            # Add chart counts to page summaries
            for page_idx, page_data in enumerate(pages):
                page_charts = [
                    chart for chart in charts 
                    if chart.get('source_page') == page_idx + 1
                ]
                page_data['chart_summary'] = {
                    'chart_count': len(page_charts),
                    'chart_types': [chart['chart_type'] for chart in page_charts]
                }
            
        except Exception as e:
            logger.error(f"❌ Chart association error: {str(e)}")
    
    def _save_results(self, results: Dict[str, Any], output_file: Path) -> None:
        """Save analysis results to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Sonuçlar kaydedildi: {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Sonuç kaydetme hatası: {str(e)}")
    
    def _print_summary(self, results: Dict[str, Any], total_time: float) -> None:
        """Print analysis summary"""
        try:
            print(f"\n📊 Analiz Özeti")
            print("=" * 40)
            
            # Document info
            doc_info = results.get('document_info', {})
            print(f"📄 Dosya: {doc_info.get('filename', 'unknown')}")
            print(f"📄 Sayfa sayısı: {doc_info.get('total_pages', 0)}")
            
            # PDF content summary
            pdf_summary = results.get('pdf_content', {}).get('summary', {})
            print(f"📝 Metin blokları: {pdf_summary.get('total_text_blocks', 0)}")
            print(f"📊 Tablolar: {pdf_summary.get('total_tables', 0)}")
            print(f"🖼️ Görseller: {pdf_summary.get('total_images', 0)}")
            
            # Chart analysis summary
            chart_summary = results.get('chart_analysis', {}).get('summary', {})
            print(f"📈 Tespit edilen grafikler: {chart_summary.get('total_charts', 0)}")
            
            chart_types = chart_summary.get('chart_types', {})
            if chart_types:
                print(f"📊 Grafik türleri:")
                for chart_type, count in chart_types.items():
                    print(f"  {chart_type}: {count}")
            
            # Performance stats
            print(f"\n⏱️ Performans:")
            print(f"  PDF çıkarımı: {self.performance_stats['pdf_extraction_time']:.2f}s")
            print(f"  Grafik analizi: {self.performance_stats['chart_analysis_time']:.2f}s")
            print(f"  Entegrasyon: {self.performance_stats['integration_time']:.2f}s")
            print(f"  Toplam süre: {total_time:.2f}s")
            
            # Output location
            print(f"\n✅ Detaylı sonuçlar: {self.output_dir}")
            
        except Exception as e:
            logger.error(f"❌ Summary print error: {str(e)}")
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            'error': True,
            'error_message': error_message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'performance_stats': self.performance_stats
        }
    
    def analyze_multiple_pdfs(self, pdf_paths: List[str]) -> Dict[str, Any]:
        """Analyze multiple PDFs in parallel"""
        logger.info(f"🔄 Batch PDF analizi: {len(pdf_paths)} dosya")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.analyze_pdf_complete, path): path 
                for path in pdf_paths
            }
            
            # Collect results
            for future in futures:
                path = futures[future]
                try:
                    result = future.result()
                    results[path] = result
                except Exception as e:
                    logger.error(f"❌ Batch analysis error {path}: {str(e)}")
                    results[path] = self._create_error_result(str(e))
        
        return results

def main():
    """Main function for testing"""
    print("🚀 Integrated PDF & Chart Analyzer")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = IntegratedAnalyzer()
    
    # Find PDF files in current directory
    pdf_files = list(Path(".").glob("*.pdf"))
    
    if not pdf_files:
        print("❌ Analiz edilecek PDF dosyası bulunamadı")
        print("💡 PDF dosyalarını proje klasörüne koyun")
        return
    
    print(f"📚 {len(pdf_files)} PDF dosyası bulundu")
    
    # Analyze first PDF (or all if you want)
    for pdf_file in pdf_files[:1]:  # Analyze first PDF only for demo
        print(f"\n🔍 Analiz ediliyor: {pdf_file}")
        result = analyzer.analyze_pdf_complete(str(pdf_file))
        
        if result.get('error'):
            print(f"❌ Analiz hatası: {result.get('error_message')}")
        else:
            print(f"✅ Analiz tamamlandı: {pdf_file}")
    
    print(f"\n📁 Tüm sonuçlar: {analyzer.output_dir}")

if __name__ == "__main__":
    main() 