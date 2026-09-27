# Yerel Yemek Pişirme Asistanı (RAG Projesi)

## Bu Proje Nedir?

Bu, tamamen kendi bilgisayarımda çalışan, internet gerektirmeyen bir 
Soru-Cevap yapay zeka asistanıdır. Yemek pişirme konusunda hazırladığım 
küçük bir bilgi bankasından yararlanarak sorularımı yanıtlar ve basit 
bir masaüstü penceresi üzerinden kullanılır.

Sistem, **RAG (Retrieval-Augmented Generation)** adı verilen bir yöntem 
kullanır: Önce sorulan soruyla en alakalı bilgiyi kendi belgelerimden 
bulur, sonra bu bilgiyi yapay zeka modeline vererek doğru ve kaynağa 
dayalı bir cevap üretmesini sağlar.

## Nasıl Çalışır?

1. Kullanıcı, açılan pencereden bir soru yazar
2. Soru, sayısal bir forma (embedding) çevrilir
3. Bu sayısal form, veritabanındaki belgelerin sayısal formlarıyla 
   karşılaştırılır (kosinüs benzerliği ile)
4. En alakalı belge bulunur
5. **Eğer en yüksek benzerlik skoru belirli bir eşiğin altındaysa**, 
   model hiç çağrılmadan doğrudan "Bu konuda bilgim yok" cevabı verilir 
   (alakasız sorularda yanlış bilgi uydurmayı önlemek için)
6. Eşiğin üstündeyse, bulunan belge, soru ile birlikte yerel bir dil 
   modeline gönderilir
7. Model, belgedeki bilgiyi neredeyse hiç değiştirmeden, olduğu gibi 
   aktararak cevap üretir (küçük modelin kendi cümle kurmaya çalışıp 
   tutarsız/anlamsız metin üretmesini önlemek için)

## Kullanılan Teknolojiler

- **Python** – projenin yazıldığı programlama dili
- **Microsoft Foundry Local** – yapay zeka modellerini internetsiz 
  çalıştıran motor
- **phi-3.5-mini** – cevap üreten dil modeli
- **qwen3-embedding-0.6b** – metni sayıya çeviren gömme modeli
- **SQLite** – belgeleri ve gömme vektörlerini saklayan yerel veritabanı
- **NumPy** – benzerlik hesaplamaları için kullanılan matematik kütüphanesi
- **Tkinter** – masaüstü arayüzü (pencere, buton, yazı kutusu) için 
  kullanılan, Python ile birlikte hazır gelen kütüphane
- **VS Code** – projenin geliştirildiği kod düzenleyici

## Proje Dosyaları

- `belgeler/` – yemek pişirme hakkında 6 adet bilgi belgesi (.txt)
- `veri_al.py` – belgeleri okuyup veritabanına kaydeden program
- `arayuz.py` – ana program: hem Soru-Cevap mantığını hem de masaüstü 
  penceresini içerir
- `bilgi_bankasi.db` – belgelerin ve embedding'lerinin saklandığı veritabanı

## Nasıl Çalıştırılır?

1. Gerekli kütüphaneleri kur (bir kere yapılır):

2. Belgeleri veritabanına yükle (belgeler değiştiğinde tekrar çalıştır):

3. Asistanı başlat (masaüstü penceresi açılır):

4. Açılan pencerede soru kutusuna yaz, Enter'a bas veya "Sor" butonuna tıkla.

## Bilinen Sınırlamalar

- Kullanılan dil modeli (phi-3.5-mini), büyük bulut tabanlı modellere 
  (ChatGPT gibi) göre daha küçük olduğu için, serbestçe cümle kurması 
  istendiğinde Türkçe'de tutarsız sonuçlar üretebiliyor. Bu yüzden 
  modelden "kendi cümlelerini kurması" yerine "belgedeki bilgiyi olduğu 
  gibi aktarması" istendi.
- Arama sistemi, sadece **en iyi 1 belgeyi** kullanıyor; bazen doğru 
  cevap birden fazla belgeye dağılmış olabilir.
- Belge sayısı arttıkça (yüzlerce belge), şu anki basit arama yöntemi 
  yavaşlayabilir; daha büyük projelerde özel vektör veritabanları 
  gerekebilir.
- Benzerlik eşiği (0.28) elle belirlenmiş bir değerdir; farklı belge 
  setlerinde farklı bir eşik daha iyi sonuç verebilir.

## Öğrenilen Dersler

- Embedding'ler, kelime eşleşmesi olmasa bile anlamca yakın metinleri 
  bulabiliyor (örneğin "programlama dili" sorusu "Python" cümlesini 
  buldu).
- RAG sistemi, modelin bilmediği bir konuda "bilmiyorum" demesini 
  sağlayarak yanlış bilgi uydurmasını (halüsinasyon) önleyebiliyor.
- En yüksek benzerlik skorunu bir eşikle karşılaştırmak, alakasız 
  sorularda modeli hiç çağırmadan güvenli bir cevap vermeyi sağlıyor.
- Küçük yapay zeka modelleri hızlı ve pratik olsa da, serbest cümle 
  kurma konusunda zayıf kalabiliyor; bu gibi durumlarda modele "yaratıcı 
  olma, sadece verilen bilgiyi aktar" gibi kısıtlayıcı talimatlar vermek 
  sonucu iyileştirebiliyor.
- Kurulum sürecinde karşılaşılan sorunlar (winget çalışmaması, PATH 
  ayarları, API'nin sürümden sürüme değişmesi) gerçek yazılım 
  geliştirmenin doğal bir parçası; belgelenmiş örnekler her zaman 
  bilgisayardaki gerçek duruma birebir uymayabiliyor.
  