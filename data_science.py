import streamlit as st
import data_science_1
import data_science_2
import data_science_3
import data_science_4
import data5 


st.set_page_config(
    page_title="Платформа для поиска работы",
    page_icon="💼",
    layout="wide"
)

# ===== Инициализация состояния =====
if "entered" not in st.session_state:
    st.session_state.entered = False
if not st.session_state.entered:
    st.markdown(
        """
        <div style="text-align:center; padding: 80px 0;">
            <h1 style="font-size:48px;">👋 Добро пожаловать!</h1>
            <p style="font-size:20px; margin-top:20px;">
                Платформа для поиска вакансий для студентов и выпускников
                с использованием Data Science и Machine Learning
            </p>
            <p style="color:gray; font-size:16px;">
                Найди работу. Проанализируй компанию. Создай резюме.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Начать", use_container_width=True):
            st.session_state.entered = True
            st.rerun()

    st.stop()
# ===== СТИЛИ КНОПОК =====
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #1f77b4 !important;
        color: white !important;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 12px;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===== SIDEBAR =====
st.sidebar.title("📌 Навигация")
page = st.sidebar.radio(
    "📄 Выберите страницу:",
    [
        "🔎 Поиск вакансий",
        "📝 Генератор резюме"
        "🌟 Оценка компании",
        "🌍 CityFit AI",
        "🎯 Skill Match/Fit"
    ]
)

# ===== НАВИГАЦИЯ =====
if page == "🔎 Поиск вакансий":
    data_science_1.page_find_vacancies()
elif page == "📝 Генератор резюме":
    data_science_3.page_generate_resume()
elif page == "🌟 Оценка компании":
    data_science_2.page_rate_company()
elif page == "🌍 CityFit AI":
    st.markdown(
        """
        <div style="padding-bottom:20px;">
            <h2>🌍 CityFit AI</h2>
            <p style="color:gray; font-size:16px;">
                Интеллектуальный ML-модуль, который показывает,
                <b>в каком городе твой шанс трудоустройства выше</b>,
                на основе анализа рынка вакансий
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # вызов ML-функции
    data_science_4.cityfit_ai(
        st.session_state.get("user_profile", {}).get("city")
    )

elif page == "🎯 Skill Match/Fit":
    data5.page_skill_match()
