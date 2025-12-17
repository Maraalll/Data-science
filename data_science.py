import streamlit as st
import data_science_1
import data_science_2
import data_science_3

st.set_page_config(
    page_title="Платформа для поиска работы",
    page_icon="💼",
    layout="wide"
)

if "entered" not in st.session_state:
    st.session_state.entered = False

if "onboarding_done" not in st.session_state:
    st.session_state.onboarding_done = False

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4f8fb 0%, #ffffff 60%);
    }

    section[data-testid="stSidebar"] {
        background-color: #f0f4f8;
    }
    </style>
    """,
    unsafe_allow_html=True
)
if st.session_state.entered and not st.session_state.onboarding_done:

    st.markdown(
        """
        <div style="text-align:center; padding: 50px 0;">
            <h2>🎯 Давайте начнём</h2>
            <p style="font-size:18px; color:gray;">
                Ответьте на несколько вопросов — мы подстроим платформу под вас
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        role = st.selectbox(
            "🎓 Кто вы?",
            ["Студент", "Выпускник", "Молодой специалист"]
        )

    with col2:
        goal = st.selectbox(
            "🎯 Ваша цель",
            ["Стажировка", "Первая работа", "Фриланс"]
        )

    with col3:
        city = st.selectbox(
            "🏙 Город",
            ["Астана", "Алматы", "Шымкент", "Караганда"]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Перейти к платформе", use_container_width=True):
            st.session_state.user_profile = {
                "role": role,
                "goal": goal,
                "city": city
            }
            st.session_state.onboarding_done = True
            st.rerun()

    st.stop()
st.sidebar.title("📌 Навигация")

st.sidebar.markdown(
    f"""
    👤 **Профиль:**  
    {st.session_state.user_profile.get('role')}  
    🎯 {st.session_state.user_profile.get('goal')}  
    🏙 {st.session_state.user_profile.get('city')}
    """
)

page = st.sidebar.radio(
    "📄 Выберите страницу:",
    [
        "🔎 Поиск вакансий",
        "🌟 Оценка компании",
        "📝 Генератор резюме"
    ]
)

if page == "🔎 Поиск вакансий":
    data_science_1.page_find_vacancies()
elif page == "🌟 Оценка компании":
    data_science_2.page_rate_company()
elif page == "📝 Генератор резюме":
    data_science_3.page_generate_resume()
