from datetime import date

import pytest
from django.urls import reverse

from apps.core.tests.base.basetest import BaseTestCase
from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.payment import PaymentFactory
from apps.core.tests.factories.user import UserFactory
from apps.payments.models import Payment


@pytest.fixture
def loan_owner():
    return UserFactory()


@pytest.fixture
def loan(loan_owner):
    return LoanFactory(owner=loan_owner)


class TestPaymentViews(BaseTestCase):
    def test_create_payment_success(self, client, loan_owner, loan):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        data = {
            "loan": loan.uuid,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_value": self.faker_generator.random_int(
                min=100, max=10000
            ),
        }

        # Act
        response = client.post(url, data=data)

        # Assert
        assert response.status_code == 201
        payment = Payment.objects.get(uuid=response.data["uuid"])
        assert payment.loan == loan
        assert (
            payment.payment_date.strftime("%Y-%m-%d") == data["payment_date"]
        )
        assert float(payment.payment_value) == float(data["payment_value"])

    def test_list_payments_success(self, client, loan_owner, loan):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        PaymentFactory.create_batch(3, loan=loan)

        # Create payments for another user's loan (should not appear)
        other_user = UserFactory()
        other_loan = LoanFactory(owner=other_user)
        PaymentFactory.create_batch(2, loan=other_loan)

        # Act
        response = client.get(url)

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 3

        # Verify all returned payments belong to the authenticated user's loans
        for payment_data in response.data["results"]:
            payment = Payment.objects.get(uuid=payment_data["uuid"])
            assert payment.loan.owner == loan_owner

    def test_retrieve_payment_success(self, client, loan_owner, loan):
        # Arrange
        payment = PaymentFactory(loan=loan)
        url = reverse("payment-detail", kwargs={"pk": payment.uuid})
        self.authenticate_user(client, loan_owner)

        # Act
        response = client.get(url)

        # Assert
        assert response.status_code == 200
        assert response.data["uuid"] == str(payment.uuid)
        assert float(response.data["payment_value"]) == float(
            payment.payment_value
        )
        assert response.data["payment_date"] == str(payment.payment_date)
        assert str(response.data["loan"]) == str(payment.loan.uuid)

    def test_update_payment_success(self, client, loan_owner, loan):
        # Arrange
        payment = PaymentFactory(loan=loan)
        url = reverse("payment-detail", kwargs={"pk": payment.uuid})
        self.authenticate_user(client, loan_owner)

        update_data = {
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_value": self.faker_generator.random_int(
                min=100, max=10000
            ),
        }

        # Act
        response = client.patch(url, data=update_data)

        # Assert
        assert response.status_code == 200
        assert response.data["payment_date"] == update_data["payment_date"]
        assert float(response.data["payment_value"]) == float(
            update_data["payment_value"]
        )

        payment.refresh_from_db()
        assert (
            payment.payment_date.strftime("%Y-%m-%d")
            == update_data["payment_date"]
        )
        assert float(payment.payment_value) == float(
            update_data["payment_value"]
        )

    def test_delete_payment_success(self, client, loan_owner, loan):
        # Arrange
        payment = PaymentFactory(loan=loan)
        url = reverse("payment-detail", kwargs={"pk": payment.uuid})
        self.authenticate_user(client, loan_owner)
        payment_uuid = payment.uuid

        # Act
        response = client.delete(url)

        # Assert
        assert response.status_code == 204
        assert not Payment.objects.filter(uuid=payment_uuid).exists()
