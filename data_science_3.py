import streamlit as st
import google.generativeai as genai
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Frame, BaseDocTemplate, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

API_KEY = "AIzaSyAQOlttcsIrSV99chFUb2g8RIV6zMxXAi4"

genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)


class Experience:
    def __init__(self, year="", company="", position="", description=""):
        self.year = year
        self.company = company
        self.position = position
        self.description = description


class UserData:
    def __init__(self):
        self.name = ""
        self.phone = ""
        self.address = ""
        self.about_me = ""
        self.has_experience = False
        self.experience_count = 0
        self.experiences = []
        self.achievements = ""


def clean_markdown_links(text):
    # Убираем [текст](ссылка)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    text = text.replace("mailto:", "")
    text = text.replace("tel:", "")


    text = re.sub(r"[*#`_]+", "", text)

    return text



def collect_user_data():
    user = UserData()

    st.title("📝 Генератор резюме")

    user.name = st.text_input("👤 ФИО:")
    user.phone = st.text_input("📞 Телефон:")
    user.address = st.text_input("🏠 Адрес:")

    user.has_experience = st.radio("Есть опыт работы?", ("Да", "Нет"))

    if user.has_experience == "Да":
        user.about_me = st.text_area("Расскажите о себе:", height=100)
        user.experience_count = st.number_input("Сколько мест работы?", min_value=1, value=1)

        user.experiences = []
        for i in range(user.experience_count):
            st.subheader(f"📌 Опыт #{i+1}")

            year = st.text_input("Год:", key=f"year_{i}")
            company = st.text_input("Компания:", key=f"company_{i}")
            position = st.text_input("Должность:", key=f"position_{i}")
            description = st.text_area("Описание:", key=f"desc_{i}")

            user.experiences.append(Experience(year, company, position, description))

    else:
        user.about_me = st.text_area("Расскажите о себе:", height=100)
        user.achievements = st.text_area("Достижения:", height=100)

    return user

def generate_resume(user):
    prompt = f"""
Создай профессиональное резюме:

ФИО: {user.name}
Телефон: {user.phone}
Адрес: {user.address}

О себе:
{user.about_me}
"""

    if user.has_experience == "Да":
        prompt += f"\nОпыт работы ({user.experience_count} мест):\n"
        for i, exp in enumerate(user.experiences):
            prompt += f"""
Опыт #{i+1}:
Год: {exp.year}
Компания: {exp.company}
Должность: {exp.position}
Описание: {exp.description}
"""
    else:
        prompt += f"\nДостижения:\n{user.achievements}\n"

    prompt += "\nОформи текст структурировано, без markdown, без ссылок."

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return ""

def setup_fonts():
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("DejaVu", font_path))
        return "DejaVu"
    return "Helvetica"


def create_pdf(text):
    buffer = io.BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    font = setup_fonts()

    style = ParagraphStyle("Normal", parent=styles["Normal"], fontName=font, fontSize=12, leading=14)

    story = [Paragraph("Резюме", ParagraphStyle("Title", alignment=TA_CENTER, fontSize=18, fontName=font))]

    for line in text.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), style))

    doc.addPageTemplates([PageTemplate(id="main",
                        frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)])])

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def page_generate_resume():
    user = collect_user_data()

    if st.button("✨ Сгенерировать резюме"):
        if not user.name or not user.phone or not user.address:
            st.warning("Заполните ФИО, телефон и адрес!")
        else:
            raw = generate_resume(user)
            st.session_state.resume = clean_markdown_links(raw)

    if "resume" in st.session_state:
        st.text_area("Предпросмотр:", st.session_state.resume, height=400)

        if st.button("📥 Скачать PDF"):
            pdf = create_pdf(st.session_state.resume)
            st.download_button("Скачать PDF", pdf,
                               file_name="resume.pdf", mime="application/pdf")


if __name__ == "__main__":
    page_generate_resume()
