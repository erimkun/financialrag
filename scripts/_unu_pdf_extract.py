import pdfplumber
from pathlib import Path
import json
from PIL import Image
import io

# $ 1.1 Metin ve 1.2 Tablo Çıkarımı (Context7 best practice: pdfplumber ile)

def extract_text_and_tables(pdf_path):
    text_data = []
    tables_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            # Metin çıkarımı
            text = page.extract_text()
            text_data.append({
                "sayfa": i + 1,
                "paragraflar": text.split('\n') if text else []
            })
            
            # Tablo çıkarımı (pdfplumber ile)
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                if table:
                    tables_data.append({
                        "sayfa": i + 1,
                        "tablo_id": j + 1,
                        "data": {"rows": table}
                    })

    return text_data, tables_data

# $ 1.3 ve 1.4 Görsel ve Başlık Çıkarımı (Context7 best practice: pdfplumber ile Windows uyumlu)
def extract_graphics(pdf_path, output_dir):
    graphics = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Sayfanın tam görselini kaydet (pdfplumber ile)
            page_img_path = output_dir / f"page{page_num + 1}_full.png"
            
            # pdfplumber ile sayfa görselini al
            try:
                page_img = page.to_image(resolution=150)
                page_img.save(page_img_path)
            except Exception as e:
                print(f"Sayfa {page_num + 1} görsel kaydı hatası: {e}")
                # Alternatif: boş görsel oluştur
                blank_img = Image.new('RGB', (800, 600), color='white')
                blank_img.save(page_img_path)
            
            # Sayfa metnini al
            page_text = page.extract_text() or ""
            text_lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            
            # Basit başlık tespiti: kısa, büyük harfle başlayan satırlar
            potential_titles = []
            for line in text_lines:
                if (len(line) < 100 and 
                    len(line) > 10 and 
                    line[0].isupper() and
                    not line.endswith('.') and
                    not line.startswith('•') and
                    not line.isdigit()):
                    potential_titles.append(line)
            
            # Her sayfa için bir görsel objesi oluştur
            title = potential_titles[0] if potential_titles else f"Sayfa {page_num + 1}"
            
            graphics.append({
                "sayfa": page_num + 1,
                "başlık": title,
                "görsel_path": str(page_img_path),
                "çıkarılan_veri": None
            })
    
    return graphics

# $ 1.5 Sayfa Bazlı JSON Çıktı

def build_page_objects(texts, tables, graphics):
    page_objs = {}
    
    # Metin verilerini ekle
    for t in texts:
        page_objs[t["sayfa"]] = {
            "sayfa": t["sayfa"],
            "paragraflar": t["paragraflar"],
            "tablolar": [],
            "grafikler": []
        }
    
    # Tablo verilerini ekle
    for tab in tables:
        if tab["sayfa"] in page_objs:
            page_objs[tab["sayfa"]]["tablolar"].append(tab["data"])
    
    # Görsel verilerini ekle
    for g in graphics:
        if g["sayfa"] in page_objs:
            page_objs[g["sayfa"]]["grafikler"].append({
                "başlık": g["başlık"],
                "görsel_path": g["görsel_path"],
                "çıkarılan_veri": g["çıkarılan_veri"]
            })
    
    return list(page_objs.values())

if __name__ == "__main__":
    pdf_path = "2025_07_16_Haziran Ayı Bütce Dengesi.pdf"
    output_dir = Path("extracted_images")
    output_dir.mkdir(exist_ok=True)

    print("📄 Metin ve tablo çıkarımı başlıyor...")
    metinler, tablolar = extract_text_and_tables(pdf_path)
    print(f"✅ Metin sayfaları: {len(metinler)}, Tablolar: {len(tablolar)}")
    
    print("🖼️ Görsel çıkarımı başlıyor...")
    grafikler = extract_graphics(pdf_path, output_dir)
    print(f"✅ Görseller: {len(grafikler)}")
    
    print("📝 JSON çıktısı oluşturuluyor...")
    sayfa_objeleri = build_page_objects(metinler, tablolar, grafikler)

    with open("extracted_data.json", "w", encoding="utf-8") as f:
        json.dump(sayfa_objeleri, f, ensure_ascii=False, indent=2)

    print("✅ Çıktı: extracted_data.json")
    print("✅ Görseller: extracted_images/ klasöründe")
    print(f"📊 Toplam {len(sayfa_objeleri)} sayfa işlendi")
    
    # Özet bilgileri
    total_paragraphs = sum(len(page.get("paragraflar", [])) for page in sayfa_objeleri)
    total_tables = sum(len(page.get("tablolar", [])) for page in sayfa_objeleri)
    total_graphics = sum(len(page.get("grafikler", [])) for page in sayfa_objeleri)
    
    print(f"📈 Özet: {total_paragraphs} paragraf, {total_tables} tablo, {total_graphics} görsel") 