import pytest
import pandas as pd
import psycopg2
import allure
import os
import math

# Конфигурация БД (можно переопределять из среды)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_USER = os.getenv("DB_USER", "testuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "testpassword")
DB_NAME = os.getenv("DB_NAME", "creditdb")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

def load_test_data():
    # Отключаем дефолтный парсинг NaN, чтобы пустые ячейки читались как пустые строки ""
    df = pd.read_csv("test_data.csv", keep_default_na=False)
    
    cases = []
    case_ids = []
    
    for _, row in df.iterrows():
        age_val = str(row['age']).strip()
        income_val = str(row['income']).strip()
        history_val = str(row['credit_history']).strip()
        emp_val = str(row['employment']).strip()
        
        age = int(age_val) if age_val else None
        income = float(income_val) if income_val else None
        hist = history_val if history_val else None
        emp = emp_val if emp_val else None
        
        cases.append((
            age,
            income,
            hist,
            emp,
            row['expected_result']
        ))
        case_ids.append(f"Case {row['case_id']}: {row['comment']}")
        
    return cases, case_ids

# Загрузка данных один раз при старте
TEST_CASES, TEST_IDS = load_test_data()

@allure.epic("Credit Scoring Engine")
@allure.feature("SP_GET_CREDIT_DECISION")
class TestCreditDecision:
    
    @allure.story("Black Box Decision Validation")
    @pytest.mark.parametrize(
        "age, income, credit_history, employment, expected_result",
        TEST_CASES,
        ids=TEST_IDS
    )
    def test_sp_get_credit_decision(self, age, income, credit_history, employment, expected_result):
        # Опционально: перезаписываем заголовок Allure более читабельно
        
        with allure.step("Подключение к Базе Данных Black Box"):
            conn = get_db_connection()
            cursor = conn.cursor()

        try:
            with allure.step(f"Вызов: SP_GET_CREDIT_DECISION(age={age}, income={income}, history={credit_history}, emp={employment})"):
                cursor.execute(
                    "SELECT SP_GET_CREDIT_DECISION(%s, %s, %s, %s);",
                    (age, income, credit_history, employment)
                )
                actual_result = cursor.fetchone()[0]
                
            with allure.step(f"Сверка результата: ожидаем '{expected_result}', получили '{actual_result}'"):
                assert actual_result == expected_result, f"Ожидали {expected_result}, получили {actual_result}"
                
        except psycopg2.errors.RaiseException as e:
            # Ошибки, выброшенные функцией через RAISE EXCEPTION
            error_message = str(e)
            with allure.step(f"Получено исключение БД (Validation Error): {error_message.strip()}"):
                if 'VALIDATION_ERROR' in error_message:
                    actual_result = 'VALIDATION_ERROR'
                else:
                    actual_result = 'UNKNOWN_EXCEPTION'
                    
            with allure.step(f"Сверка на случай невалидных данных (ожидали {expected_result})"):
                assert actual_result == expected_result, f"Ожидали {expected_result}, но упали с {error_message}"
        finally:
            cursor.close()
            conn.close()
