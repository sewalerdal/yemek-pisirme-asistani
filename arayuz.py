import sqlite3
import json
import numpy as np
import tkinter as tk
from tkinter import scrolledtext
from foundry_local_sdk import Configuration, FoundryLocalManager

print("Foundry Local başlatılıyor, lütfen bekleyin...")
config = Configuration(app_name="rag_projem")
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance

embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
embedding_model.download(lambda progress: None)
embedding_model.load()
embedding_client = embedding_model.get_embedding_client()

sohbet_model = manager.catalog.get_model("phi-3.5-mini")
sohbet_model.download(lambda progress: None)
sohbet_model.load()
sohbet_client = sohbet_model.get_chat_client()

print("Modeller hazır, pencere açılıyor!")

BENZERLIK_ESIGI = 0.28

# ---- RENK TEMASI ----
ARKA_PLAN = "#F1F8F0"       # açık yeşilimsi ana arka plan
BASLIK_RENGI = "#2E7D32"    # koyu yeşil başlık
KULLANICI_RENGI = "#1B5E20" # koyu orman yeşili (kullanıcı yazısı)
ASISTAN_RENGI = "#558B2F"   # açık zeytin yeşili (asistan yazısı)
BUTON_RENGI = "#2E7D32"


def benzerlik_hesapla(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def en_alakali_belgeleri_bul(soru, kac_tane=1):
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
    bulunanlar = en_alakali_belgeleri_bul(soru, kac_tane=1)

    en_yuksek_skor = bulunanlar[0][0]
    if en_yuksek_skor < BENZERLIK_ESIGI:
        return "Bu konuda bilgim yok. Sadece yemek pişirme hakkında sorular sorabilirsiniz.", []

    birlesik_bilgi = bulunanlar[0][2]
    kaynaklar = [bulunanlar[0][1]]

    sistem_mesaji = (
        "Sen bir yemek pişirme asistanısın. Sana bir BİLGİ metni verilecek. "
        "Görevin, bu metni OLDUĞU GİBİ, kelimeleri neredeyse hiç değiştirmeden "
        "kullanıcıya aktarmak. Yeni cümle kurma, yorum katma, ekleme yapma. "
        "Sadece BİLGİ metnindeki cümleleri, soruya en uygun sırayla tekrar yaz. "
        "Eğer BİLGİ, soruyla hiç alakalı değilse, 'Bu konuda bilgim yok' de.\n\n"
        f"BİLGİ: {birlesik_bilgi}"
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

    return kisa_cevap, kaynaklar


# ---- PENCERE (GUI) KISMI ----

def cevapla():
    soru = giris_kutusu.get()
    if soru.strip() == "":
        return

    cevap_alani.config(state=tk.NORMAL)
    cevap_alani.insert(tk.END, "Siz: ", "kullanici_etiket")
    cevap_alani.insert(tk.END, f"{soru}\n", "kullanici_metin")
    cevap_alani.config(state=tk.DISABLED)

    giris_kutusu.delete(0, tk.END)
    pencere.update()

    cevap, kaynaklar = soru_sor(soru)

    cevap_alani.config(state=tk.NORMAL)
    cevap_alani.insert(tk.END, "🍳 Asistan: ", "asistan_etiket")
    cevap_alani.insert(tk.END, f"{cevap}\n", "asistan_metin")
    if kaynaklar:
        cevap_alani.insert(tk.END, f"   (Kaynak: {', '.join(kaynaklar)})\n\n", "kaynak_metin")
    else:
        cevap_alani.insert(tk.END, "\n")
    cevap_alani.config(state=tk.DISABLED)
    cevap_alani.see(tk.END)


pencere = tk.Tk()
pencere.title("Yemek Pişirme Asistanı")
pencere.geometry("550x600")
pencere.configure(bg=ARKA_PLAN)

# ---- ÜST BAŞLIK ALANI ----
baslik_cercevesi = tk.Frame(pencere, bg=BASLIK_RENGI, height=80)
baslik_cercevesi.pack(fill=tk.X)
baslik_cercevesi.pack_propagate(False)

baslik_etiketi = tk.Label(
    baslik_cercevesi,
    text="🍳 Yemek Pişirme Asistanı 👨‍🍳",
    font=("Arial", 18, "bold"),
    bg=BASLIK_RENGI,
    fg="white"
)
baslik_etiketi.pack(expand=True)

# ---- SOHBET ALANI ----
cevap_alani = scrolledtext.ScrolledText(
    pencere,
    wrap=tk.WORD,
    font=("Segoe UI", 11),
    bg="white",
    relief=tk.FLAT,
    padx=10,
    pady=10,
    state=tk.DISABLED
)
cevap_alani.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

# Yazı renklerini tanımlıyoruz (etiketler)
cevap_alani.tag_config("kullanici_etiket", foreground=KULLANICI_RENGI, font=("Segoe UI", 11, "bold"))
cevap_alani.tag_config("kullanici_metin", foreground=KULLANICI_RENGI, font=("Segoe UI", 11))
cevap_alani.tag_config("asistan_etiket", foreground=ASISTAN_RENGI, font=("Segoe UI", 11, "bold"))
cevap_alani.tag_config("asistan_metin", foreground="#333333", font=("Segoe UI", 11))
cevap_alani.tag_config("kaynak_metin", foreground="#999999", font=("Segoe UI", 9, "italic"))

# ---- ALT GİRİŞ ALANI ----
alt_cerceve = tk.Frame(pencere, bg=ARKA_PLAN)
alt_cerceve.pack(padx=15, pady=(0, 15), fill=tk.X)

giris_kutusu = tk.Entry(
    alt_cerceve,
    font=("Segoe UI", 12),
    relief=tk.SOLID,
    borderwidth=1
)
giris_kutusu.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))
giris_kutusu.bind("<Return>", lambda event: cevapla())
giris_kutusu.focus()

gonder_butonu = tk.Button(
    alt_cerceve,
    text="Sor ➤",
    command=cevapla,
    font=("Segoe UI", 11, "bold"),
    bg=BUTON_RENGI,
    fg="white",
    relief=tk.FLAT,
    padx=15,
    cursor="hand2"
)
gonder_butonu.pack(side=tk.RIGHT)

pencere.mainloop()