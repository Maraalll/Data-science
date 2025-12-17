import streamlit as st
import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LogisticRegression


# =========================
# Загрузка данных
# =========================
@st.cache_data
def load_vacancies():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "hh_kazakhstan_final_dataset.csv.gz"
    )
    return pd.read_csv(file_path)


# =========================
# Обучение ML-модели
# =========================
@st.cache_resource
def train_cityfit_model(city_stats):
    X = []
    y = []

    median_vacancies = city_stats["vacancies"].median()

    for _, row in city_stats.iterrows():
        X.append([row["vacancies"]])
        y.append(1 if row["vacancies"] >= median_vacancies else 0)

    model = LogisticRegression()
    model.fit(X, y)
    return model


# =========================
# Основная ML-логика
# =========================
def cityfit_ai(user_city):
    df = load_vacancies()

    city_stats = (
        df["city"]
        .value_counts()
        .reset_index()
    )
    city_stats.columns = ["city", "vacancies"]

    model = train_cityfit_model(city_stats)

    probabilities = []
    for _, row in city_stats.iterrows():
        prob = model.predict_proba(
            np.array([[row["vacancies"]]])
        )[0][1]
        probabilities.append(prob)

    city_stats["chance"] = probabilities
    city_stats = city_stats.sort_values("chance", ascending=False)

    # =========================
    # UI
    # =========================
    st.markdown("## 🌍 CityFit AI")
    st.markdown(
        "<p style='color:gray;'>"
        "Интеллектуальный ML-модуль, который показывает, "
        "<b>в каком городе твой шанс трудоустройства выше</b>, "
        "на основе анализа рынка вакансий"
        "</p>",
        unsafe_allow_html=True
    )

    for _, row in city_stats.head(5).iterrows():
        city = row["city"]
        vacancies = row["vacancies"]
        chance = int(row["chance"] * 100)

        icon = "⭐"
        if city == user_city:
            icon = "📍"

        st.markdown(
            f"""
            <div style="
                background:#f4f8fb;
                padding:16px;
                border-radius:14px;
                margin-bottom:10px;
                font-size:18px;
            ">
                {icon} <b>{city}</b> — {vacancies} вакансий  
                <span style="float:right; color:#1f77b4; font-weight:bold;">
                    {chance}% шанс
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================
# Страница (как у других модулей)
# =========================
def page_cityfit_ai():
    user_city = st.session_state.get("user_profile", {}).get("city")

    if not user_city:
        st.warning("Сначала выберите город в онбординге")
        return

    cityfit_ai(user_city)
