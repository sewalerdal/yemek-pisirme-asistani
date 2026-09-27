from foundry_local_sdk import Configuration, FoundryLocalManager

print("Foundry Local başlatılıyor...")

config = Configuration(app_name="rag_projem")
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance

# Bu sefer "sohbet" modeli değil, "gömme" (embedding) modeli seçiyoruz
model = manager.catalog.get_model("qwen3-embedding-0.6b")
print("Gömme modeli indiriliyor, biraz sürebilir...")
model.download(lambda progress: print(f"\rİndirme: %{progress:.1f}", end="", flush=True))
print()
model.load()
print("Model hazır!")

# Gömme işlemleri için bir istemci alıyoruz
client = model.get_embedding_client()

# Bir cümleyi sayılara (vektöre) çevirelim
cumle = "Kediler çok sevimli hayvanlardır"
response = client.generate_embedding(cumle)
vektor = response.data[0].embedding

print(f"\nCümle: '{cumle}'")
print(f"Bu cümle {len(vektor)} tane sayıdan oluşan bir listeye dönüştü.")
print(f"İlk 5 sayı: {vektor[:5]}")