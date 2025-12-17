import streamlit as st
import pandas as pd
import os
from sklearn.linear_model import LogisticRegression
import numpy as np

@st.cache_data
def load_data():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "hh_kazakhstan_final_dataset.csv.gz"
    )
    return pd.read_csv(file_path)


@st.cache_resource
def train_city_model(city_stats):
    """
    Обучаем ML-модель:
    X = [num_vacancies, is_user_city]
    y = высокий шанс трудоустройства (1/0)
    """

    X = []
    y = []

    median_vacancies = city_stats["num_vacancies"].median()

    for _, row in city_stats.iterrows():
        X.append([row["num_vacancies"], 1])
        y.append(1 if row["num_vacancies"] >= median_vacancies else 0)

    model = LogisticRegression()
    model.fit(X, y)

    return model


def city_recommendation_ml(user_city):
    df = load_data()

    # 1️⃣ статистика по городам
    city_stats = (
        df["city"]
        .value_counts()
        .reset_index()
    )
    city_stats.columns = ["city", "num_vacancies"]

    # 2️⃣ обучаем модель
    model = train_city_model(city_stats)

    # 3️⃣ предсказываем вероятность для каждого города
    probabilities = []

    for _, row in city_stats.iterrows():
        is_user_city = 1 if row["city"] == user_city else 0
        X_test = np.array([[row["num_vacancies"], is_user_city]])
        prob = model.predict_proba(X_test)[0][1]
        probabilities.append(prob)

    city_stats["probability"] = probabilities

    # 4️⃣ сортировка по вероятности
    city_stats = city_stats.sort_values(
        "probability",
        ascending=False
    )

    # 5️⃣ UI
    st.markdown("## 🌍 В каком городе тебе будет проще найти работу?")
    st.markdown(
        "<p style='color:gray;'>ML-модель оценила вероятность трудоустройства по городам</p>",
        unsafe_allow_html=True
    )

    for _, row in city_stats.head(5).iterrows():
        city = row["city"]
        count = row["num_vacancies"]
        prob = int(row["probability"] * 100)

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
                {icon} <b>{city}</b> — {count} вакансий  
                <span style="float:right; color:#1f77b4;">
                    {prob}% шанс
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

