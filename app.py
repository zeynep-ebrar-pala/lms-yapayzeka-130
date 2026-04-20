import streamlit as st
import requests
import json
import time
from fpdf import FPDF
import io
import os

# --- Page Config ---
st.set_page_config(page_title="AI LMS - Yapay Zeka Destekli Eğitim Sistemi", layout="wide")

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
        border: 2px solid white;
    }
    .sidebar .sidebar-content {
        background-color: #1a1c24;
    }
    h1, h2, h3 {
        color: #00d2ff;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e2130;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    .lesson-content {
        line-height: 1.6;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Backend Config ---
API_BASE_URL = "http://localhost:8000"

# --- PDF Generation Function ---
class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Title
        self.cell(0, 10, 'Kurs Raporu - AI LMS', 0, 1, 'C')
        # Line break
        self.ln(10)

def generate_pdf(course_title, lessons):
    pdf = PDF()
    pdf.add_page()
    
    font_file = "DejaVuSans.ttf"
    if not os.path.exists(font_file):
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/DejaVuSans.ttf"
            urllib.request.urlretrieve(url, font_file)
        except Exception as e:
            pass

    if os.path.exists(font_file):
        pdf.add_font("DejaVu", "", font_file)
        pdf.set_font("DejaVu", size=16)
        font_name = "DejaVu"
    else:
        pdf.set_font("Arial", size=16)
        font_name = "Arial"

    pdf.cell(0, 10, f"Kurs: {course_title}", ln=True, align='L')
    pdf.ln(5)
    
    pdf.set_font(font_name, size=12)
    for lesson in lessons:
        pdf.set_font(font_name, size=14)
        pdf.cell(0, 10, f"Ders {lesson['order']}: {lesson['title']}", ln=True)
        pdf.set_font(font_name, size=11)
        content = lesson['content'].replace('#', '').replace('*', '').replace('`', '')
        pdf.multi_cell(0, 10, content)
        pdf.ln(10)
        
    return pdf.output()

# --- Auth Logic ---
if "user" not in st.session_state:
    st.session_state["user"] = None

def login_register_page():
    st.title("👤 AI LMS Giriş & Kayıt")
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        l_username = st.text_input("Kullanıcı Adı", key="l_user")
        l_password = st.text_input("Şifre", type="password", key="l_pass")
        if st.button("Giriş Yap"):
            try:
                res = requests.post(f"{API_BASE_URL}/login/", json={"username": l_username, "password": l_password})
                if res.status_code == 200:
                    st.session_state["user"] = res.json()
                    st.success("Başarıyla giriş yapıldı!")
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı.")
            except:
                st.error("Backend bağlantısı kurulamadı.")
                
    with tab2:
        r_username = st.text_input("Kullanıcı Adı", key="r_user")
        r_email = st.text_input("E-posta", key="r_email")
        r_password = st.text_input("Şifre", type="password", key="r_pass")
        if st.button("Kayıt Ol"):
            try:
                res = requests.post(f"{API_BASE_URL}/register/", json={"username": r_username, "email": r_email, "password": r_password})
                if res.status_code == 200:
                    st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
                else:
                    st.error(res.json().get("detail", "Kayıt sırasında hata oluştu."))
            except:
                st.error("Backend bağlantısı kurulamadı.")

# --- Main App ---
if st.session_state["user"] is None:
    login_register_page()
else:
    user = st.session_state["user"]
    
    # --- Sidebar ---
    with st.sidebar:
        st.title(f"🎓 Merhaba, {user['username']}")
        menu = ["🏠 Ana Sayfa", "🤖 AI Kurs Mimarı", "📚 Kurslarım"]
        choice = st.selectbox("Menü", menu)
        
        st.divider()
        st.subheader("⚙️ Yapay Zeka Ayarları")
        provider = st.radio("Varsayılan LLM Sağlayıcısı", ["gemini", "groq"])
        st.info(f"{provider.capitalize()} API Kullanılıyor")
        
        if st.button("Çıkış Yap"):
            st.session_state["user"] = None
            st.rerun()

    # --- Choice Logic ---
    if choice == "🏠 Ana Sayfa":
        st.title("Yeni Nesil Yapay Zeka LMS'e Hoş Geldiniz")
        st.markdown(f"""
        Bu platform, kişiselleştirilmiş öğrenme deneyimleri oluşturmak için en yeni büyük dil modellerini (LLM) kullanır.
        
        Hoş geldin **{user['username']}**! Bugün ne öğrenmek istersin?
        
        ### ✨ Özellikler:
        - **Anında Kurs Oluşturma**: Herhangi bir konuyu yapılandırılmış bir kursa dönüştürün.
        - **AI Eğitmenler**: Sektör lideri modeller tarafından yazılan ders içerikleri.
        - **PDF Raporlama**: Kurslarınızı Türkçe karakter desteğiyle indirilebilir formatta kaydedin.
        """)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sağlayıcılar", "Gemini, Groq")
        with col2:
            st.metric("Veritabanı", "SQLite")
        with col3:
            st.metric("Geliştiren", "ZEYNEP EBRAR PALA")

    elif choice == "🤖 AI Kurs Mimarı":
        st.title("Yapay Zeka ile Yeni Kurs Oluştur")
        topic = st.text_input("Öğrenmek istediğiniz konuyu girin:", placeholder="Örn: Yeni Başlayanlar için Kuantum Programlama")
        
        if st.button("🚀 Kurs Müfredatı Oluştur"):
            if topic:
                with st.spinner("✨ Yapay zeka kursunuzu tasarlıyor... Bu bir dakika sürebilir."):
                    try:
                        payload = {"topic": topic, "provider": provider}
                        params = {"user_id": user["user_id"]}
                        response = requests.post(f"{API_BASE_URL}/generate-course/", json=payload, params=params)
                        if response.status_code == 200:
                            st.success("🎉 Kurs başarıyla oluşturuldu!")
                            st.balloons()
                        else:
                            st.error(f"Hata: {response.text}")
                    except Exception as e:
                        st.error(f"Backend bağlantısı başarısız: {e}")
            else:
                st.warning("Lütfen bir konu başlığı girin.")

    elif choice == "📚 Kurslarım":
        st.title("Öğrenme Yolculuğunuz")
        
        try:
            courses_res = requests.get(f"{API_BASE_URL}/courses/")
            if courses_res.status_code == 200:
                courses = courses_res.json()
                if not courses:
                    st.info("Henüz kurs oluşturmadınız. Başlamak için 'AI Kurs Mimarı' sekmesine gidin.")
                else:
                    selected_course_title = st.selectbox("Bir kurs seçin:", [c['title'] for c in courses])
                    course_id = [c['id'] for c in courses if c['title'] == selected_course_title][0]
                    
                    # Fetch details
                    detail_res = requests.get(f"{API_BASE_URL}/course/{course_id}")
                    if detail_res.status_code == 200:
                        data = detail_res.json()
                        
                        col_h, col_d = st.columns([3, 1])
                        with col_h:
                            st.header(f"📖 {data['course']['title']}")
                        with col_d:
                            # PDF Download
                            try:
                                pdf_data = generate_pdf(data['course']['title'], data['lessons'])
                                st.download_button(
                                    label="📑 Raporu İndir (PDF)",
                                    data=bytes(pdf_data),
                                    file_name=f"{data['course']['title'].replace(' ', '_')}_Raporu.pdf",
                                    mime="application/pdf"
                                )
                            except Exception as e:
                                st.warning(f"PDF oluşturulamadı: {e}")

                        st.caption(data['course']['description'])
                        st.divider()
                        
                        tabs = st.tabs([f"Ders {l['order']}: {l['title']}" for l in data['lessons']])
                        
                        for i, tab in enumerate(tabs):
                            with tab:
                                lesson = data['lessons'][i]
                                st.write(lesson['content'])
            else:
                st.error("Kurslar getirilemedi.")
        except Exception as e:
            st.error(f"Backend çevrimdışı: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("ZEYNEP EBRAR PALA tarafından geliştirildi | AI LMS Sistemi")
