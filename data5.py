import streamlit as st
import pandas as pd
import numpy as np
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


st.set_page_config(
    page_title="Skill Match & Vacancy Fit",
    layout="wide"
)

#=========================
# 2. LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("hh_kazakhstan_final_dataset.csv.gz")

    df = df.dropna(subset=["name", "requirements"])
    df["requirements"] = df["requirements"].astype(str)

    return df.reset_index(drop=True)

df = load_data()

# =========================
# 3. TF-IDF MODEL
# =========================
@st.cache_resource
def build_vectorizer(texts):
    RUS_STOP_WORDS = [
    "и", "в", "на", "по", "с", "для", "из", "что", "это", "как",
    "к", "от", "до", "мы", "вы", "они", "он", "она", "при"
    ]
    vectorizer = TfidfVectorizer(
    stop_words=RUS_STOP_WORDS,
    max_features=5000
    )
    vectors = vectorizer.fit_transform(texts)
    return vectorizer, vectors

vectorizer, vacancy_vectors = build_vectorizer(df["requirements"])

# =========================
# 4. HELPER FUNCTIONS
# =========================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zа-я0-9+# ]", " ", text)
    return text


def extract_skills(text):
    return set(clean_text(text).split())


def match_vacancies(user_skills_text, top_n=5):
    user_skills_text = clean_text(user_skills_text)

    user_vector = vectorizer.transform([user_skills_text])
    similarities = cosine_similarity(user_vector, vacancy_vectors)[0]

    top_indices = np.argsort(similarities)[::-1][:top_n]
    results = df.iloc[top_indices].copy()

    results["fit_score"] = (similarities[top_indices] * 100).round(1)

    return results


def skill_gap(user_text, vacancy_text):
    user_skills = extract_skills(user_text)
    vacancy_skills = extract_skills(vacancy_text)

    matched = user_skills & vacancy_skills
    missing = vacancy_skills - user_skills

    return matched, missing

# =========================
# 5. UI
# =========================
def page_skill_match():

    st.title("🎯 Skill Match & Vacancy Fit Score")
    st.write(
        "ML-модуль, который показывает, **насколько вакансия подходит именно вам** "
        "на основе анализа навыков и требований."
    )

    st.markdown("---")

    user_skills = st.text_area(
        "🧠 Введите ваши навыки (через пробел или запятую)",
        placeholder="python sql pandas machine learning data analysis"
    )

    top_n = st.slider(
        "🔢 Количество вакансий для анализа",
        min_value=3,
        max_value=10,
        value=5
    )
    if st.button("🚀 Проверить соответствие"):

    if not user_skills.strip():
        st.warning("Введите навыки для анализа")
    else:
        results = match_vacancies(user_skills, top_n=top_n)

        # ===== Visualization =====
        st.markdown("## 📊 Топ вакансий по соответствию")

        viz_df = results[["name", "fit_score"]].copy()
        viz_df = viz_df.sort_values("fit_score", ascending=True)

        st.bar_chart(
            viz_df.set_index("name"),
            height=350
        )

        # ===== Detailed results =====
        st.markdown("## ✅ Результаты")

        for _, row in results.iterrows():
            st.markdown("---")

            st.subheader(row["name"])
            st.progress(row["fit_score"] / 100)

            st.write(f"**Fit Score:** {row['fit_score']}%")
            st.write(f"**Опыт:** {row.get('experience', 'не указан')}")
            st.write(f"**Компания:** {row.get('company', '')}")
            st.write(f"[🔗 Перейти к вакансии]({row.get('url', '#')})")
            
            matched, missing = skill_gap(user_skills, row["requirements"])
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### ✔ Совпадающие навыки")
                st.write(", ".join(sorted(matched)) if matched else "—")
            with col2:
                st.markdown("### ❌ Недостающие навыки")
                st.write(", ".join(list(missing)[:10]) if missing else "—")
