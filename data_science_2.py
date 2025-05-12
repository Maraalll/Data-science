import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
# Подключение к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "reviews"

@st.cache_resource
def connect_to_gsheet():
    service_account_info = st.secrets["google_service_account"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, SCOPE)
    client = gspread.authorize(credentials)
    sheet = client.open(SPREADSHEET_NAME).sheet1
    return sheet

# Загрузка данных
@st.cache_data(show_spinner=False)
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

# Сохранение нового отзыва или вопроса
def save_review_row(row_data):
    sheet = connect_to_gsheet()
    sheet.append_row([row_data.get("company", ""), row_data.get("question_text", ""), row_data.get("answer_text", ""),
                      row_data.get("user_name", ""), row_data.get("worked", ""), row_data.get("review_text", ""),
                      row_data.get("work_conditions", ""), row_data.get("culture", ""), row_data.get("management", "")])

# Расчет среднего рейтинга
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
            st.warning(f"Ошибка при расчёте рейтинга: {e}")
            return "Недостаточно данных", "Недостаточно данных", "Недостаточно данных", "Недостаточно данных"
    else:
        return "Нет отзывов", "Нет отзывов", "Нет отзывов", "Нет отзывов"

# Отображение вопросов и ответов
def display_questions_and_answers(company_name, worked):
    company_reviews = st.session_state.reviews_df[st.session_state.reviews_df['company'] == company_name]
    unanswered = company_reviews[company_reviews['answer_text'].isna() | (company_reviews['answer_text'] == '')]
    if unanswered.empty:
        st.write("Нет вопросов без ответов.")
    else:
        st.write("Вопросы без ответов:")
        for idx, row in unanswered.iterrows():
            st.write(f"**{row['user_name']} спрашивает:** {row['question_text']}")
            if worked == 'Да':
                answer = st.text_area("Ответить на вопрос:", key=f"answer_{idx}")
                if st.button("Отправить ответ", key=f"submit_answer_{idx}"):
                    sheet = connect_to_gsheet()
                    cell = sheet.find(row['question_text'])
                    sheet.update_cell(cell.row, 3, answer)
                    st.success("Ответ отправлен! Обновите страницу для обновления списка.")

# Отображение отзывов
def display_employee_reviews(company_name):
    reviews = st.session_state.reviews_df
    filtered = reviews[(reviews['company'] == company_name) & (reviews['worked'] == 'Да') & (reviews['review_text'] != '')]
    if filtered.empty:
        st.write("Нет отзывов о компании.")
    else:
        st.write("Отзывы сотрудников:")
        for _, row in filtered.iterrows():
            st.write(f"▶️ {row['user_name']} говорит: {row['review_text']}")

# Основная функция

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
                    'answer_text': '',
                    'user_name': first_name + ' ' + last_name,
                    'worked': 'Нет',
                    'review_text': '',
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
                    'question_text': '',
                    'answer_text': '',
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
