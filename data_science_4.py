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
    
def match_vacancies(user_text, top_n=5, city="Все города"):
    filtered_df = df.copy()

    # --- фильтрация по городу ---
    if city != "Все города":
        filtered_df = filtered_df[filtered_df["city"] == city]

    # --- если после фильтрации пусто ---
    if filtered_df.empty:
        return pd.DataFrame()

    # --- векторизация ---
    texts = filtered_df["requirements"].fillna("")
    vectors = vectorizer.transform(texts)

    user_vector = vectorizer.transform([clean_text(user_text)])
    similarities = cosine_similarity(user_vector, vectors)[0]

    # --- топ вакансий ---
    top_idx = np.argsort(similarities)[::-1][:top_n]
    results = filtered_df.iloc[top_idx].copy()

    results["fit_score"] = (similarities[top_idx] * 100).round(1)

    # 🔹 пометка режима
    if city == "Все города":
        results["city_mode"] = "🌍 Все города"
    else:
        results["city_mode"] = f"📍 {city}"

    return results



# ======================================================
# ОСНОВНАЯ ЛОГИКА CityFit AI
# ======================================================
def cityfit_ai(user_city, profession=None):
    df = load_vacancies()

    all_cities_mode = user_city is None

    # --- фильтр по профессии (если выбрана) ---
    if profession:
        df = df[
            df["name"]
            .str.contains(profession, case=False, na=False)
        ]

    # --- статистика по городам ---
    city_stats = (
        df["city"]
        .value_counts()
        .reset_index()
    )
    city_stats.columns = ["city", "vacancies"]

    if city_stats.empty:
        st.warning("⚠️ По выбранной профессии вакансий не найдено")
        return

    # --- CityFit Score (нормализованный) ---
    city_stats["score"] = (
        city_stats["vacancies"] / city_stats["vacancies"].max() * 100
    ).round().astype(int)

    city_stats = city_stats.sort_values("score", ascending=False)

    # ======================================================
    # ВИЗУАЛЬНЫЕ КАРТОЧКИ
    # ======================================================
    st.markdown("### 🌍 В каком городе тебе будет проще найти работу?")
    if all_cities_mode:
        st.info("🌍 Анализ проводится по всем городам Казахстана")
    else:
        st.info(f"📍 Анализ проводится относительно города: **{user_city}**")


    for _, row in city_stats.head(5).iterrows():
        city = row["city"]
        vacancies = row["vacancies"]
        score = row["score"]

        icon = "⭐"
        label = "Recommended"
        if not all_cities_mode and city == user_city:
            icon = "📍"
            label = "Your city"

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
                        {icon} <b>{city}</b> — {vacancies} вакансий
                        <span style="color:#999; font-size:14px;">({label})</span>
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
    # 📊 ГРАФИК CityFit Score
    # ======================================================
    st.markdown("### 📊 CityFit Score по городам")

    chart_df = city_stats.set_index("city")[["score"]]
    st.bar_chart(chart_df)

    # ======================================================
    # 🔍 Explainable AI
    # ======================================================
    with st.expander("🔍 Почему именно эти города? (Explainable AI)"):
        st.markdown(
            """
            **CityFit AI** анализирует рынок вакансий и учитывает:

            • 📌 **Количество вакансий** — чем больше предложений, тем выше шанс  
            • ⚖️ **Относительную силу рынка** — сравнение городов между собой  
            • 🧠 **Профессию пользователя** — если выбрана, анализ становится персональным  

            **CityFit Score** — это нормализованный показатель (0–100),
            который помогает быстро понять, где старт карьеры будет проще.
            """
        )


# ======================================================
# СТРАНИЦА CityFit AI (UI + управление)
# ======================================================
def page_cityfit_ai():
    st.markdown("## 🌍 CityFit AI")
    st.markdown(
        "<p style='color:gray;'>"
        "Интеллектуальный ML-модуль, который показывает, "
        "<b>в каком городе твой шанс трудоустройства выше</b>, "
        "на основе анализа рынка вакансий"
        "</p>",
        unsafe_allow_html=True
    )

    # --- инициализация профиля ---
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}

    # --- выбор / смена города ---
    if "city" not in st.session_state.user_profile or st.session_state.get("change_city", False):

        st.info("📍 Выберите город")
        df = load_vacancies()

        all_cities = (
            df["city"]
            .dropna()
            .unique()
            .tolist()
        )
        all_cities = sorted(all_cities)
        cities = ["Все города 🌍"] + all_cities
        selected_city = st.selectbox(
            "🏙 Город:",
            cities
        )



        if st.button("✅ Подтвердить город"):
            if selected_city == "Все города 🌍":
                st.session_state.user_profile["city"] = None
            else:
                st.session_state.user_profile["city"] = selected_city
            st.session_state.change_city = False
            st.rerun()


    # --- выбранный город ---
    user_city = st.session_state.user_profile["city"]

    st.success(f"📍 Выбранный город: **{user_city}**")

    if st.button("🔄 Изменить город"):
        st.session_state.change_city = True
        st.rerun()

    # ======================================================
    # 🧠 УЧЁТ ПРОФЕССИИ
    # ======================================================
    st.markdown("### 🧠 Учитывать профессию")

    profession = st.text_input(
        "Введите профессию или ключевое слово (например: Data, Analyst, Marketing)",
        placeholder="Например: Data Analyst"
    )

    # --- запуск CityFit AI ---
    cityfit_ai(user_city, profession if profession else None)
