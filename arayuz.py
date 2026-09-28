import re
import sqlite3
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

# Bu skorun altındaki sonuçlar "alakasız" kabul edilir
BENZERLIK_ESIGI = 0.30

# ---- RENK TEMASI ----
ARKA_PLAN = "#F1F8F0"
BASLIK_RENGI = "#2E7D32"
KULLANICI_RENGI = "#1B5E20"
ASISTAN_RENGI = "#558B2F"
BUTON_RENGI = "#2E7D32"


def vektor_al(metin):
    v = np.array(embedding_client.generate_embedding(metin).data[0].embedding)
    return v / np.linalg.norm(v)  # uzunluğa bölüp normalize ediyoruz


# ---- AÇILIŞTA: belgeleri cümlelere böl ve her cümlenin embedding'ini çıkar ----
def cumleleri_hazirla():
    baglanti = sqlite3.connect("bilgi_bankasi.db")
    imlec = baglanti.cursor()
    imlec.execute("SELECT dosya_adi, icerik FROM belgeler")
    belgeler = imlec.fetchall()
    baglanti.close()

    cumleler = []   # (dosya_adi, cumle) listesi
    for dosya_adi, icerik in belgeler:
        parcalar = re.split(r"(?<=[.!?])\s+", icerik.strip())
        for parca in parcalar:
            if len(parca.strip()) > 10:
                cumleler.append((dosya_adi, parca.strip()))

    print(f"{len(cumleler)} cümle hazırlanıyor...")
    matris = np.array([vektor_al(c[1]) for c in cumleler])
    return cumleler, matris


CUMLELER, CUMLE_MATRISI = cumleleri_hazirla()
print("Hazır, pencere açılıyor!")


def soru_sor(soru):
    soru_vektor = vektor_al(soru)
    skorlar = CUMLE_MATRISI @ soru_vektor

    sirali = np.argsort(skorlar)[::-1]
    en_iyi = sirali[0]
    en_yuksek_skor = float(skorlar[en_iyi])

    if en_yuksek_skor < BENZERLIK_ESIGI:
        return "Bu konuda bilgim yok. Sadece yemek pişirme hakkında sorular sorabilirsiniz.", "", en_yuksek_skor

    secilenler = [en_iyi]

    # İkinci en iyi cümle de neredeyse aynı derecede alakalıysa ve aynı belgedense onu da ekle
    ikinci = sirali[1]
    if (skorlar[ikinci] >= 0.85 * en_yuksek_skor
            and CUMLELER[ikinci][0] == CUMLELER[en_iyi][0]):
        secilenler.append(ikinci)

    secilenler.sort()  # belgedeki orijinal sıraya göre diz
    cevap = " ".join(CUMLELER[i][1] for i in secilenler)
    kaynak = CUMLELER[en_iyi][0]

    return cevap, kaynak, en_yuksek_skor


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

    cevap, kaynak, skor = soru_sor(soru)

    cevap_alani.config(state=tk.NORMAL)
    cevap_alani.insert(tk.END, "🍳 Asistan: ", "asistan_etiket")
    cevap_alani.insert(tk.END, f"{cevap}\n", "asistan_metin")
    if kaynak:
        cevap_alani.insert(
            tk.END,
            f"   (Kaynak: {kaynak}, benzerlik: {skor:.2f})\n\n",
            "kaynak_metin"
        )
    else:
        cevap_alani.insert(tk.END, "\n")
    cevap_alani.config(state=tk.DISABLED)
    cevap_alani.see(tk.END)


pencere = tk.Tk()
pencere.title("Yemek Pişirme Asistanı")
pencere.geometry("550x600")
pencere.configure(bg=ARKA_PLAN)

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

cevap_alani.tag_config("kullanici_etiket", foreground=KULLANICI_RENGI, font=("Segoe UI", 11, "bold"))
cevap_alani.tag_config("kullanici_metin", foreground=KULLANICI_RENGI, font=("Segoe UI", 11))
cevap_alani.tag_config("asistan_etiket", foreground=ASISTAN_RENGI, font=("Segoe UI", 11, "bold"))
cevap_alani.tag_config("asistan_metin", foreground="#333333", font=("Segoe UI", 11))
cevap_alani.tag_config("kaynak_metin", foreground="#999999", font=("Segoe UI", 9, "italic"))

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