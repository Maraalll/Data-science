import streamlit as st
import pandas as pd

# Загрузка данных
companies_df = pd.read_csv('companies.csv')
reviews_df = pd.read_csv('reviews.csv')

# Функция для обновления среднего рейтинга
def update_average_rating(company_name):
    company_reviews = reviews_df[reviews_df['company'] == company_name]
    if len(company_reviews) > 0:
        avg_work_conditions = company_reviews['work_conditions'].mean()
        avg_culture = company_reviews['culture'].mean()
        avg_management = company_reviews['management'].mean()
        # Вычисляем общий средний рейтинг по всем категориям
        avg_overall = (avg_work_conditions + avg_culture + avg_management) / 3
        return avg_work_conditions, avg_culture, avg_management, avg_overall
    else:
        return "Нет отзывов", "Нет отзывов", "Нет отзывов", "Нет отзывов"

# Функция для отображения всех вопросов и ответов
def display_questions_and_answers(company_name, worked):
    company_reviews = reviews_df[reviews_df['company'] == company_name]

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
                    st.write("<i>Ответ еще не дан.</i>", unsafe_allow_html=True)
                    if worked == 'Да':  # Только те, кто работал в компании, могут ответить
                        answer = st.text_area(f"Ответить на вопрос: {row['question_text']}", key=f"answer_{idx}")
                        if st.button(f"Отправить ответ", key=f"submit_answer_{idx}"):
                            # Сохраняем ответ в DataFrame
                            reviews_df.at[idx, 'answer_text'] = answer
                            reviews_df.to_csv('reviews.csv', index=False)
                            st.write("Ваш ответ был отправлен!")
def page_rate_company():
    st.title("Оценка компании")

    # Шаг 1: Запрос имени и фамилии
    first_name = st.text_input("Ваше имя:")
    last_name = st.text_input("Ваша фамилия:")

    if first_name and last_name:
        st.write(f"Привет, {first_name} {last_name}! Рады видеть вас на платформе оценки компаний.")

        # Шаг 2: Выбор компании
        company_name = st.selectbox("Выберите компанию", companies_df['company'].unique())

        # Шаг 3: Показываем средние рейтинги
        avg_work_conditions, avg_culture, avg_management, avg_overall = update_average_rating(company_name)

        st.write(f"### Средняя оценка для **{company_name}**")
        st.metric("Условия труда", avg_work_conditions if isinstance(avg_work_conditions, (int, float)) else "Нет данных")
        st.metric("Корпоративная культура", avg_culture if isinstance(avg_culture, (int, float)) else "Нет данных")
        st.metric("Управление", avg_management if isinstance(avg_management, (int, float)) else "Нет данных")
        st.metric("Общий рейтинг", avg_overall if isinstance(avg_overall, (int, float)) else "Нет данных")

        # Шаг 4: Ввод отзыва или вопроса
        worked = st.radio("Вы работали в этой компании?", ('Нет', 'Да'))

        if worked == 'Нет':
            question = st.text_area("Задайте вопрос о компании:")
            if st.button("Отправить вопрос"):
                # Сохраняем вопрос в DataFrame
                new_question = pd.DataFrame({'company': [company_name], 'question_text': [question], 'answer_text': [None], 'user_name': [first_name + ' ' + last_name], 'worked': ['Нет']})
                reviews_df = pd.concat([reviews_df, new_question], ignore_index=True)  # Используем concat вместо append
                reviews_df.to_csv('reviews.csv', index=False)  # Сохраняем обновленный DataFrame
                st.write("Ваш вопрос был отправлен!")
        else:
            review = st.text_area("Ваш отзыв о компании:")
            work_conditions = st.slider("Оцените условия труда", 1, 5)
            culture = st.slider("Оцените корпоративную культуру", 1, 5)
            management = st.slider("Оцените управление", 1, 5)

            if st.button("Отправить отзыв"):
                # Сохраняем отзыв в DataFrame
                new_review = pd.DataFrame({'company': [company_name], 'work_conditions': [work_conditions], 'culture': [culture], 'management': [management], 'review_text': [review], 'question_text': [None], 'answer_text': [None], 'user_name': [first_name + ' ' + last_name], 'worked': ['Да']})
                reviews_df = pd.concat([reviews_df, new_review], ignore_index=True)  # Используем concat вместо append
                reviews_df.to_csv('reviews.csv', index=False)  # Сохраняем обновленный DataFrame
                st.write("Ваш отзыв был отправлен!")

        # Шаг 5: Показать все вопросы и ответы
        if st.checkbox("Показать вопросы и ответы"):
            display_questions_and_answers(company_name, worked)
    else:
        st.warning("Пожалуйста, введите ваше имя и фамилию для продолжения.")