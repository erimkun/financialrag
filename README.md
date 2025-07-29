# Turkish Financial RAG System - Proje Rehberi

Bu proje, finansal raporların ve PDF belgelerinin otomatik olarak analiz edilmesini, özetlenmesini ve çeşitli testlerden geçirilmesini sağlayan bir sistemdir. Kullanıcılar, sistem aracılığıyla PDF formatındaki finansal raporları yükleyebilir, bu raporlar üzerinde metin ve görsel tabanlı analizler gerçekleştirebilir, sonuçları özetleyebilir ve test edebilirler.

---

## 0. Hızlı Kurulum ve Çalıştırma Adımları

Projeyi hızlıca kurmak ve çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

### Repository'yi Klonlayın
```bash
git clone https://github.com/erimkun/financialrag.git
cd financialrag
```

### Backend Kurulumu
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows için
# veya
source venv/bin/activate  # macOS/Linux için
pip install -r requirements.txt
copy .env.example .env  # Windows için
# veya
cp .env.example .env  # macOS/Linux için
notepad .env  # API anahtarınızı ekleyin
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Backend, `http://localhost:8000` adresinde çalışacaktır. API dokümantasyonu için: `http://localhost:8000/api/docs`

### Frontend Kurulumu
```bash
cd frontend
npm install
npm run dev
```
Frontend, `http://localhost:5173` adresinde çalışacaktır.

> **Not:** Tesseract ve Poppler gibi ek bağımlılıkların kurulumu için detaylar aşağıda "Kurulum Adımları" bölümünde verilmiştir.

---

## 1. Proje Tanıtımı

Bu sistem, finansal PDF raporlarının otomatik olarak analiz edilmesi, metin ve tablo çıkarımı, görsel analiz (grafik ve tablo tespiti), OCR ile metin tanıma, sonuçların JSON ve görsel formatlarda kaydedilmesi, otomatik test ve analiz scriptleri ile kolay kurulum ve kullanım imkanı sunar.

### Genel Özellikler
- PDF dosyalarından metin ve tablo çıkarımı
- Görsel analiz (grafik ve tablo tespiti)
- Tesseract ile OCR (Optik Karakter Tanıma) desteği
- Sonuçların JSON ve görsel formatlarda kaydedilmesi
- Otomatik test ve analiz scriptleri
- Kolay kurulum ve kullanım


## 2. Sistemin İşleyişi

Sistem, yüklenen PDF dosyalarını çok aşamalı bir analiz sürecinden geçirir. Temel iş akışı aşağıdaki gibidir:

1. **PDF Yükleme:** Kullanıcı, frontend arayüzü üzerinden PDF dosyasını yükler.
2. **Ön İşleme:** Backend, Poppler ile PDF sayfalarını görsellere dönüştürür ve Tesseract ile OCR işlemi uygular.
3. **Metin ve Tablo Çıkarımı:** pdfplumber ve ek Python kütüphaneleriyle metin ve tablo verileri ayrıştırılır.
4. **Görsel Analiz:** Grafik ve tablo tespiti için ek analizler yapılır.
5. **Vektörleştirme ve LLM Analizi:** Metinler Groq API ile özetlenir, vektör veritabanına kaydedilir.
6. **Sonuçların Sunulması:** JSON ve görsel çıktılar frontend'e iletilir, kullanıcıya özet ve analizler sunulur.

Her adımda hata kontrolü ve loglama yapılır. API endpoint'leri FastAPI ile RESTful olarak sunulmuştur. Frontend, backend ile HTTP üzerinden haberleşir.

---
## 3. Kullanım Kılavuzu

### Web Arayüzü Kullanımı
1. Frontend'i başlatın (`npm run dev`).
2. `http://localhost:5173` adresine gidin.
3. "PDF Yükle" butonunu kullanarak analiz etmek istediğiniz dosyayı seçin.
4. Yükleme ve analiz tamamlandığında, özet ve analiz sonuçları ekranda görüntülenir.
5. Sonuçları JSON veya görsel olarak indirebilirsiniz.

### Komut Satırı Kullanımı (Backend)
Backend dizininde çeşitli test ve analiz scriptleri bulunmaktadır. Örneğin:

```bash
python create_performance_optimization.py
python create_testing_checklists.py
python generate_final_summary.py
```
Bu scriptler, örnek PDF dosyaları üzerinde otomatik analiz ve özetleme işlemleri yapar. Sonuçlar `analysis_output/` veya `extracted_data/` klasörlerinde JSON olarak kaydedilir.

### API Kullanımı
Backend çalışırken, FastAPI dokümantasyonuna `http://localhost:8000/api/docs` adresinden ulaşabilir, API endpoint'lerini test edebilirsiniz.

## 4. Scriptlerde Bulunan Ama Kullanılmayan Dosyalar

Projede bazı scriptler ve dosyalar, geliştirme ve test süreçlerinde kullanılmış ancak son kullanıcı için doğrudan gerekli olmayabilir. Bu dosyalar, örnek veri üretimi, eski analiz yöntemleri veya alternatif pipeline denemeleri için bırakılmıştır. Kodun şeffaflığı ve tekrar kullanılabilirliği için projede tutulmaktadır. Gerektiğinde bu dosyalar README veya kod içi açıklamalarla işaretlenmiştir.

## 5. Adım Adım Test Etme

Sistemin doğru çalıştığını doğrulamak için aşağıdaki test adımlarını uygulayabilirsiniz:

1. **Backend Testleri:**
   - `backend` dizininde aşağıdaki komutları çalıştırarak birim ve entegrasyon testlerini başlatın:
     ```bash
     python -m unittest discover
     # veya
     pytest
     ```
   - Testler, API endpoint'lerinin ve analiz fonksiyonlarının doğru çalıştığını kontrol eder.

2. **Frontend Testleri:**
   - Frontend için özel test scriptleri veya manuel testler uygulanabilir.
   - Uygulamayı başlatıp, PDF yükleyerek ve analiz sonuçlarını kontrol ederek temel işlevleri test edin.

3. **End-to-End Testler:**
   - `test_end_to_end.py` gibi scriptlerle tam akış testleri yapılabilir.
   - Sonuçlar `test_results.json` veya benzeri dosyalarda raporlanır.

## 6. Ek Bilgiler ve Sıkça Sorulan Sorular (SSS)

### Sık Karşılaşılan Sorunlar ve Çözümleri

- **API Key Hatası (401):** `.env` dosyanızda doğru Groq API anahtarını kullandığınızdan emin olun ve backend'i yeniden başlatın.
- **Backend Bağlantı Sorunu:** Backend'in çalıştığından ve doğru portta olduğundan emin olun. `http://localhost:8000/api/health` ile kontrol edebilirsiniz.
- **Frontend CSS Sorunları:** Tailwind veya diğer CSS bağımlılıklarını yeniden derleyin: `npx tailwindcss -i ./src/index.css -o ./src/tailwind-output.css` ardından `npm run dev`.
- **PDF Yüklenmiyor:** Dosya boyutu veya formatı sınırlarını kontrol edin. `.env` dosyasında `VITE_MAX_FILE_SIZE_MB` ve `VITE_ALLOWED_FILE_TYPES` ayarlarını gözden geçirin.

### Faydalı Linkler
- [Groq API Docs](https://console.groq.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vite Docs](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

### Destek
Sorun yaşarsanız:
1. `.env` dosyalarını ve API anahtarınızı kontrol edin
2. Port çakışması olmadığından emin olun
3. Browser console'da hata mesajlarını inceleyin
4. Geliştiriciye veya proje sahibine ulaşın

Bu README, projenin kurulumundan kullanımına, testinden sorun giderimine kadar tüm adımları detaylı ve bütüncül şekilde açıklamaktadır. Kodun ve sistemin işleyişiyle ilgili daha fazla bilgi için kod içi açıklamaları ve ek dokümantasyon dosyalarını inceleyebilirsiniz.
