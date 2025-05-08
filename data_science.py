import streamlit as st
import data_science_1
import data_science_2
import data_science_3

st.set_page_config(page_title="Платформа для поиска работы", page_icon="💼", layout="wide")

# --- Custom CSS for Styling ---

st.sidebar.title("Навигация")
page = st.sidebar.radio("Выберите страницу:", [
    "Поиск вакансий",
    "Оценка компании",
    "Генератор резюме"
])

if page == "Поиск вакансий":
    data_science_1.page_find_vacancies()
elif page == "Оценка компании":
    data_science_2.page_rate_company()
elif page == "Генератор резюме":
    data_science_3.page_generate_resume()