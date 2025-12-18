import streamlit as st
import google.generativeai as genai
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Frame, BaseDocTemplate, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import sys
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os # ← покажет v1 или v1beta
# --- Показываем версию Gemini SDK ---
try:
    st.write("🧩 Gemini SDK version:", genai.__version__)
except:
    st.write("Ошибка: не удалось определить версию библиотеки")


# --- 1. Настройка API ключа и модели ---
YOUR_API_KEY = "AIzaSyDNl02SVlPinCg4nP0LSYs1YiSYbfG6Nac"

try:
    genai.configure(api_key=YOUR_API_KEY)
except Exception as e:
    st.error(f"Ошибка при настройке API: {e}")
    st.stop()

# ✔ единственно правильная модель
model = genai.GenerativeModel("gemini-1.5-pro")


# --- 2. Классы данных ---
class UserData:
    def __init__(self, name="", phone="", address="", has_experience=False,
                 experience_count=0, experiences=None, about_me="", achievements=""):
        self.name = name
        self.phone = phone
        self.address = address
        self.has_experience = has_experience
        self.experience_count = experience_count
        self.experiences = experiences or []
        self.about_me = about_me
        self.achievements = achievements


class Experience:
    def __init__(self, year="", company="", position="", description=""):
        self.year = year
        self.company = company
        self.position = position
        self.description = description


# --- 3. Сбор данных пользователя ---
def collect_user_data():
    user_data = UserData()

    st.title("📝 Создание резюме")

    user_data.name = st.text_input("👤 ФИО:")
    user_data.phone = st.text_input("📞 Номер телефона:")
    user_data.address = st.text_input("🏠 Адрес:")

    user_data.has_experience = st.radio("💼Есть ли у вас опыт работы по желаемой должности?", ("Да", "Нет"))

    if user_data.has_experience == "Да":
        user_data.about_me = st.text_area("🙋‍♀️ Расскажите о себе:", height=100)
        user_data.experience_count = st.number_input("Сколько мест работы вы хотите указать?", min_value=1, value=1)

        user_data.experiences = []  # ← очищаем

        for i in range(user_data.experience_count):
            st.subheader(f"📌 Опыт работы #{i + 1}")

            year = st.text_input("📅 Год:", key=f"year_{i}")
            company = st.text_input("🏢 Компания:", key=f"company_{i}")
            position = st.text_input("🧑‍💼 Должность:", key=f"position_{i}")
            description = st.text_area("📝 Описание работы:", key=f"description_{i}")

            # ✔ реально добавляем опыт в список
            user_data.experiences.append(
                Experience(year, company, position, description)
            )

    else:
        user_data.about_me = st.text_area("🙋‍♀️ Расскажите о себе:", height=100)
        user_data.achievements = st.text_area("🏆 Достижения:", height=100)

    return user_data


# --- 4. Генерация резюме Gemini ---
def generate_resume(user_data):

    prompt = f"""
Сгенерируй профессиональное резюме:

ФИО: {user_data.name}
Телефон: {user_data.phone}
Адрес: {user_data.address}
"""

    if user_data.has_experience == "Да":
        prompt += f"\nОпыт работы ({user_data.experience_count} мест):\n"
        for i, exp in enumerate(user_data.experiences):
            prompt += f"""
Опыт #{i+1}:
Год: {exp.year}
Компания: {exp.company}
Должность: {exp.position}
Описание: {exp.description}
"""

    else:
        prompt += f"\nО себе: {user_data.about_me}\n"
        prompt += f"Достижения: {user_data.achievements}\n"

    prompt += "\nОформи текст структурировано и профессионально."

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Ошибка при генерации резюме: {e}")
        return ""


# --- 5. PDF генерация ---
def setup_fonts():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, 'DejaVuSans.ttf')

    if not os.path.exists(font_path):
        return 'Helvetica'

    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        return 'DejaVuSans'
    except:
        return 'Helvetica'


def create_pdf_resume(text):
    buffer = io.BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    font = setup_fonts()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName=font,
        alignment=TA_CENTER,
        fontSize=16
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName=font,
        fontSize=12,
        leading=14
    )

    story = [Paragraph("Резюме", title_style)]

    for line in text.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), normal_style))

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)
    doc.addPageTemplates([PageTemplate(id='page', frames=frame)])
    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()


# --- 6. Основная страница Streamlit ---
def page_generate_resume():
    st.title("Генератор резюме")

    if "user_data" not in st.session_state:
        st.session_state.user_data = collect_user_data()
    else:
        st.session_state.user_data = collect_user_data()

    if st.button("✨ Сгенерировать резюме"):
        if st.session_state.user_data.name and st.session_state.user_data.phone and st.session_state.user_data.address:
            st.session_state.generated_resume = generate_resume(st.session_state.user_data)
        else:
            st.warning("Заполните ФИО, телефон и адрес!")

    if "generated_resume" in st.session_state:
        st.text_area("📄 Предварительный просмотр:", st.session_state.generated_resume, height=400)

        if st.button("📥 Скачать PDF"):
            pdf_bytes = create_pdf_resume(st.session_state.generated_resume)
            st.download_button(
                "Скачать PDF",
                data=pdf_bytes,
                file_name=f"resume_{st.session_state.user_data.name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )


# --- 7. Запуск ---
if __name__ == "__main__":
    page_generate_resume()
