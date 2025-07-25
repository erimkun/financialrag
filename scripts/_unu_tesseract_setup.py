"""
🔤 Tesseract OCR Setup for Windows
==================================
Simple Tesseract OCR setup helper for Windows.
"""

import subprocess
import os
from pathlib import Path

def is_tesseract_installed():
    """Check if Tesseract is already installed"""
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def try_winget_install():
    """Try to install Tesseract using winget"""
    try:
        print("🔧 Winget ile Tesseract kurulumu deneniyor...")
        
        result = subprocess.run(
            ['winget', 'install', 'UB-Mannheim.Tesseract'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ Tesseract winget ile kuruldu")
            return True
        else:
            print(f"⚠️ Winget kurulumu başarısız")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️ Winget bulunamadı")
        return False

def create_manual_instructions():
    """Create manual installation instructions"""
    instructions_dir = Path("tesseract-ocr")
    instructions_dir.mkdir(exist_ok=True)
    
    batch_content = """@echo off
echo 🔤 Tesseract OCR Manuel Kurulum
echo ============================
echo.
echo 1. https://github.com/UB-Mannheim/tesseract/releases adresine git
echo 2. tesseract-ocr-w64-setup-*.exe dosyasını indir
echo 3. Kurulum sırasında "Additional language data" seç
echo 4. Turkish language pack'i seç
echo 5. PATH'e ekle: C:\\Program Files\\Tesseract-OCR
echo.
echo Kurulum sonrası test için:
echo   tesseract --version
echo.
pause
"""
    
    batch_file = instructions_dir / "install_tesseract.bat"
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"📋 Manuel kurulum rehberi: {batch_file}")
    return str(batch_file)

def test_tesseract():
    """Test Tesseract installation"""
    try:
        print("🧪 Tesseract test ediliyor...")
        
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Tesseract başarıyla kuruldu!")
            version_line = result.stdout.split('\n')[0]
            print(f"📋 {version_line}")
            
            # Test Turkish language support
            lang_result = subprocess.run(
                ['tesseract', '--list-langs'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if 'tur' in lang_result.stdout:
                print("🇹🇷 Türkçe dil paketi mevcut")
            else:
                print("⚠️ Türkçe dil paketi bulunamadı")
            
            return True
        else:
            print("❌ Tesseract test başarısız")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Tesseract bulunamadı")
        return False

def main():
    """Main setup function"""
    print("🚀 Tesseract-OCR Kurulumu")
    print("=" * 40)
    
    # Check if already installed
    if is_tesseract_installed():
        print("ℹ️ Tesseract zaten kurulu")
        test_tesseract()
        return
    
    # Try winget installation
    if try_winget_install():
        import time
        time.sleep(3)
        
        if is_tesseract_installed():
            print("🎉 Winget kurulumu başarılı!")
            test_tesseract()
            return
    
    # Create manual instructions
    batch_file = create_manual_instructions()
    
    print("\n💡 Manuel kurulum gerekiyor:")
    print("1. https://github.com/UB-Mannheim/tesseract/releases")
    print("2. tesseract-ocr-w64-setup-*.exe indir")
    print("3. Kurulum sırasında Turkish language pack seç")
    print("4. PATH'e ekle: C:\\Program Files\\Tesseract-OCR")
    print(f"5. Detaylar için: {batch_file}")

if __name__ == "__main__":
    main() 