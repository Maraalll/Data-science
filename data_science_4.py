import streamlit as st
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("hh_kazakhstan_final_dataset.csv.gz")

    required_cols = ["name", "description", "city", "url"]
    df = df.dropna(subset=required_cols)

    df["text"] = (
        df["name"].astype(str) + " " + df["description"].astype(str)
    )

    return df.reset_index(drop=True)


# =========================
# CITYFIT ML BLOCK
# =========================
def compute_cityfit(df, query, threshold=0.25):
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english"
    )

    X = vectorizer.fit_transform(df["text"])
    q_vec = vectorizer.transform([query])

    sims = cosine_similarity(q_vec, X).flatten()
    df["similarity"] = sims

    df_rel = df[df["similarity"] >= threshold]

    city_stats = (
        df.groupby("city")
        .size()
        .rename("vacancies")
        .reset_index()
    )

    city_rel = (
        df_rel.groupby("city")
        .size()
        .rename("relevant")
        .reset_index()
    )

    cityfit = city_stats.merge(city_rel, on="city", how="left")
    cityfit["relevant"] = cityfit["relevant"].fillna(0)

    cityfit["cityfit_score"] = (
        cityfit["relevant"] / cityfit["vacancies"]
    )

    cityfit = cityfit.sort_values(
        "cityfit_score", ascending=False
    )

    return cityfit, df_rel


# =========================
# PAGE
# =========================
def page_cityfit_ai():
    st.markdown("## 🌍 CityFit AI")
    st.markdown(
        "ML-модуль, который показывает **в каких городах выше шанс найти работу по профессии**"
    )

    query = st.text_input(
        "🔍 Введите профессию или ключевое слово",
        placeholder="Data Analyst"
    )

    if not query:
        st.info("👉 Введите профессию, чтобы запустить ML-анализ")
        return

    df = load_data()

    with st.spinner("🤖 ML-анализ вакансий..."):
        cityfit, df_rel = compute_cityfit(df, query)

    top10 = cityfit.head(10)

    # =========================
    # BAR CHART
    # =========================
    st.markdown("### 📊 Топ-10 городов по CityFit Score")

    st.bar_chart(
        top10.set_index("city")["cityfit_score"]
    )

    # =========================
    # TABLE
    # =========================
    st.dataframe(
        top10[["city", "vacancies", "relevant", "cityfit_score"]],
        use_container_width=True
    )

    # =========================
    # LINKS
    # =========================
    st.markdown("### 🔗 Вакансии по городам")

    for city in top10["city"]:
        with st.expander(f"📍 {city}"):
            city_jobs = df_rel[df_rel["city"] == city].head(10)

            if city_jobs.empty:
                st.caption("Нет релевантных вакансий")
            else:
                for _, row in city_jobs.iterrows():
                    st.markdown(f"- [{row['name']}]({row['url']})")
