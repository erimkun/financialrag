# Groq API Key Güncelleme Rehberi

## Sorun
Mevcut Groq API key'i geçersiz (401 Invalid API Key hatası)

## Çözüm Adımları

### 1. Yeni API Key Alma
1. https://console.groq.com/keys adresine gidin
2. Groq hesabınızla giriş yapın (yoksa ücretsiz hesap açın)
3. "Create API Key" butonuna tıklayın
4. Key'e isim verin (örn: "Turkish-Financial-RAG")
5. API key'i kopyalayın (gsk_ ile başlar)

### 2. API Key'i Güncelleme

#### Seçenek A: Environment Variable (Önerilen)
```powershell
# PowerShell'de (yeniden başlatma gerekir)
$env:GROQ_API_KEY="gsk_YENİ_API_KEY_BURASİNA_YAPIŞTIRIN"

# Kalıcı için (sistem yeniden başlatılmalı)
[System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_YENİ_API_KEY_BURASİNA_YAPIŞTIRIN", "User")
```

#### Seçenek B: Kod İçinde Direkt Değiştirme (Geçici)
`backend/main.py` dosyasının 35. satırındaki key'i değiştirin:
```python
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_YENİ_API_KEY_BURASİNA_YAPIŞTIRIN")
```

### 3. Servisleri Yeniden Başlatma
```powershell
# Backend'i yeniden başlat
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend'i yeniden başlat (ayrı terminal)
cd frontend
npm run dev
```

### 4. Test Etme
1. Frontend'de chat'e gidin
2. Basit bir soru sorun: "Merhaba"
3. API key çalışıyorsa yanıt almalısınız

## Şu An Test Edebileceğiniz
PDF yüklemek için önce API key sorunu çözülmelidir. PMI sorunuz şu şekilde sorulabilir:
"ABD'de bileşik PMI temmuz ayında öncü veriye göre ne oldu?"

## Destek
- API key sorunu devam ederse: https://console.groq.com/docs
- Sistem sorunları için: Debug panelini açın (F12 -> Console)
