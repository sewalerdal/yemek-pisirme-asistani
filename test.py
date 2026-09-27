from foundry_local_sdk import Configuration, FoundryLocalManager

print("Foundry Local başlatılıyor...")

# 1. Ayarları oluştur
config = Configuration(app_name="rag_projem")

# 2. Sistemi başlat
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance

# 3. Modeli seç
model = manager.catalog.get_model("qwen2.5-0.5b")
model.download(lambda progress: None)
model.load()

print("Model hazır! Şimdi ona bir soru soruyoruz...")

# 4. Modelle konuşmak için bir istemci al
client = model.get_chat_client()

# 5. Soruyu gönder (bu sefer sistem mesajıyla modele kısa cevap vermesini emrediyoruz)
response = client.complete_chat([
    {"role": "system", "content": "Sen kısa ve net cevaplar veren bir asistansın. Cevapların en fazla 1-2 cümle olsun, tekrar yapma."},
    {"role": "user", "content": "Türkiye'nin başkenti neresidir?"}
])

# 6. Cevabı ekrana yazdır
print("\nModelin cevabı:")
print(response.choices[0].message.content)