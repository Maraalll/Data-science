import streamlit as st
import pandas as pd
import os
import numpy as np

@st.cache_data
def load_vacancies():
    file_path = os.path.join(
        os.path.dirname(__file__),
        "hh_kazakhstan_final_dataset.csv.gz"
    )
    return pd.read_csv(file_path)

def cityfit_ai_by_profession(profession: str):
    df = load_vacancies()

    df_prof = df[
        df["name"].str.contains(profession, case=False, na=False)
    ]

    if df_prof.empty:
        st.warning("⚠️ По этой профессии вакансий не найдено")
        return

    city_stats = (
        df_prof["city"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    city_stats.columns = ["city", "vacancies"]

    city_stats["score"] = (
        np.log1p(city_stats["vacancies"])
        / np.log1p(city_stats["vacancies"].max())
        * 100
    ).round().astype(int)

    city_stats = city_stats.sort_values("score", ascending=False)

    st.markdown("## 🌍 Города с вакансиями по выбранной профессии")
    st.info(f"🔎 **Профессия:** {profession}")

    for _, row in city_stats.iterrows():
        city = row["city"]
        vacancies = row["vacancies"]
        score = row["score"]

    
        st.markdown(
            f"""
            <div style="
                background:#f8fbff;
                padding:16px;
                border-radius:14px;
                margin-bottom:8px;
                border:1px solid #e3ecf7;
            ">
                <div style="display:flex; justify-content:space-between; align-items:center;">
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
                    height:8px;
                    margin-top:10px;
                ">
                    <div style="
                        width:{score}%;
                        background:linear-gradient(90deg,#4facfe,#00f2fe);
                        height:8px;
                        border-radius:10px;
                    "></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

      
        with st.expander(f"📋 Показать вакансии в {city}"):
            city_vacancies = df_prof[df_prof["city"] == city]

            for _, v in city_vacancies.iterrows():
                st.markdown(
                    f"""
                    • **{v['name']}**  
                    🏢 {v.get('company', 'Компания не указана')}  
                    🔗 [Открыть вакансию]({v.get('url', '#')})
                    """
                )

    st.markdown("## 📊 CityFit Score по городам")
    st.bar_chart(city_stats.set_index("city")[["score"]])


    with st.expander("🔍 Почему именно эти города?"):
        st.markdown(
            """
            **CityFit AI** анализирует рынок вакансий:

            • 📌 количество вакансий по профессии  
            • ⚖️ сравнение городов между собой  
            • 🧠 нормализацию, чтобы не было перекоса  

            **CityFit Score** — относительный показатель (0–100),
            а не гарантия трудоустройства.
            """
        )


def page_cityfit_ai():
    st.markdown("## 🌍 CityFit AI")
    st.caption(
        "Интеллектуальный ML-модуль, который показывает, "
        "в каких городах выше шанс найти работу по профессии"
    )

    profession = st.text_input(
        "🔎 Введите профессию или ключевое слово",
        placeholder="Data Analyst"
    )

    if profession:
        cityfit_ai_by_profession(profession)
    else:
        st.info("✍️ Введите профессию, чтобы начать анализ")
