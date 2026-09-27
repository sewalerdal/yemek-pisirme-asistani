import sqlite3
import json
import os
from foundry_local_sdk import Configuration, FoundryLocalManager

print("Foundry Local başlatılıyor...")
config = Configuration(app_name="rag_projem")
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance

model = manager.catalog.get_model("qwen3-embedding-0.6b")
model.download(lambda progress: None)
model.load()
print("Model hazır!\n")

client = model.get_embedding_client()

# 1. Veritabanına bağlan (projemizin asıl veritabanı)
baglanti = sqlite3.connect("bilgi_bankasi.db")
imlec = baglanti.cursor()

# 2. Tabloyu oluştur (eğer yoksa)
imlec.execute("""
CREATE TABLE IF NOT EXISTS belgeler (
    id INTEGER PRIMARY KEY,
    dosya_adi TEXT,
    icerik TEXT,
    embedding TEXT
)
""")

# 3. Eğer daha önce çalıştırdıysak, eski kayıtları temizle (tekrar tekrar eklenmesin diye)
imlec.execute("DELETE FROM belgeler")

# 4. "belgeler" klasöründeki tüm .txt dosyalarını bul
klasor = "belgeler"
dosyalar = [f for f in os.listdir(klasor) if f.endswith(".txt")]

print(f"{len(dosyalar)} adet belge bulundu: {dosyalar}\n")

# 5. Her dosyayı oku, embedding'ini çıkar, veritabanına kaydet
for dosya_adi in dosyalar:
    dosya_yolu = os.path.join(klasor, dosya_adi)
    
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        icerik = f.read().strip()
    
    print(f"İşleniyor: {dosya_adi}")
    vektor = client.generate_embedding(icerik).data[0].embedding
    vektor_yazi = json.dumps(vektor)
    
    imlec.execute(
        "INSERT INTO belgeler (dosya_adi, icerik, embedding) VALUES (?, ?, ?)",
        (dosya_adi, icerik, vektor_yazi)
    )

baglanti.commit()
baglanti.close()

print(f"\nTamamlandı! {len(dosyalar)} belge 'bilgi_bankasi.db' veritabanına kaydedildi.")