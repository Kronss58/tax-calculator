import streamlit as st
import pandas as pd

# Настройка страницы
st.set_page_config(page_title="Калькулятор 3-НДФЛ 2025", page_icon="💰")

# Стилизация через CSS для красоты
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stNumberInput label {
        font-weight: bold;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

def format_rub(value):
    """Форматирует число в русский денежный формат"""
    return f"{value:,.2f}".replace(",", " ").replace(".", ",").replace(" ", " ")

def calc_tax_amount(amount, brackets):
    """Расчет НДФЛ по прогрессивной шкале"""
    tax = 0
    prev_limit = 0
    for limit, rate in brackets:
        if amount > prev_limit:
            taxable = min(amount, limit) - prev_limit
            tax += taxable * rate
            prev_limit = limit
        else:
            break
    return tax

# Константы 2025
MAX_MAIN = 2_000_000
MAX_INT = 3_000_000
TAX_BRACKETS = [
    (2_400_000, 0.13),
    (5_000_000, 0.15),
    (20_000_000, 0.18),
    (50_000_000, 0.20),
    (float('inf'), 0.22)
]

st.title("💰 Калькулятор налогового вычета 3-НДФЛ")
st.info("Расчет актуален для налогового законодательства 2025 года.")

# Создаем колонки для ввода данных
col1, col2 = st.columns(2)

with col1:
    st.subheader("Доходы и налоги")
    income = st.number_input("Общий годовой доход (руб.)", min_value=0.0, value=0.0, step=1000.0)
    tax_paid = st.number_input("Удержанный НДФЛ за год (руб.)", min_value=0.0, value=0.0, step=100.0)

with col2:
    st.subheader("Имущественный вычет")
    purchase = st.number_input("Стоимость покупки объекта (руб.)", min_value=0.0, value=0.0, step=1000.0)
    prev_main = st.number_input("Остаток основного вычета с прошл. года", min_value=0.0, value=0.0, step=1000.0)
    interest = st.number_input("Уплаченные % по ипотеке (руб.)", min_value=0.0, value=0.0, step=1000.0)
    prev_int = st.number_input("Остаток % с прошл. года", min_value=0.0, value=0.0, step=1000.0)

if st.button("Рассчитать возврат", type="primary", use_container_width=True):
    if income == 0:
        st.error("Пожалуйста, введите сумму дохода для расчета.")
    else:
        # Логика расчета
        base_main = min(purchase, MAX_MAIN)
        base_int = min(interest, MAX_INT)
        
        rem_main_start = prev_main if prev_main > 0 else base_main
        rem_int_start = prev_int if prev_int > 0 else base_int
        rem_main_start = min(rem_main_start, base_main)
        rem_int_start = min(rem_int_start, base_int)
        
        tax_on_income = calc_tax_amount(income, TAX_BRACKETS)
        
        # Порядок применения: сначала основной, затем процентный
        used_main = min(rem_main_start, income)
        income_after_main = income - used_main
        used_int = min(rem_int_start, income_after_main)
        income_after_all = income_after_main - used_int
        
        tax_after_deduction = calc_tax_amount(income_after_all, TAX_BRACKETS)
        tax_saving = tax_on_income - tax_after_deduction
        refund_total = min(tax_saving, tax_paid)
        
        new_rem_main = rem_main_start - used_main
        new_rem_int = rem_int_start - used_int

        # --- ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ ---
        st.divider()
        st.header(f"К возврату: {format_rub(refund_total)} руб.")
        
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric("Оценочный НДФЛ", f"{format_rub(tax_on_income)} руб.")
            st.metric("Реально уплачено", f"{format_rub(tax_paid)} руб.")
        
        with res_col2:
            st.metric("Экономия за счет вычетов", f"{format_rub(tax_saving)} руб.")
            st.metric("Лимит возврата", f"{format_rub(refund_total)} руб.")

        # Таблица с деталями
        st.subheader("Детализация вычетов")
        details = {
            "Параметр": ["Основной вычет (было)", "Основной (использовано)", "Основной (остаток)", 
                        "Процентный вычет (было)", "Процентный (использовано)", "Процентный (остаток)"],
            "Сумма": [format_rub(rem_main_start), format_rub(used_main), format_rub(new_rem_main),
                      format_rub(rem_int_start), format_rub(used_int), format_rub(new_rem_int)]
        }
        st.table(pd.DataFrame(details))
        
        st.warning("⚠️ Внимание: Это предварительный расчет. Для подачи декларации используйте Личный кабинет ФНС.")

# Футер
st.markdown("---")
st.caption("Создано для упрощения расчета 3-НДФЛ. Не является официальным документом.")
