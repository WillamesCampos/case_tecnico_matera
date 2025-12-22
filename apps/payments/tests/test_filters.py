from datetime import date

import pytest
from django.urls import reverse

from apps.core.tests.base.basetest import BaseTestCase
from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.payment import PaymentFactory
from apps.core.tests.factories.user import UserFactory


@pytest.fixture
def loan_owner():
    return UserFactory()


@pytest.fixture
def other_user():
    return UserFactory()


@pytest.fixture
def loan(loan_owner):
    return LoanFactory(owner=loan_owner)


@pytest.fixture
def other_loan(other_user):
    return LoanFactory(owner=other_user)


class TestPaymentFilters(BaseTestCase):
    def test_filter_by_loan(self, client, loan_owner, loan):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        payment1 = PaymentFactory(loan=loan)
        other_loan = LoanFactory(owner=loan_owner)
        PaymentFactory(loan=other_loan)

        # Act
        response = client.get(url, {"loan": str(loan.uuid)})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(payment1.uuid)

    def test_filter_by_payment_date(self, client, loan_owner):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        loan = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 1))
        payment1 = PaymentFactory(loan=loan, payment_date=date(2024, 2, 15))
        PaymentFactory(loan=loan, payment_date=date(2024, 3, 20))
        PaymentFactory(loan=loan, payment_date=date(2024, 4, 10))

        # Act
        response = client.get(url, {"payment_date": "2024-02-15"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(payment1.uuid)

    def test_filter_by_payment_date_gte(self, client, loan_owner):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        loan = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 1))
        payment1 = PaymentFactory(loan=loan, payment_date=date(2024, 3, 15))
        payment2 = PaymentFactory(loan=loan, payment_date=date(2024, 4, 20))
        PaymentFactory(loan=loan, payment_date=date(2024, 2, 10))

        # Act
        response = client.get(url, {"payment_date__gte": "2024-03-01"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(payment1.uuid) in uuids
        assert str(payment2.uuid) in uuids

    def test_filter_by_payment_date_lte(self, client, loan_owner):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        loan = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 1))
        payment1 = PaymentFactory(loan=loan, payment_date=date(2024, 2, 15))
        payment2 = PaymentFactory(loan=loan, payment_date=date(2024, 3, 20))
        PaymentFactory(loan=loan, payment_date=date(2024, 4, 10))

        # Act
        response = client.get(url, {"payment_date__lte": "2024-03-31"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(payment1.uuid) in uuids
        assert str(payment2.uuid) in uuids

    def test_filter_by_payment_date_year(self, client, loan_owner):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        loan = LoanFactory(owner=loan_owner, request_date=date(2023, 12, 1))
        payment1 = PaymentFactory(loan=loan, payment_date=date(2024, 1, 15))
        payment2 = PaymentFactory(loan=loan, payment_date=date(2024, 6, 20))
        PaymentFactory(loan=loan, payment_date=date(2023, 12, 10))

        # Act
        response = client.get(url, {"payment_date__year": 2024})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(payment1.uuid) in uuids
        assert str(payment2.uuid) in uuids

    def test_filter_by_payment_date_month(self, client, loan_owner):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        loan = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 1))
        payment1 = PaymentFactory(loan=loan, payment_date=date(2024, 2, 15))
        PaymentFactory(loan=loan, payment_date=date(2024, 3, 20))
        PaymentFactory(loan=loan, payment_date=date(2024, 1, 10))

        # Act
        response = client.get(url, {"payment_date__month": 2})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(payment1.uuid)

    def test_filter_by_payment_value(self, client, loan_owner, loan):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        payment1 = PaymentFactory(loan=loan, payment_value=1000)
        PaymentFactory(loan=loan, payment_value=2000)
        PaymentFactory(loan=loan, payment_value=3000)

        # Act
        response = client.get(url, {"payment_value": 1000})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(payment1.uuid)

    def test_filter_by_payment_value_gte(self, client, loan_owner, loan):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        payment1 = PaymentFactory(loan=loan, payment_value=2000)
        payment2 = PaymentFactory(loan=loan, payment_value=3000)
        PaymentFactory(loan=loan, payment_value=1000)

        # Act
        response = client.get(url, {"payment_value__gte": 2000})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(payment1.uuid) in uuids
        assert str(payment2.uuid) in uuids

    def test_filter_by_payment_value_lte(self, client, loan_owner, loan):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        payment1 = PaymentFactory(loan=loan, payment_value=1000)
        payment2 = PaymentFactory(loan=loan, payment_value=2000)
        PaymentFactory(loan=loan, payment_value=3000)

        # Act
        response = client.get(url, {"payment_value__lte": 2000})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(payment1.uuid) in uuids
        assert str(payment2.uuid) in uuids

    def test_filter_by_search(self, client, loan_owner, loan):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        payment1 = PaymentFactory(loan=loan)
        PaymentFactory(loan=loan)

        # Act
        response = client.get(url, {"search": str(payment1.uuid)[:8]})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(payment1.uuid)

    def test_filter_by_search_loan_uuid(self, client, loan_owner, loan):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        payment1 = PaymentFactory(loan=loan)
        other_loan = LoanFactory(owner=loan_owner)
        PaymentFactory(loan=other_loan)

        # Act
        response = client.get(url, {"search": str(loan.uuid)[:8]})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(payment1.uuid)

    def test_filter_combines_multiple_filters(self, client, loan_owner):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        loan = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 1))
        payment1 = PaymentFactory(
            loan=loan,
            payment_value=2000,
            payment_date=date(2024, 2, 15),
        )
        payment2 = PaymentFactory(
            loan=loan,
            payment_value=2000,
            payment_date=date(2024, 3, 20),
        )
        PaymentFactory(
            loan=loan,
            payment_value=1000,
            payment_date=date(2024, 2, 15),
        )

        # Act
        response = client.get(
            url,
            {
                "loan": str(loan.uuid),
                "payment_value__gte": 2000,
                "payment_date__year": 2024,
            },
        )

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(payment1.uuid) in uuids
        assert str(payment2.uuid) in uuids

    def test_filter_only_shows_user_payments(
        self, client, loan_owner, loan, other_loan
    ):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        payment1 = PaymentFactory(loan=loan, payment_value=1000)
        PaymentFactory(loan=other_loan, payment_value=1000)

        # Act
        response = client.get(url, {"payment_value": 1000})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(payment1.uuid)

    def test_ordering_by_payment_date_asc(self, client, loan_owner):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        loan = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 1))
        payment1 = PaymentFactory(loan=loan, payment_date=date(2024, 1, 15))
        payment2 = PaymentFactory(loan=loan, payment_date=date(2024, 2, 20))
        payment3 = PaymentFactory(loan=loan, payment_date=date(2024, 3, 10))

        # Act
        response = client.get(url, {"ordering": "payment_date"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) >= 3
        # Filtrar apenas os pagamentos criados neste teste
        created_uuids = {
            str(payment1.uuid),
            str(payment2.uuid),
            str(payment3.uuid),
        }
        filtered_results = [
            item
            for item in response.data["results"]
            if item["uuid"] in created_uuids
        ]
        assert len(filtered_results) == 3
        payment_dates = [item["payment_date"] for item in filtered_results]
        assert payment_dates == ["2024-01-15", "2024-02-20", "2024-03-10"]

    def test_ordering_by_payment_date_desc(self, client, loan_owner):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        loan = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 1))
        payment1 = PaymentFactory(loan=loan, payment_date=date(2024, 1, 15))
        payment2 = PaymentFactory(loan=loan, payment_date=date(2024, 2, 20))
        payment3 = PaymentFactory(loan=loan, payment_date=date(2024, 3, 10))

        # Act
        response = client.get(url, {"ordering": "-payment_date"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) >= 3
        # Filtrar apenas os pagamentos criados neste teste
        created_uuids = {
            str(payment1.uuid),
            str(payment2.uuid),
            str(payment3.uuid),
        }
        filtered_results = [
            item
            for item in response.data["results"]
            if item["uuid"] in created_uuids
        ]
        assert len(filtered_results) == 3
        payment_dates = [item["payment_date"] for item in filtered_results]
        assert payment_dates == ["2024-03-10", "2024-02-20", "2024-01-15"]

    def test_ordering_by_payment_value(self, client, loan_owner, loan):
        # Arrange
        url = reverse("payment-list")
        self.authenticate_user(client, loan_owner)

        payment1 = PaymentFactory(loan=loan, payment_value=1000)
        payment2 = PaymentFactory(loan=loan, payment_value=2000)
        payment3 = PaymentFactory(loan=loan, payment_value=3000)

        # Act
        response = client.get(url, {"ordering": "payment_value"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 3
        assert response.data["results"][0]["uuid"] == str(payment1.uuid)
        assert response.data["results"][1]["uuid"] == str(payment2.uuid)
        assert response.data["results"][2]["uuid"] == str(payment3.uuid)
