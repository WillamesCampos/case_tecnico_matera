from datetime import date

import pytest
from django.urls import reverse

from apps.core.tests.base.basetest import BaseTestCase
from apps.core.tests.factories.loan import LoanFactory
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
