import gspread
import streamlit as st
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Подключение к Google Sheets

def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open("reviews").sheet1  # Убедись, что таблица называется "reviews"
    return sheet

# Загрузка данных из таблицы

def load_data():
    try:
        companies_df = pd.read_csv('companies.csv')
        sheet = connect_to_gsheet()
        data = sheet.get_all_records()
        reviews_df = pd.DataFrame(data)
        return companies_df, reviews_df
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")
        return None, None

# Добавление новой строки в таблицу

def save_review_row(row_dict):
    sheet = connect_to_gsheet()
    sheet.append_row(list(row_dict.values()))

# Обновление среднего рейтинга

def update_average_rating(company_name):
    company_reviews = st.session_state.reviews_df[st.session_state.reviews_df['company'] == company_name]

    if len(company_reviews) > 0:
        try:
            avg_work_conditions = company_reviews['work_conditions'].replace('', pd.NA).dropna().astype(float).mean()
            avg_culture = company_reviews['culture'].replace('', pd.NA).dropna().astype(float).mean()
            avg_management = company_reviews['management'].replace('', pd.NA).dropna().astype(float).mean()
            avg_overall = (avg_work_conditions + avg_culture + avg_management) / 3
            return avg_work_conditions, avg_culture, avg_management, avg_overall
        except Exception as e:
            st.warning(f"Ошибка при расчёте среднего рейтинга: {e}")
            return "Недостаточно данных", "Недостаточно данных", "Недостаточно данных", "Недостаточно данных"
    else:
        return "Нет отзывов", "Нет отзывов", "Нет отзывов", "Нет отзывов"

# Показ отзывов

def display_employee_reviews(company_name):
    reviews = st.session_state.reviews_df
    filtered = reviews[(reviews['company'] == company_name) & (reviews['worked'] == 'Да') & (reviews['review_text'].notna())]

    st.write(f"### Отзывы сотрудников о {company_name}:")
    if filtered.empty:
        st.write("Пока нет отзывов от работников этой компании.")
    else:
        for _, row in filtered.iterrows():
            st.markdown(f"**{row['user_name']}**: {row['review_text']}")
            st.markdown(f"  - Условия труда: {row['work_conditions']}, Культура: {row['culture']}, Управление: {row['management']}")

# Вопросы и ответы

def display_questions_and_answers(company_name, worked):
    company_reviews = st.session_state.reviews_df[st.session_state.reviews_df['company'] == company_name]

    if company_reviews.empty:
        st.write("Нет вопросов для этой компании.")
    else:
        st.write(f"Вопросы и ответы для компании {company_name}:")
        for idx, row in company_reviews.iterrows():
            if pd.notna(row['question_text']):
                st.write(f"Вопрос: {row['question_text']}")
                if pd.notna(row['answer_text']):
                    st.write(f"Ответ: {row['answer_text']}")
                else:
                    st.write("Ответ еще не дан.")
                    if worked == 'Да':
                        answer = st.text_area(f"Ответить на вопрос: {row['question_text']}", key=f"answer_{idx}")
                        if st.button(f"Отправить ответ", key=f"submit_answer_{idx}"):
                            # ❗ Нельзя обновлять ячейку напрямую — для этого нужен другой подход
                            st.warning("Редактирование ответов через Google Sheets пока не реализовано. Только добавление новых строк.")

# Главная страница

def page_rate_company():
    st.title("Оценка компании")

    if 'companies_df' not in st.session_state or 'reviews_df' not in st.session_state:
        st.session_state.companies_df, st.session_state.reviews_df = load_data()

    if st.session_state.companies_df is None or st.session_state.reviews_df is None:
        st.stop()

    first_name = st.text_input("Ваше имя:")
    last_name = st.text_input("Ваша фамилия:")

    if first_name and last_name:
        st.write(f"Привет, {first_name} {last_name}! Рады видеть вас на платформе оценки компаний.")

        company_name = st.selectbox("Выберите компанию", st.session_state.companies_df['company'].unique())

        avg_work_conditions, avg_culture, avg_management, avg_overall = update_average_rating(company_name)
        st.write(f"### Средняя оценка для **{company_name}**")
        st.metric("Условия труда", avg_work_conditions)
        st.metric("Корпоративная культура", avg_culture)
        st.metric("Управление", avg_management)
        st.metric("Общий рейтинг", avg_overall)

        worked = st.radio("Вы работали в этой компании?", ('Нет', 'Да'))

        if worked == 'Нет':
            question = st.text_area("Задайте вопрос о компании:")
            if st.button("Отправить вопрос"):
                new_question = {
                    'company': company_name,
                    'question_text': question,
                    'answer_text': None,
                    'user_name': first_name + ' ' + last_name,
                    'worked': 'Нет',
                    'review_text': None,
                    'work_conditions': '',
                    'culture': '',
                    'management': ''
                }
                save_review_row(new_question)
                st.success("Ваш вопрос был отправлен!")
        else:
            review = st.text_area("Ваш отзыв о компании:")
            work_conditions = st.slider("Оцените условия труда", 1, 5)
            culture = st.slider("Оцените корпоративную культуру", 1, 5)
            management = st.slider("Оцените управление", 1, 5)

            if st.button("Отправить отзыв"):
                new_review = {
                    'company': company_name,
                    'question_text': None,
                    'answer_text': None,
                    'user_name': first_name + ' ' + last_name,
                    'worked': 'Да',
                    'review_text': review,
                    'work_conditions': work_conditions,
                    'culture': culture,
                    'management': management
                }
                save_review_row(new_review)
                st.success("Ваш отзыв был отправлен!")

        if st.checkbox("Показать вопросы и ответы"):
            display_questions_and_answers(company_name, worked)

        if st.checkbox("Показать отзывы сотрудников"):
            display_employee_reviews(company_name)
    else:
        st.warning("Пожалуйста, введите ваше имя и фамилию для продолжения.")

