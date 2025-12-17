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
st.markdown(
    """
    <style>
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(20px);}
        to {opacity: 1; transform: translateY(0);}
    }

    .welcome {
        animation: fadeIn 1.2s ease-in-out;
        text-align: center;
        padding: 90px 0;
    }

    .card {
        background-color: #f8f9fa;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.06);
        animation: fadeIn 1.5s ease-in-out;
    }

    .start-btn button {
        background-color: #1f77b4 !important;
        color: white !important;
        font-size: 20px !important;
        padding: 14px 40px !important;
        border-radius: 16px !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)
if not st.session_state.entered:

    st.markdown(
        """
        <div class="welcome">
            <h1 style="font-size:52px;">👋 Добро пожаловать</h1>
            <p style="font-size:22px; margin-top:20px;">
                Умная платформа для студентов и выпускников  
                по поиску работы с использованием <b>Data Science & ML</b>
            </p>
            <p style="color:gray; font-size:17px;">
                Начни карьеру уверенно и осознанно
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="card">
                <h3>🔎 Поиск вакансий</h3>
                <p>Подбор вакансий под твою специальность и город</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>🌟 Оценка компаний</h3>
                <p>Анализ репутации и надежности работодателей</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card">
                <h3>📝 Генератор резюме</h3>
                <p>Создание профессионального резюме с ИИ</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="start-btn">', unsafe_allow_html=True)
        if st.button("🚀 Начать", use_container_width=True):
            st.session_state.entered = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()
st.sidebar.title("📌 Навигация")
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
