import streamlit as st
import hashlib
import os
import time
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from fpdf import FPDF
import google.generativeai as genai
from groq import Groq

# --- Constants & Configuration ---
DB_URL = "sqlite:///./lms_prod.db"
Base = declarative_base()
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- AI Service (Embedded Keys) ---
class AIService:
    def __init__(self, provider="gemini"):
        self.provider = provider
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        try:
            if hasattr(st, "secrets"):
                if "GEMINI_API_KEY" in st.secrets:
                    self.gemini_key = st.secrets["GEMINI_API_KEY"]
                if "GROQ_API_KEY" in st.secrets:
                    self.groq_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        if self.groq_key:
            self.groq_client = Groq(api_key=self.groq_key)

    def generate_content(self, prompt, model_name=None):
        try:
            if self.provider == "gemini":
                if not self.gemini_key:
                    return "Hata: GEMINI_API_KEY bulunamadı. Lütfen .env dosyasını veya Streamlit Secrets ayarlarını kontrol edin."
                model = genai.GenerativeModel(model_name or 'gemini-1.5-flash')
                response = model.generate_content(prompt)
                return response.text
            elif self.provider == "groq":
                if not self.groq_key:
                    return "Hata: GROQ_API_KEY bulunamadı. Lütfen .env dosyasını veya Streamlit Secrets ayarlarını kontrol edin."
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model_name or "llama-3.3-70b-versatile",
                )
                return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Hata: {str(e)}"

    def generate_course_curriculum(self, topic):
        prompt = f"""
        Konu: {topic}
        Bu konu hakkında 5-7 derslik bir kurs müfredatı oluştur. 
        Yanıtı SADECE şu formatta geçerli bir JSON listesi olarak ver (başka yazı ekleme):
        [
            {{"order": 1, "title": "Ders Başlığı"}},
            ...
        ]
        """
        import json
        raw = self.generate_content(prompt)
        try:
            # Clean possible markdown code blocks
            clean_raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_raw)
        except:
            return [{"order": 1, "title": "Giriş"}]

    def generate_lesson_content(self, topic, lesson_title):
        prompt = f"""
        Kurs Konusu: {topic}
        Ders Başlığı: {lesson_title}
        Lütfen bu ders için eğitici, detaylı ve profesyonel bir içerik yaz. 
        Markdown formatını kullan. Türkçe karakterlere dikkat et.
        """
        return self.generate_content(prompt)

# --- Database Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    lessons = relationship("Lesson", back_populates="course")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    content = Column(Text)
    order = Column(Integer)
    course = relationship("Course", back_populates="lessons")

def init_db():
    Base.metadata.create_all(bind=engine)

# --- Helper Functions ---
def get_password_hash(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    return get_password_hash(plain_password) == hashed_password

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Kurs Raporu - AI LMS', 0, 1, 'C')
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
            pass # ignore failure and fallback to built-in

    if os.path.exists(font_file):
        pdf.add_font("DejaVu", "", font_file)
        # Sadece desteklediğimiz font varyantını (Regular) kullanacağız. Kalın/İtalik gerekiyorsa ayrı indirmek gerekir.
        # Basitlik için sadece Regular font kullanıp boyutu değiştirelim.
        pdf.set_font("DejaVu", size=16)
        font_name = "DejaVu"
    else:
        pdf.set_font("Arial", size=16)
        font_name = "Arial"

    pdf.ln(5)
    
    # PDF'de Türkçe karakter desteği için DejaVuSans standardı
    pdf.set_font(font_name, size=12)
    for lesson in lessons:
        pdf.set_font(font_name, size=14)
        # Arial durumunda Latin-1 karakter dönüşümü denemesi, DejaVu durumunda direkt yazım
        l_title = f"Ders {lesson.order}: {lesson.title}"
        pdf.cell(0, 10, l_title if font_name == "DejaVu" else l_title.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        pdf.set_font(font_name, size=11)
        content = lesson.content.replace('#', '').replace('*', '').replace('`', '')
        pdf.multi_cell(0, 10, content if font_name == "DejaVu" else content.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(10)
    return pdf.output()

# --- Streamlit UI App ---
def main():
    st.set_page_config(page_title="AI LMS - Zeynep Ebrar Pala", layout="wide", initial_sidebar_state="expanded")
    init_db()
    db = SessionLocal()

    # --- Custom Styling (Sıcak & Premium Tema) ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #fffcf9 0%, #f7e8d0 100%) !important;
            color: #4a4a4a;
        }
        
        .stApp {
            background-color: transparent;
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            margin-bottom: 25px;
        }

        h1, h2, h3 {
            color: #7d5a50 !important;
            font-weight: 600;
        }

        .stButton>button {
            border-radius: 12px;
            background: linear-gradient(45deg, #d4a373, #faedcd);
            color: #7d5a50;
            border: none;
            font-weight: 600;
            transition: all 0.3s ease;
            height: 3.5em;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            color: #fff;
            background: #d4a373;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(255, 252, 249, 0.9) !important;
            border-right: 1px solid #f2e1c1;
        }

        .nav-card {
            cursor: pointer;
            text-align: center;
            padding: 20px;
            background: #fff;
            border-radius: 15px;
            border: 1px solid #faedcd;
            transition: all 0.3s;
        }
        .nav-card:hover {
            background: #faedcd;
            transform: scale(1.02);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "menu_choice" not in st.session_state:
        st.session_state["menu_choice"] = "🏠 Ana Sayfa"

    if st.session_state["user"] is None:
        col_img, col_form = st.columns([1, 1])
        with col_img:
            st.markdown("""
            <div class='glass-card' style='margin-top: 50px;'>
                <h1 style='font-size: 3rem;'>🎓 Lumina AI</h1>
                <p style='font-size: 1.2rem; color: #8e7d77;'>Yeni Nesil <b>Yapay Zeka Destekli Öğrenme Platformu</b>'na hoş geldiniz.</p>
                <hr style='border: 0.5px solid #d4a373;'>
                <h3 style='margin-top: 20px;'>Neler Yapabilirsiniz?</h3>
                <ul style='list-style: none; padding-left: 0;'>
                    <li style='margin-bottom: 15px;'>🚀 <b>Hızlı Kurs Oluşturma:</b> Sadece konuyu söyleyin, müfredatınız hazır olsun.</li>
                    <li style='margin-bottom: 15px;'>🤖 <b>Yapay Zeka Eğitmenler:</b> En güncel modellerle etkileşimli içerikler.</li>
                    <li style='margin-bottom: 15px;'>📑 <b>Kişisel Kütüphane:</b> Tüm eğitimlerinizi saklayın ve PDF olarak indirin.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col_form:
            st.markdown("<div style='margin-top: 50px;'>", unsafe_allow_html=True)
            st.title("👤 Giriş Yap veya Kayıt Ol")
            tab1, tab2 = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol"])
            with tab1:
                l_user = st.text_input("Kullanıcı Adı", key="l_user")
                l_pass = st.text_input("Şifre", type="password", key="l_pass")
                if st.button("Hemen Başla"):
                    user = db.query(User).filter(User.username == l_user).first()
                    if user and verify_password(l_pass, user.hashed_password):
                        st.session_state["user"] = {"id": user.id, "username": user.username}
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Kullanıcı adı veya şifre hatalı.")
            with tab2:
                r_user = st.text_input("Kullanıcı Adı", key="r_user")
                r_email = st.text_input("E-posta", key="r_email")
                r_pass = st.text_input("Şifre", type="password", key="r_pass")
                if st.button("Hesabımı Oluştur"):
                    existing = db.query(User).filter(User.username == r_user).first()
                    if existing:
                        st.error("Bu kullanıcı adı zaten alınmış.")
                    else:
                        new_user = User(username=r_user, email=r_email, hashed_password=get_password_hash(r_pass))
                        db.add(new_user)
                        db.commit()
                        st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        user = st.session_state["user"]
        
        # --- Sidebar (Basitleştirilmiş) ---
        with st.sidebar:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <div style='font-size: 3rem;'>🧑‍🎓</div>
                <h2 style='margin-bottom: 0;'>Merhaba,</h2>
                <h1 style='color: #d4a373 !important;'>{user['username']}</h1>
            </div>
            """, unsafe_allow_html=True)
            st.divider()
            
            if st.button("🏠 Ana Sayfa", type="secondary"): 
                st.session_state["menu_choice"] = "🏠 Ana Sayfa"
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            provider = st.radio("⚡ Yapay Zeka Motoru", ["gemini", "groq"])
            
            st.divider()
            if st.button("🚪 Çıkış Yap"):
                st.session_state["user"] = None
                st.rerun()

        # --- Main Logic (Dashboard / Menu Choice) ---
        choice = st.session_state["menu_choice"]

        if choice == "🏠 Ana Sayfa":
            st.markdown(f"<h1>Lumina AI Academy</h1>", unsafe_allow_html=True)
            st.markdown("<div class='glass-card'><h3>Zekice Öğrenmeye Hemen Başlayın</h3>Öğrenmek istediğiniz başlığı yazın, saniyeler içinde size özel müfredat ve ders içerikleri hazırlayalım.</div>", unsafe_allow_html=True)
            
            # Aksiyon Kartları (Görsel Navigasyon)
            st.subheader("Hızlı Erişim")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("<div class='nav-card'><div class='feature-icon'>🚀</div><h3>Yeni Kurs Oluştur</h3>Yapay zeka ile saniyeler içinde müfredat hazırlayın.</div>", unsafe_allow_html=True)
                if st.button("Mimar'a Git", key="goto_mimar"): 
                    st.session_state["menu_choice"] = "🤖 AI Kurs Mimarı"
                    st.rerun()
            
            with col2:
                st.markdown("<div class='nav-card'><div class='feature-icon'>📚</div><h3>Kütüphanem</h3>Tamamladığınız ve devam ettiğiniz kurslar.</div>", unsafe_allow_html=True)
                if st.button("Derslerime Bak", key="goto_kurslar"): 
                    st.session_state["menu_choice"] = "📚 Kurslarım"
                    st.rerun()
            
            with col3:
                st.markdown("<div class='nav-card'><div class='feature-icon'>💡</div><h3>Nasıl Çalışır?</h3>Sistemi en verimli kullanma rehberi.</div>", unsafe_allow_html=True)
                if st.button("Rehberi Oku", key="goto_rehber"): 
                    st.session_state["menu_choice"] = "💡 Rehber"
                    st.rerun()

        elif choice == "🤖 AI Kurs Mimarı":
            st.markdown("<h1>🚀 AI Kurs Mimarı</h1>", unsafe_allow_html=True)
            
            with st.container():
                st.info("İpucu: Ne kadar spesifik bir konu girerseniz (örn: 'Python ile Veri Analizi'), içerikler o kadar kaliteli olur.")
                topic = st.text_input("Öğrenmek istediğiniz konu nedir?", placeholder="Örn: Modern Japon Edebiyatı")
                if st.button("✨ Kursu Tasarla ve İçerikleri Yaz"):
                    if topic:
                        with st.status("🛠️ Yapay Zeka Laboratuvarı Çalışıyor...", expanded=True) as status:
                            st.write("🔍 Müfredat tasarlanıyor...")
                            ai = AIService(provider=provider)
                            curriculum = ai.generate_course_curriculum(topic)
                            
                            new_course = Course(title=topic, description=f"{topic} hakkında AI üretimi kapsamlı kurs.")
                            db.add(new_course)
                            db.commit()
                            
                            st.write(f"📝 {len(curriculum)} ders için içerikler yazılıyor...")
                            progress_bar = st.progress(0)
                            for i, item in enumerate(curriculum):
                                content = ai.generate_lesson_content(topic, item['title'])
                                lesson = Lesson(course_id=new_course.id, title=item['title'], content=content, order=item['order'])
                                db.add(lesson)
                                progress_bar.progress((i + 1) / len(curriculum))
                            
                            db.commit()
                            status.update(label="✅ Akademi Hazır!", state="complete")
                        st.success(f"🎉 '{topic}' kursu kütüphanenize eklendi.")
                    else:
                        st.warning("Lütfen bir konu başlığı girin.")

        elif choice == "📚 Kurslarım":
            st.markdown("<h1>📚 Kütüphanem</h1>", unsafe_allow_html=True)
            courses = db.query(Course).all()
            if not courses:
                st.info("Kütüphaneniz henüz boş. 'AI Kurs Mimarı' ile ilk kursunuzu oluşturun.")
            else:
                titles = [c.title for c in courses]
                selected = st.selectbox("Çalışmak istediğiniz kursu seçin:", titles)
                course = db.query(Course).filter(Course.title == selected).first()
                
                if course:
                    col_info, col_download = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"<h2>📖 {course.title}</h2>", unsafe_allow_html=True)
                        st.caption(f"Oluşturulma: {course.created_at.strftime('%d.%m.%Y')}")
                    with col_download:
                        try:
                            pdf_data = generate_pdf(course.title, course.lessons)
                            st.download_button("📑 PDF Kitapçığı İndir", data=bytes(pdf_data), file_name=f"{course.title}_AI_Akademi.pdf", mime="application/pdf")
                        except Exception as e:
                            st.info(f"PDF Hazır Değil: {str(e)}")
                    
                    st.markdown("<hr>", unsafe_allow_html=True)
                    
                    tabs = st.tabs([f"Ders {l.order}: {l.title}" for l in course.lessons])
                    for i, tab in enumerate(tabs):
                        with tab:
                            st.markdown(f"<div class='glass-card' style='line-height: 1.8;'>{course.lessons[i].content}</div>", unsafe_allow_html=True)

        elif choice == "💡 Rehber":
            st.markdown("<h1>💡 Nasıl Kullanılır?</h1>", unsafe_allow_html=True)
            st.markdown("""
            <div class='glass-card'>
                <h3>1. Adım: Konu Belirleme</h3>
                Öğrenmek istediğiniz konuyu <b>AI Kurs Mimarı</b> bölümüne yazın. "Python" yerine "Veri Analizi için Python" gibi daha net başlıklar daha iyi sonuç verir.
                <br><br>
                <h3>2. Adım: Motor Seçimi</h3>
                Sol taraftaki panelden <b>Gemini</b> veya <b>Groq</b> motorlarını seçebilirsiniz. Gemini daha detaylı içerik, Groq ise daha hızlı yanıt sunar.
                <br><br>
                <h3>3. Adım: Kütüphaneyi Kullanma</h3>
                Oluşturulan tüm kurslar <b>Kütüphanem</b> sekmesinde saklanır. Buradan dersleri okuyabilir ve PDF formatında çıktı alarak derslerinize çevrimdışı devam edebilirsiniz.
            </div>
            """, unsafe_allow_html=True)

    # --- Footer ---
    st.markdown("""
    <div style='text-align: center; margin-top: 50px; padding: 20px; color: #8e7d77; border-top: 1px solid rgba(0,0,0,0.05);'>
        Advanced AI Learning Management System<br>
        <b>Developed with ❤️ by Zeynep Ebrar Pala</b>
    </div>
    """, unsafe_allow_html=True)
    db.close()

if __name__ == "__main__":
    main()
