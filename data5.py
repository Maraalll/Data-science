import streamlit as st
import pandas as pd
import numpy as np
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("hh_kazakhstan_final_dataset.csv.gz")

    df = df.dropna(subset=["name", "requirements", "city"])
    df["requirements"] = df["requirements"].astype(str)
    df["city"] = df["city"].astype(str)

    return df.reset_index(drop=True)


df = load_data()


# =========================
# MODEL
# =========================
@st.cache_resource
def build_vectorizer(texts):
    vectorizer = TfidfVectorizer(max_features=5000)
    vectors = vectorizer.fit_transform(texts)
    return vectorizer, vectors


vectorizer, vacancy_vectors = build_vectorizer(df["requirements"])


# =========================
# HELPERS
# =========================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zа-я0-9+# ]", " ", text)
    return text


def extract_skills(text):
    return set(clean_text(text).split())


def skill_gap(user_text, vacancy_text):
    user_skills = extract_skills(user_text)
    vacancy_skills = extract_skills(vacancy_text)

    matched = user_skills & vacancy_skills
    missing = vacancy_skills - user_skills

    return matched, missing


def match_vacancies(user_text, top_n=5, city="Все города"):
    filtered_df = df.copy()

    if city != "Все города":
        filtered_df = filtered_df[filtered_df["city"] == city]

    if filtered_df.empty:
        return pd.DataFrame()

    texts = filtered_df["requirements"]
    vectors = vectorizer.transform(texts)

    user_vector = vectorizer.transform([clean_text(user_text)])
    similarities = cosine_similarity(user_vector, vectors)[0]

    top_idx = np.argsort(similarities)[::-1][:top_n]

    results = filtered_df.iloc[top_idx].copy()
    results["fit_score"] = (similarities[top_idx] * 100).round(1)

    return results


# =========================
# PAGE UI
# =========================
def page_skill_match():
    st.title("🎯 Skill Match / Vacancy Fit")

    st.write(
        "ML-модуль подбирает вакансии **по вашим навыкам и городу.** "
    )

    st.markdown("---")

    # --- user input ---
    user_skills = st.text_area(
        "🧠 Введите ваши навыки",
        placeholder="python sql pandas machine learning"
    )

    cities = sorted(df["city"].unique())
    cities.insert(0, "Все города")

    selected_city = st.selectbox(
        "📍 Выберите город",
        cities
    )

    top_n = st.slider(
        "🔢 Количество вакансий",
        min_value=3,
        max_value=10,
        value=5
    )

    if st.button("🚀 Проверить соответствие"):

        if not user_skills.strip():
            st.warning("Введите навыки для анализа")
            return

        results = match_vacancies(
            user_skills,
            top_n=top_n,
            city=selected_city
        )

        if results.empty:
            st.warning("Нет вакансий по выбранному городу")
            return

        # =========================
        # VISUALIZATION
        # =========================
        st.markdown("## 📊 Топ вакансий по соответствию")

        chart_df = (
            results[["name", "fit_score"]]
            .sort_values("fit_score")
            .set_index("name")
        )

        st.bar_chart(chart_df, height=350)

        # =========================
        # RESULTS
        # =========================
        st.markdown("## ✅ Результаты")

        for _, row in results.iterrows():
            st.markdown("---")

            st.subheader(row["name"])
            st.progress(row["fit_score"] / 100)

            st.write(f"**Fit Score:** {row['fit_score']}%")
            st.write(f"**Город:** {row.get('city', '')}")
            st.write(f"**Опыт:** {row.get('experience', 'не указан')}")
            st.write(f"**Компания:** {row.get('company', '')}")
            st.write(f"[🔗 Перейти к вакансии]({row.get('url', '#')})")

            matched, missing = skill_gap(
                user_skills,
                row["requirements"]
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### ✔ Совпадающие навыки")
                st.write(", ".join(sorted(matched)) if matched else "—")

            with col2:
                st.markdown("### ❌ Недостающие навыки")
                st.write(", ".join(list(missing)[:10]) if missing else "—")
