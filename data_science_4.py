import re
import numpy as np
import pandas as pd
import streamlit as st

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score


@st.cache_data
def load_cityfit_data():
    df = pd.read_csv("hh_kazakhstan_final_dataset.csv.gz")

    # минимальная очистка
    for col in ["name", "requirements", "responsibilities", "city"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)

    df = df[df["city"].str.len() > 0].copy()
    df.reset_index(drop=True, inplace=True)
    return df


def _normalize_query(q: str) -> str:
    q = q.strip().lower()
    q = re.sub(r"\s+", " ", q)
    return q


def _tokenize(q: str):
    # достанем слова/цифры, уберем совсем короткие
    tokens = re.findall(r"[a-zA-Zа-яА-Я0-9\+#\.\-]{2,}", q.lower())
    # чуть-чуть “умнее”: убираем супер-общие
    bad = {"junior", "middle", "senior", "intern", "стажер", "стажёр", "опыт", "experience"}
    tokens = [t for t in tokens if t not in bad]
    return tokens


def _weak_labels_from_title(title_series: pd.Series, query: str) -> np.ndarray:
    """
    Weak supervision:
    y=1 если хотя бы один токен из запроса встречается в названии вакансии.
    Это дает нам разметку для обучения Logistic Regression (TF-IDF).
    """
    tokens = _tokenize(query)
    if not tokens:
        return np.zeros(len(title_series), dtype=int)

    pattern = "|".join(re.escape(t) for t in tokens)
    y = title_series.str.lower().str.contains(pattern, regex=True).astype(int).values
    return y


@st.cache_resource
def train_cityfit_model(texts: np.ndarray, y: np.ndarray):
    """
    Обучаем ML-модель: TF-IDF + Logistic Regression.
    Возвращаем: vectorizer, model, metrics.
    """
    # TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        min_df=2
    )
    X = vectorizer.fit_transform(texts)

    # split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
    )

    model = LogisticRegression(
        max_iter=2000,
        solver="liblinear"
    )
    model.fit(X_train, y_train)

    # metrics
    val_proba = model.predict_proba(X_val)[:, 1]
    val_pred = (val_proba >= 0.5).astype(int)

    f1 = f1_score(y_val, val_pred) if len(np.unique(y_val)) > 1 else 0.0
    auc = roc_auc_score(y_val, val_proba) if len(np.unique(y_val)) > 1 else 0.0

    metrics = {"F1": float(f1), "AUC": float(auc)}
    return vectorizer, model, metrics


def page_cityfit_ai():
    st.markdown("## 🌍 CityFit AI")
    st.caption("Интеллектуальный ML-модуль: оценивает, в каких городах выше шанс найти работу по введённой профессии.")

    df = load_cityfit_data()

    query = st.text_input("🔎 Введите профессию или ключевое слово", placeholder="Например: Data Analyst")
    query = _normalize_query(query)

    if not query:
        st.info("👉 Введите профессию, чтобы начать анализ")
        return

    # ====== готовим тексты для ML ======
    # Берем не только title, а также требования/обязанности — так ML реально работает лучше
    texts = (df["name"] + " " + df["requirements"] + " " + df["responsibilities"]).values

    # ====== weak labels (чтобы было supervised ML) ======
    y = _weak_labels_from_title(df["name"], query)
    pos = int(y.sum())
    neg = int(len(y) - pos)

    if pos < 25:
        st.warning(
            f"Слишком мало примеров для '{query}' (нашлось {pos} совпадений по названию). "
            "Попробуй более общее слово (например: Analyst / Python / Accountant)."
        )
        return

    # ====== обучаем модель под запрос ======
    vectorizer, model, metrics = train_cityfit_model(texts, y)

    # ====== скоринг всех вакансий ======
    X_all = vectorizer.transform(texts)
    proba = model.predict_proba(X_all)[:, 1]

    df_scored = df.copy()
    df_scored["match_proba"] = proba

    # ====== агрегация по городам (CityFit Score) ======
    city_stats = (
        df_scored.groupby("city", as_index=False)
        .agg(
            cityfit_score=("match_proba", "mean"),
            vacancies=("match_proba", "size"),
            strong_matches=("match_proba", lambda x: int((x >= 0.6).sum()))
        )
    )

    city_stats = city_stats.sort_values(["cityfit_score", "strong_matches", "vacancies"], ascending=False)

    # ====== вывод ======
    st.markdown("### 📊 ML-качество (на валидации)")
    c1, c2, c3 = st.columns(3)
    c1.metric("F1-score", f"{metrics['F1']:.3f}")
    c2.metric("ROC AUC", f"{metrics['AUC']:.3f}")
    c3.metric("Примеры (pos/neg)", f"{pos}/{neg}")

    st.markdown("### 🏙️ Топ городов по CityFit Score")
    topN = city_stats.head(10).copy()
    st.dataframe(topN, use_container_width=True)

    st.bar_chart(topN.set_index("city")["cityfit_score"])

    st.markdown("### 🔥 Примеры вакансий (самые вероятные совпадения)")
    examples = df_scored.sort_values("match_proba", ascending=False).head(8)[
        ["name", "city", "match_proba"]
    ]
    st.dataframe(examples, use_container_width=True)
