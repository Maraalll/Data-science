import streamlit as st
import data_science_1
import data_science_2
import data_science_3
st.set_page_config(page_title="Платформа для поиска работы", page_icon="💼", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1581091012184-7f3c64f2303b");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: white;
    }

    label, .stSelectbox label {
        color: white !important;
        font-weight: bold;
    }

    .stButton>button {
        background-color: #c94f7c;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
    }

    .stSelectbox>div>div {
        background-color: rgba(0, 0, 0, 0.6);
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.title("🌟 Навигация")
page = st.sidebar.radio("📄 Выберите страницу:", [
    "🔎 Поиск вакансий",
    "🏢 Оценка компании",
    "📝 Генератор резюме"
])

if page == "🔎 Поиск вакансий":
    data_science_1.page_find_vacancies()
elif page == "🏢 Оценка компании":
    data_science_2.page_rate_company()
elif page == "📝 Генератор резюме":
    data_science_3.page_generate_resume()

