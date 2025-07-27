"""
🧪 Simple Chart Analysis Test
Test chart detection on existing images
"""

import os
import sys
import pytesseract
from chart_analyzer import ChartAnalyzer

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def test_chart_analysis():
    """Test chart analysis on extracted images"""
    
    print("🚀 Simple Chart Analysis Test")
    print("="*50)
    
    # Initialize analyzer
    try:
        analyzer = ChartAnalyzer()
        print("✅ ChartAnalyzer initialized")
    except Exception as e:
        print(f"❌ ChartAnalyzer init failed: {e}")
        return
    
    # Test images directory
    images_dir = "../extracted_data"
    
    if not os.path.exists(images_dir):
        print(f"❌ Directory not found: {images_dir}")
        return
    
    # Get image files
    image_files = [f for f in os.listdir(images_dir) if f.endswith('.png')]
    print(f"📸 Found {len(image_files)} images")
    
    if not image_files:
        print("❌ No PNG images found")
        return
    
    # Test first few images
    for i, image_file in enumerate(image_files[:3]):
        print(f"\n📊 Testing image {i+1}: {image_file}")
        image_path = os.path.join(images_dir, image_file)
        
        try:
            # Analyze chart
            result = analyzer.analyze_image(image_path)
            
            if result:
                print(f"   📈 Chart type: {result.chart_type}")
                print(f"   🎯 Confidence: {result.confidence}")
                
                # Check OCR text
                if result.extracted_text:
                    print(f"   📝 OCR found {len(result.extracted_text)} text elements")
                    for text in result.extracted_text[:3]:  # Show first 3
                        print(f"      - {text.strip()}")
                else:
                    print("   📝 No OCR text extracted")
            else:
                print("   ❌ No chart detected")
                
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_chart_analysis()
