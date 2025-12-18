import streamlit as st
import streamlit.components.v1 as components

import data_science_1
import data_science_2
import data_science_3
import data_science_4
import data5


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
/* ===== ГЛОБАЛЬНЫЙ ФОН ===== */
.stApp {
    background:
        radial-gradient(circle at top left, rgba(120,190,255,0.35), transparent 55%),
        radial-gradient(circle at bottom right, rgba(0,180,255,0.35), transparent 60%),
        linear-gradient(180deg, #f6faff 0%, #eef4ff 100%);
}

/* убираем лишний отступ сверху */
.main {
    padding-top: 0rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===== КНОПКА JobBuddy ===== */
.jobbuddy-btn {
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    color: white;
    font-size: 20px;
    font-weight: 600;
    padding: 16px 52px;
    border-radius: 30px;
    border: none;
    cursor: pointer;
    transition: all 0.35s ease;
    box-shadow: 0 12px 30px rgba(0, 120, 255, 0.35);
}

/* HOVER */
.jobbuddy-btn:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow:
        0 18px 45px rgba(0, 160, 255, 0.55),
        0 0 25px rgba(0, 200, 255, 0.65);
}
</style>
""", unsafe_allow_html=True)

# =========================
# HOME PAGE
# =========================
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
    <div style="
        margin-top:-120px;
        display:flex;
        justify-content:center;
    ">
    """, unsafe_allow_html=True)
    </div>
   
    if st.session_state.get("start"):
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
