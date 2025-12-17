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
    df = df.dropna(subset=["name", "requirements"])
    df["requirements"] = df["requirements"].astype(str)
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


def match_vacancies(user_text, top_n=5):
    user_vector = vectorizer.transform([clean_text(user_text)])
    similarities = cosine_similarity(user_vector, vacancy_vectors)[0]
    top_idx = np.argsort(similarities)[::-1][:top_n]

    results = df.iloc[top_idx].copy()
    results["fit_score"] = (similarities[top_idx] * 100).round(1)
    return results


# =========================
# PAGE UI
# =========================
def page_skill_match():
    st.title("🎯 Skill Match / Fit")

    user_skills = st.text_area(
        "🧠 Введите ваши навыки",
        placeholder="python sql pandas machine learning"
    )

    top_n = st.slider("🔢 Количество вакансий", 3, 10, 5)

    if st.button("🚀 Проверить соответствие"):
        if not user_skills.strip():
            st.warning("Введите навыки")
        else:
            results = match_vacancies(user_skills, top_n)

            st.markdown("## 📊 Топ вакансий по соответствию")
            chart_df = results[["name", "fit_score"]].set_index("name")
            st.bar_chart(chart_df)

            st.markdown("## ✅ Результаты")
            for _, row in results.iterrows():
                st.markdown("---")
                st.subheader(row["name"])
                st.progress(row["fit_score"] / 100)
                
                st.write(f"**Fit Score:** {row['fit_score']}%")
                st.write(f"**Опыт:** {row.get('experience', 'не указан')}")
                st.write(f"**Компания:** {row.get('company', '')}")
                st.write(f"[🔗 Перейти к вакансии]({row.get('url', '#')})")
                # 🔍 анализ навыков
                matched, missing = skill_gap(user_skills, row["requirements"])

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### ✔ Совпадающие навыки")
                    if matched:
                        st.write(", ".join(sorted(matched)))
                    else:
                        st.write("—")
                with col2:
                    st.markdown("### ❌ Недостающие навыки")
                    if missing:
                        st.write(", ".join(list(missing)[:10]))
                    else:
                        st.write("—")
