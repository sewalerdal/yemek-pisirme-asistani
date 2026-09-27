import sqlite3
import json
import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager

print("Foundry Local başlatılıyor...")
config = Configuration(app_name="rag_projem")
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance

# 1. Embedding modelini yükle (arama için)
embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
embedding_model.download(lambda progress: None)
embedding_model.load()
embedding_client = embedding_model.get_embedding_client()
print("Embedding modeli hazır.")

# 2. Sohbet modelini yükle (cevap üretmek için)
sohbet_model = manager.catalog.get_model("qwen2.5-0.5b")
sohbet_model.download(lambda progress: None)
sohbet_model.load()
sohbet_client = sohbet_model.get_chat_client()
print("Sohbet modeli hazır.\n")


def benzerlik_hesapla(vektor1, vektor2):
    vektor1 = np.array(vektor1)
    vektor2 = np.array(vektor2)
    return np.dot(vektor1, vektor2) / (np.linalg.norm(vektor1) * np.linalg.norm(vektor2))


def en_alakali_belgeleri_bul(soru, kac_tane=3):
    soru_vektor = embedding_client.generate_embedding(soru).data[0].embedding

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


def soru_sor(soru):
    bulunanlar = en_alakali_belgeleri_bul(soru, kac_tane=3)

    for skor, dosya_adi, icerik in bulunanlar:
        print(f"  [Kaynak: {dosya_adi}, benzerlik: {skor:.4f}]")

    birlesik_bilgi = "\n\n".join([icerik for (skor, dosya_adi, icerik) in bulunanlar])

    sistem_mesaji = (
        "Sen yardımsever bir yemek pişirme asistanısın. "
        "Sadece sana verilen BİLGİ'yi kullanarak soruyu cevapla. "
        "Eğer bilgi yetersizse, 'Bu konuda bilgim yok' de. "
        "Kısa ve net cevap ver.\n\n"
        f"BİLGİ:\n{birlesik_bilgi}"
    )

    yanit = sohbet_client.complete_chat([
        {"role": "system", "content": sistem_mesaji},
        {"role": "user", "content": soru}
    ])

    tam_cevap = yanit.choices[0].message.content
    cumleler = tam_cevap.split(". ")
    kisa_cevap = ". ".join(cumleler[:2])
    if not kisa_cevap.endswith("."):
        kisa_cevap += "."

    return kisa_cevap


# ANA DÖNGÜ: Kullanıcı istediği kadar soru sorabilir
print("=" * 50)
print("Yemek Pişirme Asistanına Hoş Geldiniz!")
print("Çıkmak için 'çık' yazabilirsiniz.")
print("=" * 50)

while True:
    soru = input("\nSorunuz: ")

    if soru.lower() in ["çık", "cik", "exit", "quit"]:
        print("Görüşmek üzere!")
        break

    if soru.strip() == "":
        continue

    cevap = soru_sor(soru)
    print(f"\nAsistan: {cevap}")