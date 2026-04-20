# 💎 Lumina AI Academy — Akıllı Öğrenme Deneyimi

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live%20&%20Stable-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/UI-Premium%20Warm-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/AI-Gemini%201.5%20Flash-4285F4?style=for-the-badge" />
</p>

Lumina AI Academy, öğrenme süreçlerini yapay zeka ile modernize eden, kişiselleştirilmiş ve zekice tasarlanmış bir Eğitim Yönetim Sistemidir (LMS). Bu platform, karmaşık müfredat süreçlerini saniyeler içinde zengin içerikli derslere dönüştürür.

---

## 🌐 CANLI UYGULAMA (Live Demo)
Uygulamanın en güncel ve kararlı sürümüne aşağıdaki adresten ulaşabilirsiniz:
👉 **[Lumina AI Academy Canlı İzle](https://lms-yapayzeka-130-ebii.streamlit.app/)**

---

## ✨ ÖNE ÇIKAN YENİLİKLER (V2.0)

- 🎨 **Premium UI:** Zihne hitap eden sıcak krem ve altın tonlarından oluşan "Buzlu Cam" (Glassmorphism) arayüz.
- 🚀 **AI Kurs Mimarı:** Herhangi bir konuyu girin, zekice bir ders planı ve içerikler saniyeler içinde hazırlansın.
- 📚 **Kişisel Kütüphane:** Oluşturulan tüm kurslara anında erişim ve ders takibi.
- 📑 **Akıllı Raporlama:** Kurs içeriklerini Türkçe karakter destekli profesyonel PDF formatında indirme imkanı.
- 🛡️ **Stabilite Garantisi:** Modeller arası otomatik 'Fallback' (Yedeğe Geçiş) sistemi ile kesintisiz hizmet.

---

## 📂 PROJE MİMARİSİ (Ağaç Modeli)

```text
Lumina-AI-Academy/
├── 📄 streamlit_app.py       # 🚀 ANA UYGULAMA (Monolitik / Profesyonel UI)
├── 📄 requirements.txt       # 📦 Bağımlılıklar (google-generativeai==0.7.2)
├── 📄 .env                   # 🔑 API Güvenlik Anahtarları
├── 📄 lms_prod.db            # 🗄️ Üretim Veritabanı (SQLite)
├── 📄 DejaVuSans.ttf         # 🖋️ PDF Türkçe Font Desteği
└── 🛠️ Dağıtık Sistem Dosyaları (Backend/Frontend Ayrık Kullanım İçin)
    ├── main.py, app.py, ai_service.py, models.py, database.py
```

---

## 🛠️ TEKNOLOJİ YIĞINI

| Katman | Teknoloji |
|---|---|
| **Frontend/Backend** | [Streamlit](https://streamlit.io/) & Python 3.10+ |
| **Yapay Zeka** | Google Gemini 1.5 & Groq Llama 3.3 |
| **Veritabanı** | SQLAlchemy & SQLite |
| **Dökümantasyon** | FPDF2 (UTF-8 Destekli) |
| **Styling** | Custom Premium CSS (Warm Theme) |

---

## 🚀 HIZLI BAŞLANGIÇ

1. **Bağımlılıkları Kur:** `pip install -r requirements.txt`
2. **API Anahtarlarını Ayarla:** `.env` dosyasına `GEMINI_API_KEY` ve `GROQ_API_KEY` bilgilerini ekle.
3. **Başlat:** `streamlit run streamlit_app.py`

---

## ✍️ GELİŞTİRİCİ
Bu proje **ZEYNEP EBRAR PALA** tarafından, eğitim teknolojilerini yapay zeka ile bir üst seviyeye taşımak amacıyla geliştirilmiştir. Modern tasarımı ve teknik sağlamlığı ile yayındadır.

---
<p align="center"><i>© 2026 Lumina AI Academy - Developed with ❤️ by Zeynep Ebrar Pala</i></p>
