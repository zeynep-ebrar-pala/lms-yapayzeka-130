# 🎓 AI-Powered LMS — Yapay Zeka Destekli Akıllı Eğitim Platformu

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white" />
</p>

> **Geliştiren:** ZEYNEP EBRAR PALA  
> **Vizyon:** Herkes için, her an, her konuda kişiselleştirilmiş dijital akademi.

---

## 📂 PROJE YAPISI (Tree Model)

```text
lms-yapayzeka-130/
├── 📄 streamlit_app.py       # ⭐ ANA UYGULAMA (Tek dosya - Canlı yayın/Deploy için)
├── 📄 requirements.txt       # Gerekli kütüphaneler (pip install -r ...)
├── 📄 .env                   # 🔑 API Anahtarları (Sadece burada tutulur)
├── 📄 .gitignore             # Güvenlik için hariç tutulan dosyalar
├── 📁 .pycache               # Python çalışma önbelleği
│
├── 🛠️ GELİŞMİŞ MİMARİ (Backend & Frontend Ayrı)
│   ├── main.py               # FastAPI Backend Sunucusu (REST API)
│   ├── app.py                # Streamlit Frontend (API üzerinden çalışır)
│   ├── ai_service.py         # AI Servis Katmanı (Gemini 1.5 & Groq)
│   ├── models.py             # Veritabanı Şemaları (User, Course, Lesson)
│   └── database.py           # SQL Bağlantı Yönetimi
│
├── 🗄️ VERİTABANI
│   └── lms.sqlite            # SQLite Veritabanı Dosyası
└── 📖 README.md              # Proje Dökümantasyonu
```

---

## 🌟 PROJE ÖZETİ VE MANTIK AKIŞI

Bu sistem, karmaşık eğitim süreçlerini yapay zeka yardımıyla otomatikleştirir. Projede iki farklı çalışma mantığı sunulmuştur:

1.  **Hızlı Yayın (Monolitik):** `streamlit_app.py` dosyası her şeyi (arayüz, veritabanı, AI) içinde barındırır. Streamlit Cloud gibi platformlarda saniyeler içinde yayına almak için tasarlanmıştır.
2.  **Profesyonel Mimari (Dağıtık):** `main.py` (Backend) ve `app.py` (Frontend) ayrılmıştır. Bu sayede sistem ölçeklenebilir ve farklı arayüzlere (mobil uygulama vb.) hizmet verebilir hale getirilmiştir.

---

## ✨ ÖNE ÇIKAN ÖZELLİKLER

| Özellik | Teknik Detay |
|---|---|
| 🧠 **Zeki Müfredat** | Google Gemini 1.5 Flash ile saniyeler içinde konu analizi ve ders planı. |
| ⚡ **Yıldırım Hızı** | Groq Llama 3.3 entegrasyonu ile anlık içerik üretimi. |
| 🔐 **Maksimum Güvenlik** | API anahtarları asla kodda tutulmaz, `.env` veya `Secrets` üzerinden okunur. |
| 📄 **Eğitim Raporu** | Oluşturulan kurslar tek tıkla PDF formatında indirilebilir. |
| 🌓 **Modern UI** | Koyu tema (Dark Mode) odaklı, kullanıcı dostu premium arayüz. |

---

## 🚀 KURULUM VE BAŞLATMA

### 1. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 2. API Anahtarlarını Ayarlayın
Proje dizinindeki `.env` dosyasını açın ve anahtarlarınızı girin:
```env
GEMINI_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
```

### 3. Uygulamayı Çalıştırın

**Seçenek A: Tek Dosya (Önerilen/Hızlı)**
```bash
streamlit run streamlit_app.py
```

**Seçenek B: Dağıtık Sistem (Backend + Frontend)**
```bash
# Terminal 1:
python main.py

# Terminal 2:
streamlit run app.py
```

---

## ☁️ STREAMLIT CLOUD'DA YAYINLAMA (DEPLOY)

1.  GitHub'a projenizi yükleyin.
2.  Streamlit Cloud'da yeni uygulama oluşturun ve `streamlit_app.py` dosyasını seçin.
3.  **Advanced Settings > Secrets** kısmına `.env` içindeki anahtarları eklemeyi unutmayın!

---

## ⚠️ GÜVENLİK VE GİZLİLİK

*   **API Anahtarları:** Proje kodları içinde hiçbir API anahtarı barındırılmaz. Tüm anahtarlar `os.getenv` ile güvenli şekilde çekilir.
*   **Veri Saklama:** Kullanıcı şifreleri `SHA-256` ile özetlenerek (hash) saklanır, asla açık metin olarak tutulmaz.

---

## ✍️ LİSANS VE GELİŞTİRİCİ
Bu proje **ZEYNEP EBRAR PALA** tarafından eğitim teknolojilerinde yapay zeka kullanımını modernize etmek amacıyla geliştirilmiştir. Tüm hakları saklıdır.
