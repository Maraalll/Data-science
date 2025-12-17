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
# CityFit AI — анализ ТОЛЬКО по профессии
# ======================================================
def cityfit_ai_by_profession(profession: str):
    df = load_vacancies()

    # --- фильтр по профессии ---
    df = df[df["name"].str.contains(profession, case=False, na=False)]

    if df.empty:
        st.warning("⚠️ По этой профессии вакансий не найдено")
        return

    # --- статистика по городам ---
    city_stats = (
        df["city"]
        .dropna()
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
    # UI — РЕЗУЛЬТАТЫ
    # ======================================================
    st.markdown("### 🌍 Города с вакансиями по выбранной профессии")
    st.info(f"🔎 Профессия: **{profession}**")

    for _, row in city_stats.head(7).iterrows():
        city = row["city"]
        vacancies = int(row["vacancies"])
        score = int(row["score"])

        # --- карточка ---
        st.markdown(
            f"""
            <div style="
                background:#f8fbff;
                padding:16px;
                border-radius:14px;
                margin-bottom:10px;
                border:1px solid #e6ecf5;
            ">
                ⭐ <b>{city}</b> — {vacancies} вакансий  
                <span style="float:right; font-weight:600; color:#1f77b4;">
                    {score}%
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- стабильный прогресс-бар ---
        st.progress(score / 100)

    # ======================================================
    # 📊 ГРАФИК
    # ======================================================
    st.markdown("### 📊 CityFit Score по городам")
    st.bar_chart(city_stats.set_index("city")[["score"]])

    # ======================================================
    # 🔍 Explainable AI
    # ======================================================
    with st.expander("🔍 Почему именно эти города?"):
        st.markdown(
            """
            **CityFit AI** анализирует рынок вакансий по выбранной профессии:

            • 📌 количество вакансий в городе  
            • ⚖️ относительную силу рынка труда  
            • 🧠 сравнение городов между собой  

            **CityFit Score** — относительный показатель (0–100),
            а не реальный процент трудоустройства.
            """
        )


# ======================================================
# СТРАНИЦА CityFit AI
# ======================================================
def page_cityfit_ai():
    st.markdown("## 🌍 CityFit AI")
    st.markdown(
        """
        <p style="color:gray; font-size:16px;">
        Интеллектуальный ML-модуль, который показывает,
        <b>в каких городах выше шанс найти работу</b>
        по выбранной профессии
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🔎 Анализ по профессии")
    st.caption(
        "Введите профессию или ключевое слово — анализ выполняется по всем городам Казахстана"
    )

    profession = st.text_input(
        "Например: Data Analyst, Marketing, Python",
        placeholder="Data Analyst"
    )

    if profession:
        cityfit_ai_by_profession(profession)
    else:
        st.info("✍️ Введите профессию, чтобы увидеть анализ по городам")
