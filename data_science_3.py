import streamlit as st
import google.generativeai as genai
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, BaseDocTemplate, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import sys
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab import pdfbase
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from reportlab.lib.utils import simpleSplit  # Для отладки

# --- 1. Настройка API ключа и выбор модели ---
YOUR_API_KEY = "AIzaSyDhTRGV7c7ePDNA2G1PtvjNf-Xvmy-zy-Q"  # ***** ВСТАВЬТЕ СВОЙ КЛЮЧ ЗДЕСЬ *****
try:
    genai.configure(api_key=YOUR_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
except Exception as e:
    st.error(f"Ошибка при настройке API: {e}. Пожалуйста, проверьте ваш API ключ и подключение к интернету.")
    st.stop()

# --- 2. Классы для хранения данных пользователя ---
class UserData:
    def __init__(self, name="", phone="", address="", has_experience=False, experience_count=0, experiences=[], about_me="", achievements=""):
        self.name = name
        self.phone = phone
        self.address = address
        self.has_experience = has_experience
        self.experience_count = experience_count
        self.experiences = experiences
        self.about_me = about_me
        self.achievements = achievements

class Experience:
    def __init__(self, year="", company="", position="", description=""):
        self.year = year
        self.company = company
        self.position = position
        self.description = description

# --- 3. Функция для сбора данных пользователя через Streamlit ---
def collect_user_data():
    user_data = UserData()

    st.title("📝 Создание резюме")

    user_data.name = st.text_input("👤 ФИО:")
    user_data.phone = st.text_input("📞 Номер телефона:")
    user_data.address = st.text_input("🏠 Адрес:")

    user_data.has_experience = st.radio("💼Есть ли у вас опыт работы по желаемой должности?", ("Да", "Нет"))

    if user_data.has_experience == "Да":
        user_data.about_me = st.text_area("🙋‍♀️Расскажите о себе (навыки, цели, сильные стороны):", height=100)
        user_data.experience_count = st.number_input("Сколько мест работы вы хотите указать?", min_value=1, value=1)

        for i in range(user_data.experience_count):
            st.subheader(f"📌 Опыт работы #{i + 1}")
            year = st.text_input("📅 Год:", key=f"year_{i}")
            company = st.text_input("🏢 Компания:", key=f"company_{i}")
            position = st.text_input("🧑‍💼 Должность:", key=f"position_{i}")
            description = st.text_area("📝 Описание работы:", key=f"description_{i}")

    else:
        user_data.about_me = st.text_area("🙋‍♀️ Расскажите о себе (навыки, цели, сильные стороны):", height=100)
        user_data.achievements = st.text_area("🏆 Перечислите ваши достижения:", height=100)

    return user_data

# --- 4. Функция для генерации резюме с использованием Gemini ---
def generate_resume(user_data):
    """Генерирует резюме на основе данных пользователя."""

    prompt = f"""
    Сгенерируй резюме на основе следующей информации:

    ФИО: {user_data.name}
    Номер телефона: {user_data.phone}
    Адрес: {user_data.address}

    """

    if user_data.has_experience == "Да":
        prompt += "Опыт работы:\n"
        prompt += f"Количество мест работы: {user_data.experience_count}\n\n"
        for i, exp in enumerate(user_data.experiences):
            prompt += f"Опыт работы #{i + 1}:\n"
            prompt += f"Год: {exp.year}\n"
            prompt += f"Компания: {exp.company}\n"
            prompt += f"Должность: {exp.position}\n"
            prompt += f"Описание: {exp.description}\n\n"
    else:
        prompt += f"О себе: {user_data.about_me}\n"
        prompt += f"Достижения: {user_data.achievements}\n"

    prompt += """

    Сгенерируй хорошо структурированное резюме, используя профессиональный стиль.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Ошибка при генерации резюме: {e}. Пожалуйста, проверьте свой запрос и API ключ.")
        return ""

# --- 5. Функция для работы со шрифтами ---
def setup_fonts():
    """Настраивает шрифты для reportlab, обрабатывая возможные ошибки."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, 'DejaVuSans.ttf')  # Ищем шрифт в той же директории

    if not os.path.exists(font_path):
        st.warning(f"Файл шрифта не найден по пути: {font_path}. Используется стандартный шрифт.")
        return 'Helvetica'

    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        return 'DejaVuSans'  # Возвращаем имя шрифта для использования в стилях
    except Exception as e:
        print(f"Error registering font: {e}, using fallback.", file=sys.stderr)
        pdfmetrics.registerFont(pdfmetrics.standardFonts['Helvetica'])  # Fallback
        return 'Helvetica'  # Возвращаем имя запасного шрифта

# --- 6. Функция для создания PDF из текста резюме ---
def create_pdf_resume(resume_text, filename="resume.pdf"):
    """Создает PDF файл из текста резюме с улучшенным форматированием."""

    buffer = io.BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # --- 1. Настройка шрифтов ---
    default_font = setup_fonts()  # Получаем имя шрифта (или запасного)

    # --- 2. Создание стилей с указанием шрифта ---
    try:
        title_style = ParagraphStyle(
            name='TitleStyle',
            parent=styles['h1'],
            alignment=TA_CENTER,
            fontName=default_font,  # Используем default_font
            fontSize=16,
            spaceAfter=12,  # Добавляем отступ после заголовка
        )
        normal_style = ParagraphStyle(
            name='NormalStyle',
            parent=styles['Normal'],
            leading=14,
            spaceAfter=6,
            fontName=default_font,  # Используем default_font
            fontSize=12,
        )
        experience_title_style = ParagraphStyle(
            name='ExperienceTitleStyle',
            parent=styles['h2'],
            fontName=default_font,
            fontSize=14,
            spaceBefore=10,  # Отступ перед разделом опыта
            spaceAfter=6,
        )
        experience_detail_style = ParagraphStyle(
            name='ExperienceDetailStyle',
            parent=styles['Normal'],
            fontName=default_font,
            fontSize=12,
            leading=14,
            spaceAfter=4,
        )
    except Exception as e:
        print(f"Error creating styles: {e}, using standard styles.", file=sys.stderr)
        # Fallback to standard styles
        title_style = styles['h1']
        title_style.alignment = TA_CENTER
        normal_style = styles['Normal']
        experience_title_style = styles['h2']
        experience_detail_style = styles['Normal']

    def build_flowables(text):
        """Разбивает текст на элементы reportlab."""
        flowables = []
        lines = text.split('\n')
        current_title = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("## ") or line.startswith("### "):
                if current_title:
                    flowables.append(Paragraph(current_title.lstrip('# ').strip(), title_style))
                    flowables.append(Paragraph("<br/>".join(current_content), normal_style))

                current_title = line
                current_content = []
            elif current_title and "Опыт работы" in current_title:
                # Обработка деталей опыта работы
                if line.startswith("- "):
                    flowables.append(Paragraph(line.lstrip('- ').strip(), experience_detail_style))
                elif ":" in line:
                    flowables.append(Paragraph(line, experience_title_style))
                else:
                    current_content.append(line)
            else:
                current_content.append(line)

        if current_title:
            flowables.append(Paragraph(current_title.lstrip('# ').strip(), title_style))
            flowables.append(Paragraph("<br/>".join(current_content), normal_style))

        return flowables

    story = build_flowables(resume_text)

    main_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='main')
    doc.addPageTemplates([PageTemplate(id='one', frames=main_frame)])
    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()

# --- 7. Streamlit приложение ---
def page_generate_resume():  # Переименовано в page_generate_resume
    st.title("Генератор резюме")

    if 'user_data' not in st.session_state:
        st.session_state.user_data = collect_user_data()
    else:
        st.session_state.user_data = collect_user_data()

    if st.button("✨ Сгенерировать резюме"):
        if st.session_state.user_data.name and st.session_state.user_data.phone and st.session_state.user_data.address:
            st.session_state.generated_resume = generate_resume(st.session_state.user_data)
        else:
            st.warning("Пожалуйста, заполните основные данные (ФИО, телефон, адрес).")

    if 'generated_resume' in st.session_state:
        st.text_area("📄Предварительный просмотр резюме (вы можете отредактировать, так же уберите '*, #'. Они все сохраняются в PDF, когда вы скачаете его)", st.session_state.generated_resume, height=400)

        if st.button("📥 Скачать резюме в PDF"):
            if not st.session_state.generated_resume:
                st.error("Ошибка: Невозможно создать PDF, резюме не сгенерировано.")
                return

            pdf_bytes = create_pdf_resume(st.session_state.generated_resume, f"resume_{st.session_state.user_data.name.replace(' ', '_')}.pdf")
            st.download_button(
                label="Скачать резюме в PDF",
                data=pdf_bytes,
                file_name=f"resume_{st.session_state.user_data.name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    page_generate_resume()  # Вызываем функцию напрямую, если запускаем этот файл
