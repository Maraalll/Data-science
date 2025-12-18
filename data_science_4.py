import streamlit as st
import pandas as pd


# =========================
# ЗАГРУЗКА ДАННЫХ (БЕЗ ОШИБОК)
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("hh_kazakhstan_final_dataset.csv.gz")

    # 🛡️ Унификация колонок
    column_map = {
        "name": "vacancy_name",
        "vacancy_name": "vacancy_name",
        "url": "vacancy_url",
        "vacancy_url": "vacancy_url",
        "area_name": "city",
        "city": "city"
    }

    df = df.rename(columns=column_map)

    # если cityfit_score нет — создаём фиктивный (по количеству вакансий)
    if "cityfit_score" not in df.columns:
        df["cityfit_score"] = 1.0

    required_cols = ["city", "vacancy_name", "vacancy_url", "cityfit_score"]

    # оставляем только реально существующие
    existing_cols = [c for c in required_cols if c in df.columns]

    df = df.dropna(subset=existing_cols)

    return df


# =========================
# ОСНОВНАЯ СТРАНИЦА
# =========================
def page_cityfit_ai():
    st.markdown("## 🌍 CityFit AI")
    st.markdown(
        "Показывает **в каких городах больше всего релевантных вакансий** "
        "по выбранной профессии."
    )

    df = load_data()

    profession = st.text_input(
        "🔍 Введите профессию или ключевое слово",
        placeholder="Data Analyst, Python, Marketing..."
    )

    if not profession:
        st.info("👉 Введите профессию, чтобы увидеть топ городов")
        return

    # =========================
    # ФИЛЬТРАЦИЯ
    # =========================
    mask = df["vacancy_name"].str.contains(profession, case=False, na=False)
    df_prof = df[mask]

    if df_prof.empty:
        st.warning("❌ По этой профессии вакансий не найдено")
        return

    # =========================
    # ТОП-10 ГОРОДОВ
    # =========================
    city_stats = (
        df_prof
        .groupby("city")
        .agg(vacancies=("vacancy_name", "count"))
        .reset_index()
        .sort_values("vacancies", ascending=False)
        .head(10)
    )

    st.markdown("### 🏙️ Топ-10 городов")

    # =========================
    # КЛИК → ССЫЛКИ
    # =========================
    for _, row in city_stats.iterrows():
        city = row["city"]
        count = row["vacancies"]

        with st.expander(f"📍 **{city} — {count} вакансий**"):
            city_vacancies = df_prof[df_prof["city"] == city]

            for _, v in city_vacancies.iterrows():
                st.markdown(
                    f"- 🔗 [{v['vacancy_name']}]({v['vacancy_url']})"
                )
