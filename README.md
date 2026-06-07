# Real Estate Price Prediction -  Machine Learning Pipeline

An end-to-end data science and machine learning pipeline built to predict property prices using data from Zameen.com. This repository covers the core backend engineering, data collection, rigorous preprocessing, exploratory analysis, and predictive modeling stages of the project.

---

## 🚀 Looking for the Web Application?
> **Note:** This repository contains the data engineering and model training pipeline. The interactive UI dashboard built with Streamlit can be found here:
> 👉 **[Link to Streamlit Frontend App](https://real-estate-369.streamlit.app/)**

---

## 📂 Repository Structure

The project is structured chronologically, following standard data science lifecycles:

* **`1. Data Cleaning`** – Initial parsing of scraped strings, handling structural anomalies, drop-splitting structural categories, and initial row evaluations.
* **`2. EDA`** – Exploratory Data Analysis leveraging univariate and multivariate distributions to uncover key patterns, real estate insights, and geographical trends.
* **`3. Outlier Detection`** – Dynamic filtering of skewed distributions and removing extreme price/area anomalies across different property types (houses vs. flats).
* **`4. Missing Values Imputation`** – Strategic handling of null elements customized by sub-locations and property characteristics to prevent data leakage.
* **`5. Feature Selection`** – Feature engineering, data splits, and isolation of highly correlated or redundant variables to optimize model performance.
* **`6. Model Selection`** – Training, hyperparameter tuning, and cross-validation comparisons across multiple architectures (including Tree-based regressors like XGBoost and Random Forest). Production pipelines are exported as serialized models (`.joblib`).

---

## 🛠️ Tech Stack & Tooling

* **Data Collection:** Python, Selenium, BeautifulSoup
* **Data Manipulation & Cleaning:** Pandas, NumPy
* **Analysis & Visualization:** Matplotlib, Seaborn, D-Tale
* **Machine Learning:** Scikit-Learn, XGBoost, Joblib

---

## ⚙️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Piro369/End-to-End-Real-Estate-ml.git](https://github.com/Piro369/End-to-End-Real-Estate-ml.git)
   cd End-to-End-Real-Estate-ml
