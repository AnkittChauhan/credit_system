'''
Author: AnkittChauhan ankittrajput.4@gmail.com
Date: 2026-02-03 14:47:31
LastEditors: AnkittChauhan ankittrajput.4@gmail.com
LastEditTime: 2026-02-03 14:47:33
FilePath: /credit_system/core/services.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from datetime import date
from .models import Loan


def calculate_credit_score(customer):
    loans = Loan.objects.filter(customer=customer)

    if sum(l.loan_amount for l in loans) > customer.approved_limit:
        return 0

    score = 0
    score += sum(l.emis_paid_on_time for l in loans) * 2
    score -= loans.count() * 5
    score -= sum(l.loan_amount for l in loans) / 100000

    current_year_loans = loans.filter(start_date__year=date.today().year).count()
    score -= current_year_loans * 5

    return max(0, min(100, int(score)))


def compound_emi(principal, rate, tenure):
    monthly_rate = rate / (12 * 100)
    return principal * monthly_rate * ((1 + monthly_rate) ** tenure) / (((1 + monthly_rate) ** tenure) - 1)
