import sqlite3
import json
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

# 1. Veritabanına bağlan (dosya yoksa otomatik oluşturulur)
baglanti = sqlite3.connect("belgelerim.db")
imlec = baglanti.cursor()

# 2. Tablo oluştur (eğer daha önce oluşturulmadıysa)
imlec.execute("""
CREATE TABLE IF NOT EXISTS belgeler (
    id INTEGER PRIMARY KEY,
    icerik TEXT,
    embedding TEXT
)
""")

# 3. Örnek belgelerimiz
belgeler = [
    "Kediler çok sevimli ve bağımsız hayvanlardır.",
    "Python, öğrenmesi kolay bir programlama dilidir.",
    "İstanbul, Türkiye'nin en kalabalık şehridir."
]

# 4. Her belgeyi embedding'e çevirip veritabanına kaydet
for belge in belgeler:
    vektor = client.generate_embedding(belge).data[0].embedding
    # Vektör bir sayı listesi, SQLite'a yazı (text) olarak kaydetmemiz lazım
    vektor_yazi = json.dumps(vektor)
    
    imlec.execute(
        "INSERT INTO belgeler (icerik, embedding) VALUES (?, ?)",
        (belge, vektor_yazi)
    )

# 5. Değişiklikleri kalıcı hale getir
baglanti.commit()

print("3 belge veritabanına kaydedildi!\n")

# 6. Veritabanından okuyup kontrol edelim
imlec.execute("SELECT id, icerik FROM belgeler")
sonuclar = imlec.fetchall()

print("Veritabanındaki belgeler:")
for satir in sonuclar:
    print(f"  ID: {satir[0]}  -->  {satir[1]}")

baglanti.close()