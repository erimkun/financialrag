import os
import sys
import requests
import zipfile
from pathlib import Path
import subprocess
import json
from typing import Optional, Dict, Any

class PopplerWindowsSetup:
    """
    Windows için poppler-windows otomatik kurulum
    Context7 best practice ile GitHub API kullanımı
    """
    
    def __init__(self):
        self.poppler_dir = Path("poppler-windows")
        self.github_api_url = "https://api.github.com/repos/oschwartz10612/poppler-windows/releases/latest"
        
    def get_latest_release_info(self) -> Optional[Dict[str, Any]]:
        """GitHub API'den latest release bilgisini al"""
        try:
            response = requests.get(self.github_api_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ GitHub API hatası: {e}")
            return None
    
    def download_poppler(self, download_url: str, filename: str) -> bool:
        """Poppler zip dosyasını indir"""
        print(f"📥 İndiriliyor: {filename}")
        
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ İndirildi: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ İndirme hatası: {e}")
            return False
    
    def extract_poppler(self, zip_filename: str) -> bool:
        """Zip dosyasını çıkart"""
        print(f"📦 Çıkartılıyor: {zip_filename}")
        
        try:
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # Çıkartılan klasörü bul ve yeniden adlandır
            for item in Path(".").iterdir():
                if item.is_dir() and "poppler" in item.name.lower() and item.name != "poppler-windows":
                    if self.poppler_dir.exists():
                        import shutil
                        shutil.rmtree(self.poppler_dir)
                    item.rename(self.poppler_dir)
                    break
            
            print(f"✅ Çıkartıldı: {self.poppler_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Çıkartma hatası: {e}")
            return False
    
    def add_to_path(self) -> bool:
        """Poppler'ı PATH'e ekle"""
        bin_path = self.poppler_dir / "Library" / "bin"
        
        if not bin_path.exists():
            print(f"❌ Poppler bin klasörü bulunamadı: {bin_path}")
            return False
        
        # PATH'e ekle (session için)
        current_path = os.environ.get('PATH', '')
        if str(bin_path) not in current_path:
            os.environ['PATH'] = str(bin_path) + os.pathsep + current_path
            print(f"✅ PATH'e eklendi: {bin_path}")
        else:
            print(f"ℹ️ Zaten PATH'te: {bin_path}")
        
        return True
    
    def test_poppler(self) -> bool:
        """Poppler kurulumunu test et"""
        print("🧪 Poppler test ediliyor...")
        
        try:
            # pdftoppm komutunu test et
            result = subprocess.run(['pdftoppm', '-h'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0:
                print("✅ Poppler başarıyla kuruldu!")
                return True
            else:
                print(f"❌ Poppler test hatası: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Poppler test timeout")
            return False
        except FileNotFoundError:
            print("❌ pdftoppm komutu bulunamadı")
            return False
        except Exception as e:
            print(f"❌ Poppler test hatası: {e}")
            return False
    
    def test_pdf2image(self) -> bool:
        """pdf2image ile poppler entegrasyonunu test et"""
        print("🧪 pdf2image entegrasyonu test ediliyor...")
        
        try:
            import pdf2image
            
            # Basit test - pdf2image.exceptions yerine try-except kullan
            try:
                test_result = pdf2image.pdfinfo_from_path("test.pdf")
                print("✅ pdf2image poppler entegrasyonu başarılı!")
                return True
            except Exception as pdf_error:
                if "PDFInfoNotInstalledError" in str(type(pdf_error)):
                    print("❌ pdf2image poppler bulamıyor")
                    return False
                elif "FileNotFoundError" in str(type(pdf_error)):
                    print("ℹ️ Test PDF dosyası yok, ancak poppler bulundu")
                    return True
                else:
                    print(f"❌ pdf2image test hatası: {pdf_error}")
                    return False
                
        except ImportError:
            print("❌ pdf2image modülü bulunamadı")
            return False
        except Exception as e:
            print(f"❌ pdf2image test hatası: {e}")
            return False
    
    def setup_poppler(self) -> bool:
        """Ana kurulum fonksiyonu"""
        print("🚀 Poppler-Windows Kurulumu")
        print("=" * 40)
        
        # Zaten kurulu mu kontrol et
        if self.poppler_dir.exists():
            print(f"ℹ️ Poppler zaten kurulu: {self.poppler_dir}")
            self.add_to_path()
            if self.test_poppler():
                return True
            else:
                print("🔄 Mevcut kurulum bozuk, yeniden kuruluyor...")
        
        # Latest release bilgisini al
        release_info = self.get_latest_release_info()
        if not release_info:
            return False
        
        # Download URL'i bul
        download_url: Optional[str] = None
        filename: Optional[str] = None
        
        for asset in release_info.get('assets', []):
            if asset['name'].endswith('.zip'):
                download_url = asset['browser_download_url']
                filename = asset['name']
                break
        
        if not download_url or not filename:
            print("❌ Download URL bulunamadı")
            return False
        
        print(f"📋 Latest release: {release_info['tag_name']}")
        print(f"📥 Download: {filename}")
        
        # İndir ve kur
        if not self.download_poppler(download_url, filename):
            return False
        
        if not self.extract_poppler(filename):
            return False
        
        # Zip dosyasını sil
        try:
            os.remove(filename)
            print(f"🗑️ Zip dosyası silindi: {filename}")
        except Exception:
            pass
        
        # PATH'e ekle
        if not self.add_to_path():
            return False
        
        # Test et
        if not self.test_poppler():
            return False
        
        if not self.test_pdf2image():
            print("⚠️ pdf2image test başarısız, ancak poppler kuruldu")
        
        print("\n✅ Poppler-Windows kurulumu tamamlandı!")
        print(f"📁 Kurulum dizini: {self.poppler_dir.absolute()}")
        print("🔄 Yeni terminal oturumlarında PATH otomatik olarak ayarlanmayacak")
        print("💡 Kalıcı PATH için sistem ayarlarını güncelleyin")
        
        return True
    
    def get_setup_info(self) -> Dict[str, Any]:
        """Kurulum bilgilerini döndür"""
        return {
            "poppler_dir": str(self.poppler_dir.absolute()),
            "bin_path": str(self.poppler_dir / "Library" / "bin"),
            "installed": self.poppler_dir.exists(),
            "in_path": str(self.poppler_dir / "Library" / "bin") in os.environ.get('PATH', '')
        }

if __name__ == "__main__":
    setup = PopplerWindowsSetup()
    
    if setup.setup_poppler():
        print("\n📊 Kurulum Bilgileri:")
        info = setup.get_setup_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
    else:
        print("\n❌ Kurulum başarısız!")
        sys.exit(1) 