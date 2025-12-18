import streamlit as st
import pandas as pd

# =========================
# ЗАГРУЗКА ДАННЫХ
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("hh_kazakhstan_final_dataset.csv.gz")

    # обязательные колонки
    required_cols = [
        "city",
        "vacancy_name",
        "vacancy_url",
        "cityfit_score"
    ]
    df = df.dropna(subset=required_cols)

    return df


# =========================
# ОСНОВНАЯ СТРАНИЦА
# =========================
def page_cityfit_ai():
    st.markdown("## 🌍 CityFit AI")
    st.markdown(
        "Интеллектуальный модуль, показывающий, **в каких городах выше шанс найти работу** "
        "по выбранной профессии."
    )

    df = load_data()

    # =========================
    # ВВОД ПРОФЕССИИ
    # =========================
    profession = st.text_input(
        "🔍 Введите профессию или ключевое слово",
        placeholder="Data Analyst, Python, Marketing..."
    )

    if not profession:
        st.info("👉 Введите профессию, чтобы увидеть топ городов")
        return

    # =========================
    # ФИЛЬТРАЦИЯ ПО ПРОФЕССИИ
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
        df_prof[df_prof["cityfit_score"] > 0]
        .groupby("city")
        .agg(
            vacancies=("vacancy_name", "count"),
            cityfit_score=("cityfit_score", "mean")
        )
        .reset_index()
        .sort_values("cityfit_score", ascending=False)
        .head(10)
    )

    st.markdown("### 🏙️ Топ-10 городов по CityFit")

    # =========================
    # ВЫВОД ГОРОДОВ + КЛИК
    # =========================
    for idx, row in city_stats.iterrows():
        city = row["city"]
        vacancies_count = row["vacancies"]

        with st.expander(f"📍 **{city} — {vacancies_count} вакансий**"):
            city_vacancies = df_prof[df_prof["city"] == city]

            for _, v in city_vacancies.iterrows():
                st.markdown(
                    f"- 🔗 [{v['vacancy_name']}]({v['vacancy_url']})"
                )
