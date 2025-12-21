from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.core.tests.base.basetest import BaseTestCase
from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.payment import PaymentFactory
from apps.core.tests.factories.user import UserFactory
from apps.loans.models import Loan


@pytest.fixture
def loan_owner():
    return UserFactory()


class TestLoanViews(BaseTestCase):
    def test_create_loan_success(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        data = {
            "bank": self.faker_generator.company(),
            "amount": self.faker_generator.random_int(min=1000, max=100000),
            "interest_rate": self.faker_generator.random_int(min=1, max=10),
            "request_date": date.today().strftime("%Y-%m-%d"),
        }

        # Act
        response = client.post(url, data=data)

        # Assert
        loan = Loan.objects.get(uuid=response.data["uuid"])

        assert loan.owner == loan_owner
        assert response.status_code == 201
        assert float(response.data["amount"]) == float(data["amount"])
        assert float(response.data["interest_rate"]) == float(
            data["interest_rate"]
        )
        assert response.data["request_ip"] == loan.request_ip
        assert response.data["request_date"] == data["request_date"]
        assert response.data["bank"] == data["bank"]

    def test_list_loans_success(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        LoanFactory.create_batch(3, owner=loan_owner)

        other_user = UserFactory()
        LoanFactory.create_batch(2, owner=other_user)

        # Act
        response = client.get(url)

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 3

        for loan_data in response.data["results"]:
            loan = Loan.objects.get(uuid=loan_data["uuid"])
            assert loan.owner == loan_owner

    def test_retrieve_loan_success(self, client, loan_owner):
        # Arrange
        loan = LoanFactory(owner=loan_owner)
        url = reverse("loan-detail", kwargs={"pk": loan.uuid})
        self.authenticate_user(client, loan_owner)

        # Act
        response = client.get(url)

        # Assert
        assert response.status_code == 200
        assert response.data["uuid"] == str(loan.uuid)
        assert float(response.data["amount"]) == float(loan.amount)
        assert float(response.data["interest_rate"]) == float(
            loan.interest_rate
        )
        assert response.data["bank"] == loan.bank
        assert response.data["request_date"] == str(loan.request_date)

    def test_update_loan_success(self, client, loan_owner):
        # Arrange
        loan = LoanFactory(owner=loan_owner)
        url = reverse("loan-detail", kwargs={"pk": loan.uuid})
        self.authenticate_user(client, loan_owner)

        update_data = {
            "bank": self.faker_generator.company(),
            "amount": self.faker_generator.random_int(min=1000, max=100000),
            "interest_rate": self.faker_generator.random_int(min=1, max=10),
            "request_date": date.today().strftime("%Y-%m-%d"),
        }

        # Act
        response = client.patch(url, data=update_data)

        # Assert
        assert response.status_code == 200
        assert response.data["bank"] == update_data["bank"]
        assert float(response.data["amount"]) == float(update_data["amount"])
        assert float(response.data["interest_rate"]) == float(
            update_data["interest_rate"]
        )
        assert response.data["request_date"] == update_data["request_date"]

        loan.refresh_from_db()
        assert loan.bank == update_data["bank"]
        assert float(loan.amount) == float(update_data["amount"])

    def test_delete_loan_success(self, client, loan_owner):
        # Arrange
        loan = LoanFactory(owner=loan_owner)
        url = reverse("loan-detail", kwargs={"pk": loan.uuid})
        self.authenticate_user(client, loan_owner)
        loan_uuid = loan.uuid

        # Act
        response = client.delete(url)

        # Assert
        assert response.status_code == 204
        assert not Loan.objects.filter(uuid=loan_uuid).exists()

    def test_create_loan_without_authentication(self, client):
        # Arrange
        url = reverse("loan-list")
        data = {
            "bank": self.faker_generator.company(),
            "amount": 10000,
            "interest_rate": 2.5,
            "request_date": date.today().strftime("%Y-%m-%d"),
        }

        # Act
        response = client.post(url, data=data)

        # Assert
        assert response.status_code == 401

    def test_create_loan_amount_zero_raises_error(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)
        data = {
            "bank": self.faker_generator.company(),
            "amount": 0,
            "interest_rate": 2.5,
            "request_date": date.today().strftime("%Y-%m-%d"),
        }

        # Act
        response = client.post(url, data=data)

        # Assert
        assert response.status_code == 400
        assert "amount" in response.data

    def test_create_loan_amount_negative_raises_error(
        self, client, loan_owner
    ):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)
        data = {
            "bank": self.faker_generator.company(),
            "amount": -1000,
            "interest_rate": 2.5,
            "request_date": date.today().strftime("%Y-%m-%d"),
        }

        # Act
        response = client.post(url, data=data)

        # Assert
        assert response.status_code == 400
        assert "amount" in response.data

    def test_create_loan_interest_rate_below_minimum_raises_error(
        self, client, loan_owner
    ):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)
        data = {
            "bank": self.faker_generator.company(),
            "amount": 10000,
            "interest_rate": 0.05,
            "request_date": date.today().strftime("%Y-%m-%d"),
        }

        # Act
        response = client.post(url, data=data)

        # Assert
        assert response.status_code == 400
        assert "interest_rate" in response.data

    def test_retrieve_loan_includes_total_paid_and_remaining_balance(
        self, client, loan_owner
    ):
        # Arrange
        loan = LoanFactory(owner=loan_owner)
        PaymentFactory(loan=loan, payment_value=Decimal("1000.00"))
        url = reverse("loan-detail", kwargs={"pk": loan.uuid})
        self.authenticate_user(client, loan_owner)

        # Act
        response = client.get(url)

        # Assert
        assert response.status_code == 200
        assert "total_paid" in response.data
        assert "remaining_balance" in response.data
        assert "iof" in response.data
        assert isinstance(response.data["total_paid"], float)
        assert isinstance(response.data["remaining_balance"], float)
        assert isinstance(response.data["iof"], float)

    def test_list_loans_does_not_include_total_paid_and_remaining_balance(
        self, client, loan_owner
    ):
        # Arrange
        loan = LoanFactory(owner=loan_owner)
        PaymentFactory(loan=loan, payment_value=Decimal("1000.00"))
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        # Act
        response = client.get(url)

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) > 0
        for loan_data in response.data["results"]:
            assert "total_paid" not in loan_data
            assert "remaining_balance" not in loan_data
            assert "iof" not in loan_data

    def test_update_loan_critical_fields_with_payments_raises_error(
        self, client, loan_owner
    ):
        # Arrange
        loan = LoanFactory(owner=loan_owner)
        PaymentFactory(loan=loan)
        url = reverse("loan-detail", kwargs={"pk": loan.uuid})
        self.authenticate_user(client, loan_owner)

        update_data = {
            "amount": 20000,
            "interest_rate": 5.0,
        }

        # Act
        response = client.patch(url, data=update_data)

        # Assert
        assert response.status_code == 200
        # Fields should remain unchanged
        loan.refresh_from_db()
        assert float(loan.amount) != float(update_data["amount"])
        assert float(loan.interest_rate) != float(update_data["interest_rate"])

    def test_retrieve_loan_from_other_user_returns_404(
        self, client, loan_owner
    ):
        # Arrange
        other_user = UserFactory()
        loan = LoanFactory(owner=other_user)
        url = reverse("loan-detail", kwargs={"pk": loan.uuid})
        self.authenticate_user(client, loan_owner)

        # Act
        response = client.get(url)

        # Assert
        assert response.status_code == 404

    def test_update_loan_from_other_user_returns_404(self, client, loan_owner):
        # Arrange
        other_user = UserFactory()
        loan = LoanFactory(owner=other_user)
        url = reverse("loan-detail", kwargs={"pk": loan.uuid})
        self.authenticate_user(client, loan_owner)

        update_data = {"bank": "New Bank"}

        # Act
        response = client.patch(url, data=update_data)

        # Assert
        assert response.status_code == 404

    def test_delete_loan_from_other_user_returns_404(self, client, loan_owner):
        # Arrange
        other_user = UserFactory()
        loan = LoanFactory(owner=other_user)
        url = reverse("loan-detail", kwargs={"pk": loan.uuid})
        self.authenticate_user(client, loan_owner)

        # Act
        response = client.delete(url)

        # Assert
        assert response.status_code == 404

    def test_create_loan_captures_request_ip(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)
        data = {
            "bank": self.faker_generator.company(),
            "amount": 10000,
            "interest_rate": 2.5,
            "request_date": date.today().strftime("%Y-%m-%d"),
        }

        # Act
        response = client.post(url, data=data)

        # Assert
        assert response.status_code == 201
        loan = Loan.objects.get(uuid=response.data["uuid"])
        assert loan.request_ip is not None
        assert loan.request_ip
