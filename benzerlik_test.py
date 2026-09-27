from foundry_local_sdk import Configuration, FoundryLocalManager
import numpy as np

print("Foundry Local başlatılıyor...")

config = Configuration(app_name="rag_projem")
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance

model = manager.catalog.get_model("qwen3-embedding-0.6b")
model.download(lambda progress: None)
model.load()
print("Model hazır!\n")

client = model.get_embedding_client()

# Elimizde 3 örnek "belge" (cümle) olsun
belgeler = [
    "Kediler çok sevimli ve bağımsız hayvanlardır.",
    "Python, öğrenmesi kolay bir programlama dilidir.",
    "İstanbul, Türkiye'nin en kalabalık şehridir."
]

# Kullanıcının sorduğu soru
soru = "Hangi programlama dili başlangıç için iyidir?"

# Fonksiyon: iki vektör arasındaki benzerliği hesaplar (0 ile 1 arası)
def benzerlik_hesapla(vektor1, vektor2):
    vektor1 = np.array(vektor1)
    vektor2 = np.array(vektor2)
    return np.dot(vektor1, vektor2) / (np.linalg.norm(vektor1) * np.linalg.norm(vektor2))

# Sorunun vektörünü hesapla
soru_vektor = client.generate_embedding(soru).data[0].embedding

print(f"Soru: '{soru}'\n")

# Her belgeyle karşılaştır
en_yuksek_skor = -1
en_iyi_belge = ""

for belge in belgeler:
    belge_vektor = client.generate_embedding(belge).data[0].embedding
    skor = benzerlik_hesapla(soru_vektor, belge_vektor)
    print(f"Benzerlik: {skor:.4f}  -->  '{belge}'")
    
    if skor > en_yuksek_skor:
        en_yuksek_skor = skor
        en_iyi_belge = belge

print(f"\nEn alakalı belge: '{en_iyi_belge}'")