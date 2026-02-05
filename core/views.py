from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .services import calculate_credit_score, compound_emi
from datetime import date, timedelta


@api_view(["GET"])
def home(request):
    return Response({
        "service": "credit-approval",
        "status": "ok",
        "endpoints": [
            "/api/register",
            "/api/check-eligibility",
            "/api/create-loan",
            "/api/view-loan/<loan_id>",
            "/api/view-loans/<customer_id>",
        ],
    })


@api_view(["POST"])
def register(request):
    salary = request.data["monthly_income"]
    approved_limit = round((36 * salary) / 100000) * 100000

    customer = Customer.objects.create(
        first_name=request.data["first_name"],
        last_name=request.data["last_name"],
        age=request.data["age"],
        monthly_salary=salary,
        approved_limit=approved_limit,
        phone_number=request.data["phone_number"],
    )

    return Response({
        "customer_id": customer.id,
        "name": f"{customer.first_name} {customer.last_name}",
        "age": customer.age,
        "monthly_income": customer.monthly_salary,
        "approved_limit": customer.approved_limit,
        "phone_number": customer.phone_number
    })

@api_view(["POST"])
def check_eligibility(request):
    customer = Customer.objects.get(id=request.data["customer_id"])
    loan_amount = float(request.data["loan_amount"])
    interest_rate = float(request.data["interest_rate"])
    tenure = int(request.data["tenure"])

    credit_score = calculate_credit_score(customer)

    total_emi = sum(
        l.monthly_installment for l in Loan.objects.filter(customer=customer)
    )

    if total_emi > 0.5 * customer.monthly_salary:
        return Response({
            "customer_id": customer.id,
            "approval": False,
            "interest_rate": interest_rate,
            "corrected_interest_rate": interest_rate,
            "tenure": tenure,
            "monthly_installment": None
        })

    approval = False
    corrected_rate = interest_rate

    if credit_score > 50:
        approval = True
    elif 30 < credit_score <= 50:
        corrected_rate = max(interest_rate, 12)
        approval = True
    elif 10 < credit_score <= 30:
        corrected_rate = max(interest_rate, 16)
        approval = True
    else:
        approval = False

    emi = compound_emi(loan_amount, corrected_rate, tenure) if approval else None

    return Response({
        "customer_id": customer.id,
        "approval": approval,
        "interest_rate": interest_rate,
        "corrected_interest_rate": corrected_rate,
        "tenure": tenure,
        "monthly_installment": round(emi, 2) if emi else None
    })

@api_view(["POST"])
def create_loan(request):
    customer = Customer.objects.get(id=request.data["customer_id"])
    loan_amount = float(request.data["loan_amount"])
    interest_rate = float(request.data["interest_rate"])
    tenure = int(request.data["tenure"])

    credit_score = calculate_credit_score(customer)

    if credit_score < 10:
        return Response({
            "loan_id": None,
            "customer_id": customer.id,
            "loan_approved": False,
            "message": "Credit score too low",
            "monthly_installment": None
        })

    corrected_rate = interest_rate
    if 30 < credit_score <= 50:
        corrected_rate = max(interest_rate, 12)
    elif 10 < credit_score <= 30:
        corrected_rate = max(interest_rate, 16)

    emi = compound_emi(loan_amount, corrected_rate, tenure)

    loan = Loan.objects.create(
        customer=customer,
        loan_amount=loan_amount,
        interest_rate=corrected_rate,
        tenure=tenure,
        monthly_installment=emi,
        emis_paid_on_time=0,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30 * tenure)
    )

    customer.current_debt += loan_amount
    customer.save()

    return Response({
        "loan_id": loan.id,
        "customer_id": customer.id,
        "loan_approved": True,
        "message": "Loan approved",
        "monthly_installment": round(emi, 2)
    })


@api_view(["GET"])
def view_loan(request, loan_id):
    loan = Loan.objects.get(id=loan_id)

    return Response({
        "loan_id": loan.id,
        "customer": {
            "id": loan.customer.id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age,
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_installment,
        "tenure": loan.tenure,
    })


@api_view(["GET"])
def view_loans(request, customer_id):
    loans = Loan.objects.filter(customer_id=customer_id)

    response = []
    for loan in loans:
        response.append({
            "loan_id": loan.id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "repayments_left": loan.tenure - loan.emis_paid_on_time,
        })

    return Response(response)

@api_view(["GET"])
def view_loan(request, loan_id):
    loan = Loan.objects.get(id=loan_id)

    return Response({
        "loan_id": loan.id,
        "customer": {
            "id": loan.customer.id,
            "first_name": loan.customer.first_name,
            "last_name": loan.customer.last_name,
            "phone_number": loan.customer.phone_number,
            "age": loan.customer.age
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_installment,
        "tenure": loan.tenure
    })

@api_view(["GET"])
def view_loans(request, customer_id):
    loans = Loan.objects.filter(customer_id=customer_id)

    response = []
    for loan in loans:
        response.append({
            "loan_id": loan.id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "repayments_left": loan.tenure - loan.emis_paid_on_time
        })

    return Response(response)



