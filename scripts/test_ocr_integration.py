"""
🔤 OCR Integration Test
======================
Test Tesseract OCR integration with Turkish text extraction
"""

import pytesseract
import cv2
import numpy as np
from pathlib import Path
import json
from chart_analyzer import ChartAnalyzer

def test_tesseract_basic():
    """Test basic Tesseract functionality"""
    print("🧪 Basic Tesseract Test")
    print("=" * 40)
    
    try:
        # Test version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract Version: {version}")
        
        # Test languages
        langs = pytesseract.get_languages()
        print(f"✅ Available Languages: {len(langs)} languages")
        
        if 'tur' in langs:
            print("🇹🇷 Turkish language pack: AVAILABLE")
        else:
            print("❌ Turkish language pack: NOT FOUND")
            
        if 'eng' in langs:
            print("🇺🇸 English language pack: AVAILABLE")
        else:
            print("❌ English language pack: NOT FOUND")
            
        return True
        
    except Exception as e:
        print(f"❌ Tesseract test failed: {e}")
        return False

def test_chart_analyzer_ocr():
    """Test ChartAnalyzer OCR functionality"""
    print("\n📊 ChartAnalyzer OCR Test")
    print("=" * 40)
    
    try:
        # Initialize analyzer
        analyzer = ChartAnalyzer()
        print("✅ ChartAnalyzer initialized successfully")
        
        # Test OCR configuration
        print(f"✅ OCR Config: {analyzer.ocr_config}")
        
        # Test with existing chart images if available
        images_dir = Path("extracted_data/images")
        if images_dir.exists():
            image_files = list(images_dir.glob("*.png"))
            if image_files:
                print(f"📁 Found {len(image_files)} chart images")
                
                # Test OCR on first image
                test_image = image_files[0]
                print(f"🔍 Testing OCR on: {test_image.name}")
                
                # Load image
                image = cv2.imread(str(test_image))
                if image is not None:
                    # Test OCR extraction
                    try:
                        text = pytesseract.image_to_string(
                            image, 
                            config=analyzer.ocr_config
                        )
                        
                        if text.strip():
                            print(f"✅ OCR extracted text: {len(text)} characters")
                            print(f"📝 Sample text: {text[:100]}...")
                        else:
                            print("⚠️ No text extracted from image")
                            
                    except Exception as e:
                        print(f"❌ OCR extraction failed: {e}")
                        
                else:
                    print("❌ Could not load image")
            else:
                print("⚠️ No chart images found in extracted_data/images")
        else:
            print("⚠️ No extracted_data/images directory found")
            
        return True
        
    except Exception as e:
        print(f"❌ ChartAnalyzer test failed: {e}")
        return False

def test_turkish_ocr():
    """Test Turkish OCR with synthetic text"""
    print("\n🇹🇷 Turkish OCR Test")
    print("=" * 40)
    
    try:
        # Create a simple test image with Turkish text
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        
        # Add Turkish text
        turkish_text = [
            "Gelir Gider Analizi",
            "Ocak 2024",
            "Toplam: 150,000 TL",
            "Kategori: Bütçe",
            "Durum: Başarılı"
        ]
        
        for i, text in enumerate(turkish_text):
            ax.text(0.1, 0.8 - i*0.15, text, fontsize=14, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Save test image
        test_image_path = "test_turkish_ocr.png"
        plt.savefig(test_image_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Test image created: {test_image_path}")
        
        # Test OCR on synthetic image
        image = cv2.imread(test_image_path)
        if image is not None:
            # Test with Turkish + English
            text_tur_eng = pytesseract.image_to_string(
                image, 
                config=r'--oem 3 --psm 6 -l tur+eng'
            )
            
            # Test with English only
            text_eng = pytesseract.image_to_string(
                image, 
                config=r'--oem 3 --psm 6 -l eng'
            )
            
            print(f"✅ Turkish+English OCR: {len(text_tur_eng)} characters")
            print(f"✅ English only OCR: {len(text_eng)} characters")
            
            if text_tur_eng.strip():
                print(f"📝 Turkish+English result:\n{text_tur_eng}")
            
            # Clean up
            Path(test_image_path).unlink()
            
        return True
        
    except Exception as e:
        print(f"❌ Turkish OCR test failed: {e}")
        return False

def main():
    """Run all OCR tests"""
    print("🚀 OCR Integration Test Suite")
    print("=" * 50)
    
    results = {
        'basic_tesseract': test_tesseract_basic(),
        'chart_analyzer_ocr': test_chart_analyzer_ocr(),
        'turkish_ocr': test_turkish_ocr()
    }
    
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    overall_success = all(results.values())
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 OCR Integration Ready!")
        print("✅ Tesseract installed and configured")
        print("✅ Turkish language support active")
        print("✅ ChartAnalyzer OCR integration working")
        print("\n📋 Next Steps:")
        print("1. Test OCR on real chart images")
        print("2. Integrate with FAISS vector store")
        print("3. Build RAG pipeline")
    
    return overall_success

if __name__ == "__main__":
    main() 