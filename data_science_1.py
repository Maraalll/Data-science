import streamlit as st
import pandas as pd

prof_df = pd.read_csv('prof.csv', delimiter=';')

df_new = pd.read_csv('hh_full_kz.csv')

specialty_keywords = {
    "Диджитал маркетинг": ["маркетолог", "digital marketing", "SEO", "SMM", "контент-маркетинг", "онлайн-реклама", "веб-аналитика"],
    "Менеджмент": ["менеджер", "управление проектами", "проектный менеджер", "менеджер по продажам", "операционный менеджер", "управление бизнесом"],
    "Учет и аудит": ["бухгалтер", "аудитор", "финансовый анализ", "финансовый отчет", "налоговый консультант", "управленческий учет", "инспектор"],
    "Финансы": ["финансовый аналитик", "бухгалтер", "финансовый менеджер", "управление активами", "финансовая отчетность", "инвестиции", "финансовые рынки"],
    "Экономика": ["экономист", "экономический анализ", "макроэкономика", "микроэкономика", "экономическое планирование", "планирование ресурсов"],
    "Информационные системы": ["информационные технологии", "системный аналитик", "разработчик ПО", "системный администратор", "базы данных", "IT-поддержка", "инфраструктура"],
    "Информационные системы для бизнеса": ["бизнес-аналитик", "информационные системы", "бизнес-процессы", "автоматизация", "IT-менеджер", "разработчик бизнес-систем"],
    "Компьютерные науки": ["программист", "разработчик ПО", "системный архитектор", "data science", "машинное обучение", "анализ данных", "нейросети", "искусственный интеллект"],
    "Математика": ["математик", "математическое моделирование", "математический анализ", "аналитик", "программист", "исследования данных", "статистика"],
    "Математическое и компьютерное моделирование": ["математическое моделирование", "симуляция", "исследования операций", "компьютерное моделирование", "анализ данных", "инженер", "системы моделирования"],
    "Мультимедийные науки": ["графический дизайнер", "видеомонтажер", "аниматор", "мультимедиа", "UX/UI дизайнер", "веб-дизайнер", "3D графика", "видеопродакшн"],
    "Программная инженерия": ["программист", "разработчик ПО", "системный архитектор", "инженер по разработке", "программирование", "Java", "Python", "C++"],
    "Статистика и наука о данных": ["статистик", "data scientist", "аналитик данных", "большие данные", "машинное обучение", "статистический анализ", "предсказательная аналитика", "data", "дата"],
    "Информатика": ["программист", "информатик", "разработчик ПО", "системный администратор", "анализ данных", "информационные технологии"],
    "История": ["историк", "архивист", "музейный работник", "преподаватель истории", "культурный проект", "научный сотрудник", "исследования"],
    "Казахский язык и литература": ["учитель казахского языка", "преподаватель литературы", "переводчик", "филолог", "казахская литература", "языкознание"],
    "Математика (педагогика)": ["педагог математики", "учитель математики", "образование", "методист", "учебный процесс", "педагогика", "методика обучения"],
    "Педагогика и методика начального обучения": ["учитель начальных классов", "педагог", "методист начального образования", "педагогика", "методика преподавания"],
    "Педагогика и Психология": ["педагог", "психолог", "образование", "психологическая поддержка", "психотерапевт", "социальная психология"],
    "Прикладная филология": ["филолог", "переводчик", "письменный перевод", "синхронный переводчик", "языкознание", "литературоведение"],
    "Русский язык и литература в школах с русским и нерусским языками обучения": ["учитель русского языка", "преподаватель литературы", "русский язык", "литературоведение", "школа", "образование"],
    "Социальная педагогика": ["социальный педагог", "психолог", "работа с детьми", "образовательные учреждения", "социальная работа", "педагогическая помощь"],
    "Международные отношения": ["дипломат", "международные отношения", "международная политика", "глобальные исследования", "экономика международных отношений"],
    "Мультимедиа и телевизионная журналистика": ["журналист", "мультимедийный редактор", "видеопроизводство", "телевизионная съемка", "журналистика", "СМИ"],
    "Право государственного управления": ["юрист", "государственное право", "государственная служба", "управление", "право", "законотворчество"],
    "Прикладное право": ["прикладной юрист", "гражданский юрист", "корпоративное право", "юридическое консультирование"],
    "Два иностранных языка": ["преподаватель английского", "учитель языка", "иностранные языки", "перевод", "филология", "английский", "немецкий", "французский", "language teacher", "translator"],
    "Переводческое дело": ["перевод", "переводчик", "синхронный перевод", "устный перевод", "письменный перевод", "локализация", "технический перевод", "интерпретатор", "лингвист", "language specialist"],
    "Математика (педагогика)": ["учитель математики", "преподавание", "методика"],
    "Физика": ["физик", "научный сотрудник", "исследование", "эксперимент", "оптика", "теоретическая физика", "прикладная физика", "лаборатория", "измерения"],
    "Химия": ["химик", "химический анализ", "лаборант", "органическая химия", "неорганическая химия", "фармацевтика", "реактивы", "аналитическая химия"],
    "Международное право": ["международное право", "юрист", "право", "международные организации", "международные договоры", "гуманитарное право", "дипломатия", "правозащита", "международные суды"],
    "Мультимедиа и теливизионная журналистика": ["журналист", "СМИ", "телевидение", "видеопроизводство", "оператор", "редактор", "телевизионная журналистика", "мультимедийный контент", "новости", "продюсер"],
    "Прикладная психология": ["психолог", "консультант", "психотерапия", "работа с клиентами", "коррекционная психология", "психодиагностика", "HR-специалист", "психология труда", "коучинг"]
}

def filter_vacancies_by_specialty(specialty):
    keywords = specialty_keywords.get(specialty, [])
    if not keywords:
        return pd.DataFrame()  
    filtered_df = df_new[df_new['name'].str.contains('|'.join(keywords), case=False, na=False)]
    return filtered_df

def page_find_vacancies():
    st.title("🎯Поиск вакансий для студентов и выпускников")

    faculty = st.selectbox("🏫 Выберите факультет", prof_df['Факультет'].unique())

    specialty = st.selectbox("💼 Выберите специальность", prof_df[prof_df['Факультет'] == faculty]['Специальность'].unique())

    city_name = st.selectbox("📍 Выберите город", df_new['city'].unique())
    if st.button("🔎Показать вакансии"):
        filtered_df = filter_vacancies_by_specialty(specialty)
    
        filtered_df = filtered_df[filtered_df['city'] == city_name]
    
        if not filtered_df.empty:
            st.write("✅Компании, которые ищут специалистов по выбранной специальности:")

            for _, row in filtered_df.iterrows():
                company_name = row['company']
                vacancy_link = row['url'] 
                st.markdown(f"[{company_name}]({vacancy_link})")
        else:
            st.write("🙁 Нет вакансий, соответствующих вашим критериям.")

