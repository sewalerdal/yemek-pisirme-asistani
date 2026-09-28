# Yerel Yemek Pişirme Asistanı (RAG Projesi)

## Bu Proje Nedir?

Bu, tamamen kendi bilgisayarımda çalışan, internet gerektirmeyen bir
Soru-Cevap asistanıdır. Yemek pişirme konusunda hazırladığım küçük bir
bilgi bankasından yararlanarak sorularımı yanıtlar ve basit bir
masaüstü penceresi üzerinden kullanılır.

Sistem, **RAG (Retrieval-Augmented Generation)** yaklaşımının "bilgi
bulma" (retrieval) kısmına dayanır: Sorulan soruyla en alakalı bilgiyi
kendi belgelerimden bulur ve cevabı yapay zekanın uydurmasına izin
vermeden, doğrudan bu belgelerden alıntılayarak verir.

## Nasıl Çalışır?

1. Program açılırken belgeler cümlelere bölünür ve her cümle,
   embedding modeliyle sayısal bir forma (vektöre) çevrilir
2. Kullanıcı pencerede bir soru yazar
3. Soru da aynı şekilde sayısal forma çevrilir
4. Sorunun vektörü, tüm cümlelerin vektörleriyle karşılaştırılır
   (kosinüs benzerliği ile)
5. En benzer cümle bulunur ve cevap olarak gösterilir. Aynı belgeden
   ikinci bir cümle de neredeyse aynı derecede alakalıysa, o da eklenir
6. **En yüksek benzerlik skoru belirli bir eşiğin altındaysa**, sistem
   "Bu konuda bilgim yok" der. Böylece alakasız sorularda yanlış bilgi
   uydurulmaz
7. Cevabın altında kaynak dosya adı ve benzerlik skoru gösterilir

## Neden Sohbet Modeli Kullanılmadı?

Projenin ilk sürümlerinde cevabı bir sohbet modeli (qwen2.5-0.5b ve
sonra phi-3.5-mini) yazıyordu. Ancak bu bilgisayarda çalışabilecek
boyuttaki modeller Türkçe cümle kurmada tutarsız kaldı: bozuk cümleler
üretti, bazen alakasız bilgi uydurdu ve cevap süresi uzundu.

Bu yüzden yaklaşım değiştirildi: cevabı model yazmak yerine, bilgi
bankasındaki en uygun cümle bulunup olduğu gibi gösteriliyor. Bu
yöntem hem çok daha hızlı hem de her zaman düzgün Türkçe cevap veriyor.
Bu yaklaşıma "extractive" (alıntılayarak cevap verme) denir.

## Kullanılan Teknolojiler

- **Python** – projenin yazıldığı programlama dili
- **Microsoft Foundry Local** – yapay zeka modellerini internetsiz
  çalıştıran motor
- **qwen3-embedding-0.6b** – metni sayıya çeviren gömme (embedding)
  modeli
- **SQLite** – belgeleri ve gömme vektörlerini saklayan yerel veritabanı
- **NumPy** – benzerlik hesaplamaları için kullanılan matematik
  kütüphanesi
- **Tkinter** – masaüstü arayüzü için kullanılan, Python ile birlikte
  hazır gelen kütüphane
- **VS Code** – projenin geliştirildiği kod düzenleyici

## Proje Dosyaları

- `belgeler/` – yemek pişirme hakkında 6 adet bilgi belgesi (.txt)
- `veri_al.py` – belgeleri okuyup veritabanına kaydeden program
- `arayuz.py` – ana program: arama mantığını ve masaüstü penceresini
  içerir
- `bilgi_bankasi.db` – belgelerin saklandığı veritabanı
- `asistan.py` – arayüzden önce yazılmış, terminalde çalışan ilk
  sürüm (sohbet modelli)
- `arama.py`, `benzerlik_test.py`, `embedding_test.py`, `test.py`,
  `veritabani_test.py`, `belgelerim.db` – geliştirme sürecinde adım adım
  denediğim küçük test dosyaları

## Nasıl Çalıştırılır?

1. Gerekli kütüphaneleri kur (bir kere yapılır):
```
   pip install foundry-local-sdk numpy
```

2. Belgeleri veritabanına yükle (belgeler değiştiğinde tekrar çalıştır):
```
   python veri_al.py
```

3. Asistanı başlat (masaüstü penceresi açılır):
```
   python arayuz.py
```

4. Açılan pencerede soru kutusuna yaz, Enter'a bas veya "Sor"
   butonuna tıkla.

## Bilinen Sınırlamalar

- Cevaplar serbest bir sohbet cümlesi değil, belgelerden alınmış
  cümlelerdir. Bilgi bankasında olmayan bir şey sorulursa asistan
  "bilgim yok" der.
- Asistan sadece bilgi bankasındaki 6 belgeyle sınırlıdır. Daha fazla
  konuyu bilmesi için yeni belgeler eklenip `veri_al.py` tekrar
  çalıştırılmalıdır.
- Benzerlik eşiği (0.30) elle belirlenmiş bir değerdir. Farklı belge
  setlerinde farklı bir eşik daha iyi sonuç verebilir.
- Belgeler değiştirilirse, güncel hâlini görmesi için `arayuz.py`
  yeniden başlatılmalıdır.

## Öğrenilen Dersler

- Embedding'ler, kelime eşleşmesi olmasa bile anlamca yakın metinleri
  bulabiliyor (örneğin "programlama dili" sorusu "Python" cümlesini
  buldu).
- En yüksek benzerlik skorunu bir eşikle karşılaştırmak, alakasız
  sorularda "bilmiyorum" demeyi ve yanlış bilgi uydurmayı (halüsinasyon)
  önlemeyi sağlıyor.
- Küçük yapay zeka modelleri hızlı ve pratik olsa da, Türkçe gibi
  dillerde serbest cümle kurmada zayıf kalabiliyor. Talimatları
  değiştirmek yetmediğinde, modeli hiç kullanmayan bir yaklaşıma
  geçmek daha güvenilir sonuç verdi.
- Kurulum sürecinde karşılaşılan sorunlar (winget çalışmaması, PATH
  ayarları, API'nin sürümden sürüme değişmesi) gerçek yazılım
  geliştirmenin doğal bir parçası. Belgelenmiş örnekler her zaman
  bilgisayardaki gerçek duruma birebir uymayabiliyor.