import sqlite3
import json
import numpy as np
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


def benzerlik_hesapla(vektor1, vektor2):
    vektor1 = np.array(vektor1)
    vektor2 = np.array(vektor2)
    return np.dot(vektor1, vektor2) / (np.linalg.norm(vektor1) * np.linalg.norm(vektor2))


def en_alakali_belgeleri_bul(soru, kac_tane=2):
    soru_vektor = client.generate_embedding(soru).data[0].embedding

    baglanti = sqlite3.connect("bilgi_bankasi.db")
    imlec = baglanti.cursor()
    imlec.execute("SELECT dosya_adi, icerik, embedding FROM belgeler")
    tum_belgeler = imlec.fetchall()
    baglanti.close()

    sonuclar = []
    for dosya_adi, icerik, embedding_yazi in tum_belgeler:
        belge_vektor = json.loads(embedding_yazi)
        skor = benzerlik_hesapla(soru_vektor, belge_vektor)
        sonuclar.append((skor, dosya_adi, icerik))

    sonuclar.sort(key=lambda x: x[0], reverse=True)
    return sonuclar[:kac_tane]


soru = "Bıçakla nasıl doğru doğrama yapılır?"
print(f"Soru: '{soru}'\n")

en_iyi_belgeler = en_alakali_belgeleri_bul(soru, kac_tane=2)

print("En alakalı belgeler:")
for skor, dosya_adi, icerik in en_iyi_belgeler:
    print(f"\n[Benzerlik: {skor:.4f}] {dosya_adi}")
    print(f"  \"{icerik}\"")