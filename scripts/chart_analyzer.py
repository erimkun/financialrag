"""
📊 Chart Analyzer Module
=========================
Advanced chart detection and numerical data extraction from PDF images.
Supports bar charts, line charts, pie charts, and scatter plots.

Features:
- Chart type detection using OpenCV
- Numerical data extraction from axes and data points
- OCR integration for text recognition
- Integration with hybrid PDF extractor
- Turkish language support
"""

import cv2
import numpy as np
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Sequence
from pathlib import Path
import pytesseract
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ChartData:
    """Chart data structure"""
    chart_type: str
    title: Optional[str]
    x_axis_label: Optional[str]
    y_axis_label: Optional[str]
    data_points: List[Dict[str, Any]]
    confidence: float
    extracted_text: List[str]
    
@dataclass
class BoundingBox:
    """Bounding box for chart elements"""
    x: int
    y: int
    width: int
    height: int

class ChartAnalyzer:
    """Advanced chart analyzer with OpenCV and OCR"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize chart analyzer
        
        Args:
            tesseract_path: Path to Tesseract executable (optional)
        """
        self.performance_stats = {
            'chart_detection': {'time': 0, 'success': 0, 'errors': 0},
            'data_extraction': {'time': 0, 'success': 0, 'errors': 0},
            'ocr_processing': {'time': 0, 'success': 0, 'errors': 0}
        }
        
        # Configure Tesseract for Turkish
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # Default Tesseract path for Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
        # OCR configuration for Turkish
        self.ocr_config = r'--oem 3 --psm 6 -l tur+eng'
        
        # Chart detection parameters
        self.chart_types = {
            'bar_chart': self._detect_bar_chart,
            'line_chart': self._detect_line_chart,
            'pie_chart': self._detect_pie_chart,
            'scatter_plot': self._detect_scatter_plot
        }
        
        logger.info("🚀 Chart Analyzer başlatıldı")
    
    def analyze_image(self, image_path: str) -> Optional[ChartData]:
        """
        Analyze image for chart content
        
        Args:
            image_path: Path to image file
            
        Returns:
            ChartData object or None if no chart detected
        """
        try:
            start_time = time.time()
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"❌ Görsel yüklenemedi: {image_path}")
                return None
            
            logger.info(f"🔍 Görsel analiz ediliyor: {Path(image_path).name}")
            
            # Detect chart type
            chart_type, confidence = self._detect_chart_type(image)
            
            if chart_type is None:
                logger.info(f"📊 Grafik tespit edilemedi: {Path(image_path).name}")
                return None
            
            logger.info(f"📊 Grafik türü: {chart_type} (güven: {confidence:.2f})")
            
            # Extract chart data
            chart_data = self._extract_chart_data(image, chart_type)
            
            # Update performance stats
            elapsed_time = time.time() - start_time
            self.performance_stats['chart_detection']['time'] += int(elapsed_time)
            self.performance_stats['chart_detection']['success'] += 1
            
            logger.info(f"✅ Grafik analizi tamamlandı: {elapsed_time:.2f}s")
            
            return chart_data
            
        except Exception as e:
            logger.error(f"❌ Grafik analizi hatası: {str(e)}")
            self.performance_stats['chart_detection']['errors'] += 1
            return None
    
    def _detect_chart_type(self, image: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Detect chart type using OpenCV
        
        Args:
            image: OpenCV image array
            
        Returns:
            Tuple of (chart_type, confidence)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Test each chart type
            best_type = None
            best_confidence = 0.0
            
            for chart_type, detector in self.chart_types.items():
                confidence = detector(image, gray, edges, contours)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_type = chart_type
            
            # Minimum confidence threshold
            if best_confidence < 0.3:
                return None, 0.0
                
            return best_type, best_confidence
            
        except Exception as e:
            logger.error(f"❌ Grafik türü tespit hatası: {str(e)}")
            return None, 0.0
    
    def _detect_bar_chart(self, image: np.ndarray, gray: np.ndarray, 
                         edges: np.ndarray, contours: Sequence[np.ndarray]) -> float:
        """Detect bar chart patterns"""
        try:
            # Look for rectangular shapes (bars)
            rectangles = 0
            total_area = 0
            
            for contour in contours:
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's roughly rectangular
                if len(approx) == 4:
                    area = cv2.contourArea(contour)
                    if area > 100:  # Minimum area threshold
                        rectangles += 1
                        total_area += area
            
            # Calculate confidence based on number of rectangles
            if rectangles >= 3:
                return min(0.8, rectangles / 10.0)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_line_chart(self, image: np.ndarray, gray: np.ndarray, 
                          edges: np.ndarray, contours: Sequence[np.ndarray]) -> float:
        """Detect line chart patterns"""
        try:
            # Use HoughLines to detect lines
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                   minLineLength=50, maxLineGap=10)
            
            if lines is None:
                return 0.0
            
            # Look for connected line segments
            line_count = len(lines)
            
            # Calculate confidence based on line density
            if line_count >= 5:
                return min(0.7, line_count / 20.0)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_pie_chart(self, image: np.ndarray, gray: np.ndarray, 
                         edges: np.ndarray, contours: Sequence[np.ndarray]) -> float:
        """Detect pie chart patterns"""
        try:
            # Look for circular shapes
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                     param1=50, param2=30, minRadius=10, maxRadius=200)
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                if len(circles) >= 1:
                    return 0.8
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_scatter_plot(self, image: np.ndarray, gray: np.ndarray, 
                           edges: np.ndarray, contours: Sequence[np.ndarray]) -> float:
        """Detect scatter plot patterns"""
        try:
            # Look for small circular/dot patterns
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 10,
                                     param1=50, param2=30, minRadius=2, maxRadius=10)
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                if len(circles) >= 5:  # Multiple points
                    return min(0.7, len(circles) / 20.0)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _extract_chart_data(self, image: np.ndarray, chart_type: str) -> ChartData:
        """
        Extract numerical data from chart
        
        Args:
            image: OpenCV image array
            chart_type: Detected chart type
            
        Returns:
            ChartData object
        """
        try:
            start_time = time.time()
            
            # Extract text using OCR
            extracted_text = self._extract_text_ocr(image)
            
            # Extract title and axis labels
            title = self._extract_title(extracted_text)
            x_axis_label = self._extract_axis_label(extracted_text, 'x')
            y_axis_label = self._extract_axis_label(extracted_text, 'y')
            
            # Extract data points based on chart type
            if chart_type == 'bar_chart':
                data_points = self._extract_bar_data(image, extracted_text)
            elif chart_type == 'line_chart':
                data_points = self._extract_line_data(image, extracted_text)
            elif chart_type == 'pie_chart':
                data_points = self._extract_pie_data(image, extracted_text)
            else:
                data_points = self._extract_scatter_data(image, extracted_text)
            
            # Update performance stats
            elapsed_time = time.time() - start_time
            self.performance_stats['data_extraction']['time'] += int(elapsed_time)
            self.performance_stats['data_extraction']['success'] += 1
            
            return ChartData(
                chart_type=chart_type,
                title=title,
                x_axis_label=x_axis_label,
                y_axis_label=y_axis_label,
                data_points=data_points,
                confidence=0.8,  # Base confidence
                extracted_text=extracted_text
            )
            
        except Exception as e:
            logger.error(f"❌ Veri çıkarma hatası: {str(e)}")
            self.performance_stats['data_extraction']['errors'] += 1
            return ChartData(
                chart_type=chart_type,
                title=None,
                x_axis_label=None,
                y_axis_label=None,
                data_points=[],
                confidence=0.0,
                extracted_text=[]
            )
    
    def _extract_text_ocr(self, image: np.ndarray) -> List[str]:
        """Extract text using OCR"""
        try:
            start_time = time.time()
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get better text recognition
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Extract text
            text = pytesseract.image_to_string(thresh, config=self.ocr_config)
            
            # Clean and split text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Update performance stats
            elapsed_time = time.time() - start_time
            self.performance_stats['ocr_processing']['time'] += int(elapsed_time)
            self.performance_stats['ocr_processing']['success'] += 1
            
            logger.info(f"📝 OCR metin çıkarımı: {len(lines)} satır")
            
            return lines
            
        except Exception as e:
            logger.error(f"❌ OCR hatası: {str(e)}")
            self.performance_stats['ocr_processing']['errors'] += 1
            return []
    
    def _extract_title(self, text_lines: List[str]) -> Optional[str]:
        """Extract chart title from text"""
        if not text_lines:
            return None
        
        # Usually the first line or longest line is the title
        title_candidates = [line for line in text_lines if len(line) > 5]
        
        if title_candidates:
            return title_candidates[0]
        
        return None
    
    def _extract_axis_label(self, text_lines: List[str], axis: str) -> Optional[str]:
        """Extract axis label from text"""
        # Look for common axis label patterns
        axis_patterns = {
            'x': ['x', 'horizontal', 'yatay', 'zaman', 'time'],
            'y': ['y', 'vertical', 'dikey', 'değer', 'value', 'miktar']
        }
        
        patterns = axis_patterns.get(axis, [])
        
        for line in text_lines:
            line_lower = line.lower()
            for pattern in patterns:
                if pattern in line_lower:
                    return line
        
        return None
    
    def _extract_bar_data(self, image: np.ndarray, text_lines: List[str]) -> List[Dict[str, Any]]:
        """Extract data points from bar chart"""
        try:
            # Extract numerical values from text
            numbers = []
            for line in text_lines:
                # Find numbers in text
                found_numbers = re.findall(r'\d+(?:\.\d+)?', line)
                numbers.extend([float(num) for num in found_numbers])
            
            # Create data points
            data_points = []
            for i, value in enumerate(numbers):
                data_points.append({
                    'category': f'Bar {i+1}',
                    'value': value,
                    'type': 'bar'
                })
            
            return data_points
            
        except Exception as e:
            logger.error(f"❌ Bar veri çıkarma hatası: {str(e)}")
            return []
    
    def _extract_line_data(self, image: np.ndarray, text_lines: List[str]) -> List[Dict[str, Any]]:
        """Extract data points from line chart"""
        try:
            # Extract numerical values from text
            numbers = []
            for line in text_lines:
                found_numbers = re.findall(r'\d+(?:\.\d+)?', line)
                numbers.extend([float(num) for num in found_numbers])
            
            # Create data points (assuming x,y pairs)
            data_points = []
            for i in range(0, len(numbers)-1, 2):
                if i+1 < len(numbers):
                    data_points.append({
                        'x': numbers[i],
                        'y': numbers[i+1],
                        'type': 'line_point'
                    })
            
            return data_points
            
        except Exception as e:
            logger.error(f"❌ Line veri çıkarma hatası: {str(e)}")
            return []
    
    def _extract_pie_data(self, image: np.ndarray, text_lines: List[str]) -> List[Dict[str, Any]]:
        """Extract data points from pie chart"""
        try:
            # Extract percentages and labels
            data_points = []
            
            for line in text_lines:
                # Look for percentage patterns
                percentage_match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
                if percentage_match:
                    percentage = float(percentage_match.group(1))
                    label = line.replace(percentage_match.group(0), '').strip()
                    
                    data_points.append({
                        'label': label or f'Segment {len(data_points)+1}',
                        'percentage': percentage,
                        'type': 'pie_segment'
                    })
            
            return data_points
            
        except Exception as e:
            logger.error(f"❌ Pie veri çıkarma hatası: {str(e)}")
            return []
    
    def _extract_scatter_data(self, image: np.ndarray, text_lines: List[str]) -> List[Dict[str, Any]]:
        """Extract data points from scatter plot"""
        return self._extract_line_data(image, text_lines)  # Similar to line chart
    
    def analyze_batch(self, image_paths: List[str]) -> Dict[str, Optional[ChartData]]:
        """
        Analyze multiple images in parallel
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Dictionary mapping image paths to ChartData
        """
        logger.info(f"🔄 Batch analiz başlatılıyor: {len(image_paths)} görsel")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.analyze_image, path): path 
                for path in image_paths
            }
            
            # Collect results
            for future in futures:
                path = futures[future]
                try:
                    result = future.result()
                    results[path] = result
                except Exception as e:
                    logger.error(f"❌ Batch analiz hatası {path}: {str(e)}")
                    results[path] = None
        
        logger.info(f"✅ Batch analiz tamamlandı: {len(results)} sonuç")
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'performance_stats': self.performance_stats,
            'total_time': sum(
                stats['time'] for stats in self.performance_stats.values()
            ),
            'total_success': sum(
                stats['success'] for stats in self.performance_stats.values()
            ),
            'total_errors': sum(
                stats['errors'] for stats in self.performance_stats.values()
            )
        }

def main():
    """Test the chart analyzer"""
    print("🚀 Chart Analyzer Test")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = ChartAnalyzer()
    
    # Test with extracted images
    extracted_dir = Path("extracted_data")
    if not extracted_dir.exists():
        print("❌ extracted_data klasörü bulunamadı")
        print("💡 Önce hybrid_pdf_extractor.py çalıştırın")
        return
    
    # Find image files
    image_files = list(extracted_dir.glob("*.png")) + list(extracted_dir.glob("*.jpg"))
    
    if not image_files:
        print("❌ Analiz edilecek görsel bulunamadı")
        return
    
    print(f"📊 {len(image_files)} görsel analiz edilecek")
    
    # Analyze images
    results = analyzer.analyze_batch([str(path) for path in image_files])
    
    # Save results
    output_file = extracted_dir / "chart_analysis.json"
    chart_results = {}
    
    for path, chart_data in results.items():
        if chart_data:
            chart_results[path] = {
                'chart_type': chart_data.chart_type,
                'title': chart_data.title,
                'x_axis_label': chart_data.x_axis_label,
                'y_axis_label': chart_data.y_axis_label,
                'data_points': chart_data.data_points,
                'confidence': chart_data.confidence,
                'extracted_text': chart_data.extracted_text
            }
        else:
            chart_results[path] = None
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chart_results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n📊 Sonuçlar:")
    successful_analyses = sum(1 for result in results.values() if result is not None)
    print(f"✅ Başarılı analiz: {successful_analyses}/{len(results)}")
    
    # Print chart types found
    chart_types = {}
    for result in results.values():
        if result:
            chart_types[result.chart_type] = chart_types.get(result.chart_type, 0) + 1
    
    if chart_types:
        print(f"📈 Tespit edilen grafik türleri:")
        for chart_type, count in chart_types.items():
            print(f"  {chart_type}: {count}")
    
    # Performance stats
    stats = analyzer.get_performance_stats()
    print(f"\n🔧 Performans:")
    print(f"  Toplam süre: {stats['total_time']:.2f}s")
    print(f"  Başarı: {stats['total_success']}")
    print(f"  Hata: {stats['total_errors']}")
    
    print(f"\n✅ Çıktı: {output_file}")

if __name__ == "__main__":
    main() 