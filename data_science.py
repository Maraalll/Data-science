import streamlit as st
import streamlit.components.v1 as components

# =========================
# CONFIG (ДОЛЖЕН БЫТЬ ПЕРВЫМ)
# =========================
st.set_page_config(
    page_title="JobBuddy",
    page_icon="🎯",
    layout="wide"
)

# =========================
# STATE
# =========================
if "show_home" not in st.session_state:
    st.session_state.show_home = True


# =========================
# GLOBAL CSS (фон и кнопки)
# =========================
st.markdown("""
<style>
/* фон для всего приложения */
.stApp {
    background: radial-gradient(circle at top right, #cfe8ff 0%, #f8fbff 35%, #eaf1ff 100%);
}

/* чуть меньше верхний отступ */
.main {
    padding-top: 0rem;
}

/* кнопки streamlit */
.stButton > button {
    background: linear-gradient(90deg, #4facfe, #00f2fe) !important;
    color: white !important;
    border-radius: 18px !important;
    padding: 14px 42px !important;
    font-size: 18px !important;
    border: none !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)


# =========================
# HOME PAGE
# =========================
# =========================
# HOME PAGE
if st.session_state.show_home:

    home_html = """
    <style>
      .hero-wrapper {
        min-height: 85vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
      }

      .hero {
        text-align: center;
        max-width: 1100px;
        margin: 0 auto;
      }

      .heroIcon {
        font-size: 60px;
        margin-bottom: 12px;
      }

      .heroTitle {
        font-size: 56px;
        font-weight: 800;
        color: #1f2a44;
        margin: 0;
      }

      .heroSub {
        font-size: 18px;
        color: #4a5b7c;
        margin-top: 14px;
        line-height: 1.6;
      }

      .heroSub small {
        font-size: 16px;
      }

      .cards {
        display: flex;
        gap: 24px;
        justify-content: center;
        max-width: 1100px;
        margin-top: 48px;
        flex-wrap: wrap;
      }

      .card {
        background: white;
        border-radius: 22px;
        padding: 26px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.08);
        width: 320px;
        min-height: 120px;
        text-align: left;
      }

      .card h4 {
        margin: 0 0 8px 0;
        font-size: 20px;
        color: #1f2a44;
      }

      .card p {
        margin: 0;
        color: #4a5b7c;
        font-size: 15px;
      }
    </style>

    <div class="hero-wrapper">
      <div class="hero">
          <div class="heroIcon">🎯</div>
          <h1 class="heroTitle">JobBuddy</h1>

          <div class="heroSub">
              Умный поиск работы для студентов<br/>
              <small>
                Анализ вакансий, городов и навыков с использованием
                <b>Data Science & Machine Learning</b>
              </small>
          </div>

          <div class="cards">
              <div class="card">
                  <h4>🎯 Точные вакансии</h4>
                  <p>Подбор вакансий под навыки и профессию</p>
              </div>
              <div class="card">
                  <h4>🌍 CityFit AI</h4>
                  <p>Где проще найти работу</p>
              </div>
              <div class="card">
                  <h4>🤖 ML-анализ</h4>
                  <p>Решения на основе данных</p>
              </div>
          </div>
      </div>
    </div>
    """

    # 🔥 КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ — ВЫСОТА
    components.html(home_html, height=780)

    # ✅ КНОПКА ПО ЦЕНТРУ
    st.markdown("""
    <div style="margin-top:-160px;">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Начать с JobBuddy", use_container_width=True):
            st.session_state.show_home = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# =========================
# SIDEBAR + NAVIGATION
# =========================
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

# 🔥 ИМПОРТЫ ТОЛЬКО ЗДЕСЬ
if page == "🔎 Поиск вакансий":
    import data_science_1
    data_science_1.page_find_vacancies()

elif page == "📝 Генератор резюме":
    import data_science_3
    data_science_3.page_generate_resume()

elif page == "🌟 Оценка компании":
    import data_science_2
    data_science_2.page_rate_company()

elif page == "🌍 CityFit AI":
    import data_science_4
    data_science_4.page_cityfit_ai()

elif page == "🎯 Skill Match/Fit":
    import data5
    data5.page_skill_match()
