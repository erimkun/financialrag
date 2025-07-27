import requests
import json

# Test query
query_data = {
    'question': 'BIST 100 endeksi hakkında bilgi ver',
    'language': 'tr'
}

try:
    response = requests.post(
        'http://localhost:8000/api/query',
        json=query_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print('✅ Query başarılı!')
        print(f'📊 Cevap: {result["answer"][:200]}...')
        print(f'⏱️ Süre: {result["response_time"]:.2f}s')
        print(f'🎯 Güven: {result["confidence"]:.2f}')
    else:
        print(f'❌ Hata: {response.status_code} - {response.text}')
        
except Exception as e:
    print(f'❌ Bağlantı hatası: {e}')
