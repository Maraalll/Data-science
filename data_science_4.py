import streamlit as st
import pandas as pd
import os
import numpy as np


# ======================================================
# Загрузка данных
# ======================================================
@st.cache_data
def load_vacancies():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "hh_kazakhstan_final_dataset.csv.gz"
    )
    return pd.read_csv(file_path)


# ======================================================
# ОСНОВНАЯ ЛОГИКА CityFit AI
# ======================================================
def cityfit_ai(profession):
    df = load_vacancies()

    # --- фильтр по профессии ---
    df = df[
        df["name"]
        .str.contains(profession, case=False, na=False)
    ]

    if df.empty:
        st.warning("⚠️ По этой профессии вакансий не найдено")
        return

    # --- статистика по городам ---
    city_stats = (
        df["city"]
        .value_counts()
        .reset_index()
    )
    city_stats.columns = ["city", "vacancies"]

    # --- CityFit Score (лог-нормализация) ---
    city_stats["score"] = (
        np.log1p(city_stats["vacancies"])
        / np.log1p(city_stats["vacancies"].max())
        * 100
    ).round().astype(int)

    city_stats = city_stats.sort_values("score", ascending=False)

    # ======================================================
    # ВИЗУАЛЬНЫЕ КАРТОЧКИ
    # ======================================================
    st.markdown("### 🌍 Города с вакансиями по выбранной профессии")
    st.info(f"🔎 Профессия: **{profession}**")

    for _, row in city_stats.head(7).iterrows():
        city = row["city"]
        vacancies = row["vacancies"]
        score = row["score"]

        st.markdown(
            f"""
            <div style="
                background:linear-gradient(135deg,#f8fbff,#eef4ff);
                padding:18px;
                border-radius:16px;
                margin-bottom:14px;
                box-shadow:0 6px 16px rgba(0,0,0,0.04);
            ">
                <div style="display:flex; justify-content:space-between;">
                    <div style="font-size:18px;">
                        ⭐ <b>{city}</b> — {vacancies} вакансий
                    </div>
                    <div style="font-weight:700; color:#1f77b4;">
                        {score}%
                    </div>
                </div>

                <div style="
                    background:#e6ecf5;
                    border-radius:10px;
                    height:10px;
                    margin-top:10px;
                ">
                    <div style="
                        width:{score}%;
                        background:linear-gradient(90deg,#4facfe,#00f2fe);
                        height:10px;
                        border-radius:10px;
                    "></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ======================================================
    # 📊 ГРАФИК
    # ======================================================
    st.markdown("### 📊 CityFit Score по городам")
    st.bar_chart(city_stats.set_index("city")[["score"]])

    # ======================================================
    # 🔍 Explainable AI
    # ======================================================
    with st.expander("🔍 Почему именно эти города? (Explainable AI)"):
        st.markdown(
            """
            **CityFit AI** анализирует рынок вакансий по выбранной профессии:

            • 📌 учитывает количество вакансий  
            • ⚖️ сравнивает города между собой  
            • 🧠 показывает, где выше шанс трудоустройства  

            **CityFit Score** — относительный показатель (0–100),
            а не абсолютный процент.
            """
        )


# ======================================================
# СТРАНИЦА CityFit AI
# ======================================================
def page_cityfit_ai():
    st.markdown("## 🌍 CityFit AI")
    st.markdown(
        "<p style='color:gray;'>"
        "Интеллектуальный ML-модуль, который показывает, "
        "<b>в каких городах выше шанс трудоустройства</b> "
        "на основе анализа рынка вакансий"
        "</p>",
        unsafe_allow_html=True
    )

    st.markdown("### 🧠 Учитывать профессию")

    profession = st.text_input(
        "Введите профессию или ключевое слово",
        placeholder="Например: Data Analyst, Python, Marketing"
    )

    if not profession:
        st.info("✍️ Введите профессию, чтобы увидеть подходящие города")
        return

    cityfit_ai(profession)
