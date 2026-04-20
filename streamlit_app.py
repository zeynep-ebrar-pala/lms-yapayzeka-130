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

    pdf.cell(0, 10, f"Kurs: {course_title}", ln=True, align='L')
    pdf.ln(5)
    
    pdf.set_font(font_name, size=12)
    for lesson in lessons:
        pdf.set_font(font_name, size=14)
        pdf.cell(0, 10, f"Ders {lesson.order}: {lesson.title}", ln=True)
        pdf.set_font(font_name, size=11)
        content = lesson.content.replace('#', '').replace('*', '').replace('`', '')
        pdf.multi_cell(0, 10, content)
        pdf.ln(10)
    return pdf.output()

# --- Streamlit UI App ---
def main():
    st.set_page_config(page_title="AI LMS - Zeynep Ebrar Pala", layout="wide")
    init_db()
    db = SessionLocal()

    # --- Custom Styling ---
    st.markdown("""
    <style>
        .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4CAF50; color: white; border: none; }
        .stButton>button:hover { background-color: #45a049; border: 2px solid white; }
        h1, h2, h3 { color: #00d2ff; }
        .sidebar .sidebar-content { background-color: #1a1c24; }
    </style>
    """, unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if st.session_state["user"] is None:
        st.title("👤 AI LMS Giriş & Kayıt")
        tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
        with tab1:
            l_user = st.text_input("Kullanıcı Adı", key="l_user")
            l_pass = st.text_input("Şifre", type="password", key="l_pass")
            if st.button("Giriş Yap"):
                user = db.query(User).filter(User.username == l_user).first()
                if user and verify_password(l_pass, user.hashed_password):
                    st.session_state["user"] = {"id": user.id, "username": user.username}
                    st.success("Başarıyla giriş yapıldı!")
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı.")
        with tab2:
            r_user = st.text_input("Kullanıcı Adı", key="r_user")
            r_email = st.text_input("E-posta", key="r_email")
            r_pass = st.text_input("Şifre", type="password", key="r_pass")
            if st.button("Kayıt Ol"):
                existing = db.query(User).filter(User.username == r_user).first()
                if existing:
                    st.error("Bu kullanıcı adı zaten alınmış.")
                else:
                    new_user = User(username=r_user, email=r_email, hashed_password=get_password_hash(r_pass))
                    db.add(new_user)
                    db.commit()
                    st.success("Kayıt başarılı! Giriş yapabilirsiniz.")

    else:
        user = st.session_state["user"]
        with st.sidebar:
            st.title(f"🎓 Merhaba, {user['username']}")
            choice = st.selectbox("Menü", ["🏠 Ana Sayfa", "🤖 AI Kurs Mimarı", "📚 Kurslarım"])
            st.divider()
            provider = st.radio("LLM Sağlayıcısı", ["gemini", "groq"])
            if st.button("Çıkış Yap"):
                st.session_state["user"] = None
                st.rerun()

        if choice == "🏠 Ana Sayfa":
            st.title("Yeni Nesil Yapay Zeka LMS")
            st.markdown(f"Hoş geldin **{user['username']}**! Zeynep Ebrar Pala tarafından geliştirilen yeni nesil eğitim platformundasın.")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Sağlayıcılar", "Gemini, Groq")
            with col2: st.metric("Veritabanı", "SQLite")
            with col3: st.metric("Geliştiren", "ZEYNEP EBRAR PALA")

        elif choice == "🤖 AI Kurs Mimarı":
            st.title("AI ile Kurs Oluştur")
            topic = st.text_input("Öğrenmek istediğiniz konu:", placeholder="Örn: Modern Sanat Tarihi")
            if st.button("🚀 Kursu Oluştur"):
                if topic:
                    with st.spinner("AI müfredat ve dersleri hazırlıyor..."):
                        ai = AIService(provider=provider)
                        curriculum = ai.generate_course_curriculum(topic)
                        new_course = Course(title=topic, description=f"{topic} hakkında AI üretimi kapsamlı kurs.")
                        db.add(new_course)
                        db.commit()
                        for item in curriculum:
                            content = ai.generate_lesson_content(topic, item['title'])
                            lesson = Lesson(course_id=new_course.id, title=item['title'], content=content, order=item['order'])
                            db.add(lesson)
                        db.commit()
                        st.success("🎉 Kurs oluşturuldu! Kurslarım sekmesine gidin.")
                else:
                    st.warning("Lütfen bir konu başlığı girin.")

        elif choice == "📚 Kurslarım":
            st.title("Kurslarım")
            courses = db.query(Course).all()
            if not courses:
                st.info("Henüz kursunuz yok.")
            else:
                titles = [c.title for c in courses]
                selected = st.selectbox("Bir kurs seçin:", titles)
                course = db.query(Course).filter(Course.title == selected).first()
                if course:
                    col_h, col_d = st.columns([3, 1])
                    with col_h: st.header(f"📖 {course.title}")
                    with col_d:
                        try:
                            pdf_data = generate_pdf(course.title, course.lessons)
                            st.download_button("📑 Raporu İndir (PDF)", data=bytes(pdf_data), file_name=f"{course.title}_Rapor.pdf", mime="application/pdf")
                        except Exception as e:
                            st.info(f"PDF Hazır: {e}")
                    st.divider()
                    tabs = st.tabs([f"Ders {l.order}: {l.title}" for l in course.lessons])
                    for i, tab in enumerate(tabs):
                        with tab: st.write(course.lessons[i].content)

    db.close()

if __name__ == "__main__":
    main()
