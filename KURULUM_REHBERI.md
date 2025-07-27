# Turkish Financial RAG System - Kurulum Rehberi

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler
- Python 3.8+
- Node.js 18+
- Groq API Key (ücretsiz)

### 2. Groq API Key Alma
1. https://console.groq.com/keys adresine gidin
2. Ücretsiz hesap oluşturun
3. "Create API Key" butonuna tıklayın
4. API key'i kopyalayın (gsk_ ile başlar)

### 3. Backend Kurulumu

```bash
# 1. Backend dizinine gidin
cd backend

# 2. .env dosyasını oluşturun
copy .env.example .env

# 3. .env dosyasını düzenleyin ve API key'inizi ekleyin
notepad .env
# GROQ_API_KEY=gsk_BURAYA_API_KEYINIZI_YAPIŞTIRIN

# 4. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 5. Backend'i başlatın
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Kurulumu

```bash
# 1. Yeni terminal açın ve frontend dizinine gidin
cd frontend

# 2. .env dosyası zaten mevcut (değiştirmeye gerek yok)
# Gerekirse .env dosyasını özelleştirebilirsiniz

# 3. Bağımlılıkları yükleyin
npm install

# 4. Frontend'i başlatın
npm run dev
```

### 5. Sistem Kontrolü

1. **Backend:** http://localhost:8000/api/docs
2. **Frontend:** http://localhost:5173
3. **Health Check:** http://localhost:8000/api/health

## ⚙️ Konfigürasyon

### Backend (.env dosyası)

```env
# Ana konfigürasyon
GROQ_API_KEY=gsk_your_api_key_here
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Model ayarları
GROQ_MODEL=llama-3.1-70b-versatile
MAX_TOKENS=2048
TEMPERATURE=0.1

# Dosya yükleme
MAX_FILE_SIZE_MB=50
UPLOADS_DIR=uploads

# Vector store
VECTOR_STORE_PATH=../vector_store
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Frontend (.env dosyası)

```env
# API ayarları
VITE_API_BASE_URL=http://localhost:8000
VITE_REQUEST_TIMEOUT=30000

# UI ayarları
VITE_APP_TITLE=Turkish Financial AI Assistant
VITE_ENABLE_DEBUG=false

# Dosya yükleme
VITE_MAX_FILE_SIZE_MB=50
VITE_ALLOWED_FILE_TYPES=.pdf
```

## 🔧 Özelleştirme

### API Key Değiştirme
Backend `.env` dosyasında `GROQ_API_KEY` değerini güncelleyin ve backend'i yeniden başlatın.

### Port Değiştirme
- **Backend:** `.env` dosyasında `SERVER_PORT`
- **Frontend:** `.env` dosyasında `VITE_PORT`

### Model Değiştirme
Backend `.env` dosyasında `GROQ_MODEL` değerini değiştirin:
- `llama-3.1-70b-versatile` (varsayılan, en iyi kalite)
- `llama-3.1-8b-instant` (daha hızlı)
- `mixtral-8x7b-32768` (daha uzun context)

## 🐛 Sorun Giderme

### API Key Hatası (401)
```bash
# .env dosyasını kontrol edin
cat backend/.env | grep GROQ_API_KEY

# Yeni API key alın ve güncelleyin
# Backend'i yeniden başlatın
```

### Backend Bağlantı Hatası
```bash
# Backend'in çalıştığını kontrol edin
curl http://localhost:8000/api/health

# Port çakışması varsa farklı port kullanın
SERVER_PORT=8001 python -m uvicorn main:app --reload --port 8001
```

### Frontend CSS Sorunları
```bash
# Tailwind CSS'i yeniden build edin
cd frontend
npx tailwindcss -i ./src/index.css -o ./src/tailwind-output.css
npm run dev
```

## 📋 Sistem Durumu

Sistem çalışır durumda ise:
- ✅ Backend: API dokumentasyonu açılır
- ✅ Frontend: Ana sayfa yüklenir
- ✅ Debug panel: CSS yüklendi gösterir
- ✅ Upload: PDF dosyaları yüklenebilir
- ✅ Chat: Sorulara yanıt alınır

## 🔗 Faydalı Linkler

- [Groq API Docs](https://console.groq.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vite Docs](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

## 📞 Destek

Sorun yaşıyorsanız:
1. `.env` dosyalarını kontrol edin
2. API key'in geçerli olduğundan emin olun
3. Port çakışması olmadığını kontrol edin
4. Browser console'da hata mesajlarını kontrol edin
