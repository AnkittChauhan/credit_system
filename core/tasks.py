import pandas as pd
from celery import shared_task
from .models import Customer, Loan
from datetime import date


@shared_task
def ingest_customers():
    df = pd.read_excel("data/customer_data.xlsx")
    for _, row in df.iterrows():
        Customer.objects.get_or_create(
            id=row["customer_id"],
            defaults={
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "phone_number": row["phone_number"],
                "monthly_salary": row["monthly_salary"],
                "approved_limit": row["approved_limit"],
                "current_debt": row["current_debt"],
                "age": 30,
            }
        )


@shared_task
def ingest_loans():
    df = pd.read_excel("data/loan_data.xlsx")
    for _, row in df.iterrows():
        Loan.objects.get_or_create(
            id=row["loan id"],
            defaults={
                "customer_id": row["customer id"],
                "loan_amount": row["loan amount"],
                "interest_rate": row["interest rate"],
                "tenure": row["tenure"],
                "monthly_installment": row["monthly repayment"],
                "emis_paid_on_time": row["EMIs paid on time"],
                "start_date": row["start date"],
                "end_date": row["end date"],
            }
        )
