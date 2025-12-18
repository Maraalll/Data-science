import streamlit as st
import data_science_1
import data_science_2
import data_science_3
import data_science_4
import data5

st.set_page_config(
    page_title="Платформа для поиска работы",
    page_icon="🎯",
    layout="wide"
)

# ===== ИНИЦИАЛИЗАЦИЯ =====
if "show_home" not in st.session_state:
    st.session_state.show_home = True

# ===== СТИЛИ =====
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top right, #cfe8ff 0%, #f8fbff 35%, #eaf1ff 100%);
}

.main {
    padding-top: 0rem;
}

.hero {
    text-align: center;
    padding: 90px 20px 70px 20px;
}

.hero-title {
    font-size: 48px;
    font-weight: 800;
    color: #1f2a44;
}

.hero-subtitle {
    font-size: 18px;
    color: #4a5b7c;
    margin-top: 12px;
}

.card {
    background: white;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.06);
}

.stButton > button {
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    color: white;
    border-radius: 18px;
    padding: 14px 42px;
    font-size: 18px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ===== ГЛАВНАЯ СТРАНИЦА =====
if st.session_state.show_home:

    st.markdown("""
    <div class="hero">

        <div style="font-size:60px; margin-bottom:10px;">🎯</div>

        <div class="hero-title">
            JobBuddy
        </div>

        <div class="hero-subtitle">
            Умный поиск работы для студентов<br>
            <span style="font-size:16px;">
            Анализ вакансий, городов и навыков с использованием
            <b>Data Science & Machine Learning</b>
            </span>
        </div>

    </div>
    """, unsafe_allow_html=True)


    st.markdown("""
    <div style="display:flex; gap:24px; justify-content:center; max-width:1000px; margin:auto;">
        <div class="card" style="flex:1;">
            <h4>🎯 Точные вакансии</h4>
            <p>Подбор вакансий под навыки и профессию</p>
        </div>

        <div class="card" style="flex:1;">
            <h4>🌍 CityFit AI</h4>
            <p>Где проще найти работу</p>
        </div>

        <div class="card" style="flex:1;">
            <h4>🤖 ML-анализ</h4>
            <p>Решения на основе данных</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center; margin-top:40px;'>", unsafe_allow_html=True)
    if st.button("🚀 Начать с JobBuddy"):
        st.session_state.show_home = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ===== SIDEBAR =====
st.sidebar.title("📌 Навигация")
page = st.sidebar.radio(
    "Выберите страницу:",
    [
        "🔎 Поиск вакансий",
        "📝 Генератор резюме",
        "🌟 Оценка компании",
        "🌍 CityFit AI",
        "🎯 Skill Match/Fit"
    ]
)

# ===== СТРАНИЦЫ =====
if page == "🔎 Поиск вакансий":
    data_science_1.page_find_vacancies()
elif page == "📝 Генератор резюме":
    data_science_3.page_generate_resume()
elif page == "🌟 Оценка компании":
    data_science_2.page_rate_company()
elif page == "🌍 CityFit AI":
    data_science_4.page_cityfit_ai()
elif page == "🎯 Skill Match/Fit":
    data5.page_skill_match()
