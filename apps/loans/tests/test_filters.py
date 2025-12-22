from datetime import date

import pytest
from django.urls import reverse

from apps.core.tests.base.basetest import BaseTestCase
from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.user import UserFactory


@pytest.fixture
def loan_owner():
    return UserFactory()


@pytest.fixture
def other_user():
    return UserFactory()


class TestLoanFilters(BaseTestCase):
    def test_filter_by_request_date(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 15))
        LoanFactory(owner=loan_owner, request_date=date(2024, 2, 20))
        LoanFactory(owner=loan_owner, request_date=date(2024, 3, 10))

        # Act
        response = client.get(url, {"request_date": "2024-01-15"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)

    def test_filter_by_request_date_gte(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, request_date=date(2024, 2, 15))
        loan2 = LoanFactory(owner=loan_owner, request_date=date(2024, 3, 20))
        LoanFactory(owner=loan_owner, request_date=date(2024, 1, 10))

        # Act
        response = client.get(url, {"request_date__gte": "2024-02-01"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(loan1.uuid) in uuids
        assert str(loan2.uuid) in uuids

    def test_filter_by_request_date_lte(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 15))
        loan2 = LoanFactory(owner=loan_owner, request_date=date(2024, 2, 20))
        LoanFactory(owner=loan_owner, request_date=date(2024, 3, 10))

        # Act
        response = client.get(url, {"request_date__lte": "2024-02-28"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(loan1.uuid) in uuids
        assert str(loan2.uuid) in uuids

    def test_filter_by_request_date_year(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 15))
        loan2 = LoanFactory(owner=loan_owner, request_date=date(2024, 6, 20))
        LoanFactory(owner=loan_owner, request_date=date(2023, 12, 10))

        # Act
        response = client.get(url, {"request_date__year": 2024})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(loan1.uuid) in uuids
        assert str(loan2.uuid) in uuids

    def test_filter_by_request_date_month(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, request_date=date(2024, 2, 15))
        LoanFactory(owner=loan_owner, request_date=date(2024, 3, 20))
        LoanFactory(owner=loan_owner, request_date=date(2024, 1, 10))

        # Act
        response = client.get(url, {"request_date__month": 2})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)

    def test_filter_by_amount(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, amount=5000)
        LoanFactory(owner=loan_owner, amount=10000)
        LoanFactory(owner=loan_owner, amount=15000)

        # Act
        response = client.get(url, {"amount": 5000})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)

    def test_filter_by_amount_gte(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, amount=10000)
        loan2 = LoanFactory(owner=loan_owner, amount=15000)
        LoanFactory(owner=loan_owner, amount=5000)

        # Act
        response = client.get(url, {"amount__gte": 10000})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(loan1.uuid) in uuids
        assert str(loan2.uuid) in uuids

    def test_filter_by_amount_lte(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, amount=5000)
        loan2 = LoanFactory(owner=loan_owner, amount=10000)
        LoanFactory(owner=loan_owner, amount=15000)

        # Act
        response = client.get(url, {"amount__lte": 10000})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(loan1.uuid) in uuids
        assert str(loan2.uuid) in uuids

    def test_filter_by_interest_rate(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, interest_rate=2.5)
        LoanFactory(owner=loan_owner, interest_rate=5.0)
        LoanFactory(owner=loan_owner, interest_rate=7.5)

        # Act
        response = client.get(url, {"interest_rate": 2.5})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)

    def test_filter_by_interest_rate_gte(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, interest_rate=5.0)
        loan2 = LoanFactory(owner=loan_owner, interest_rate=7.5)
        LoanFactory(owner=loan_owner, interest_rate=2.5)

        # Act
        response = client.get(url, {"interest_rate__gte": 5.0})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(loan1.uuid) in uuids
        assert str(loan2.uuid) in uuids

    def test_filter_by_interest_rate_lte(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, interest_rate=2.5)
        loan2 = LoanFactory(owner=loan_owner, interest_rate=5.0)
        LoanFactory(owner=loan_owner, interest_rate=7.5)

        # Act
        response = client.get(url, {"interest_rate__lte": 5.0})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        uuids = [item["uuid"] for item in response.data["results"]]
        assert str(loan1.uuid) in uuids
        assert str(loan2.uuid) in uuids

    def test_filter_by_bank(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, bank="Banco do Brasil")
        LoanFactory(owner=loan_owner, bank="Itaú")
        LoanFactory(owner=loan_owner, bank="Bradesco")

        # Act
        response = client.get(url, {"bank": "Brasil"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)

    def test_filter_by_search(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, bank="Banco Teste")
        LoanFactory(owner=loan_owner, bank="Outro Banco")

        # Act
        response = client.get(url, {"search": "Teste"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)

    def test_filter_by_search_uuid(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner)
        LoanFactory(owner=loan_owner)

        # Act
        response = client.get(url, {"search": str(loan1.uuid)[:8]})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)

    def test_filter_combines_multiple_filters(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(
            owner=loan_owner,
            amount=10000,
            interest_rate=5.0,
            request_date=date(2024, 2, 15),
        )
        LoanFactory(
            owner=loan_owner,
            amount=10000,
            interest_rate=3.0,
            request_date=date(2024, 2, 15),
        )
        LoanFactory(
            owner=loan_owner,
            amount=5000,
            interest_rate=5.0,
            request_date=date(2024, 2, 15),
        )

        # Act
        response = client.get(
            url,
            {
                "amount__gte": 10000,
                "interest_rate": 5.0,
                "request_date__year": 2024,
            },
        )

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)

    def test_filter_only_shows_user_loans(
        self, client, loan_owner, other_user
    ):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, amount=5000)
        LoanFactory(owner=other_user, amount=5000)

        # Act
        response = client.get(url, {"amount": 5000})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)

    def test_ordering_by_request_date_asc(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 15))
        loan2 = LoanFactory(owner=loan_owner, request_date=date(2024, 2, 20))
        loan3 = LoanFactory(owner=loan_owner, request_date=date(2024, 3, 10))

        # Act
        response = client.get(url, {"ordering": "request_date"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 3
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)
        assert response.data["results"][1]["uuid"] == str(loan2.uuid)
        assert response.data["results"][2]["uuid"] == str(loan3.uuid)

    def test_ordering_by_request_date_desc(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, request_date=date(2024, 1, 15))
        loan2 = LoanFactory(owner=loan_owner, request_date=date(2024, 2, 20))
        loan3 = LoanFactory(owner=loan_owner, request_date=date(2024, 3, 10))

        # Act
        response = client.get(url, {"ordering": "-request_date"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 3
        assert response.data["results"][0]["uuid"] == str(loan3.uuid)
        assert response.data["results"][1]["uuid"] == str(loan2.uuid)
        assert response.data["results"][2]["uuid"] == str(loan1.uuid)

    def test_ordering_by_amount(self, client, loan_owner):
        # Arrange
        url = reverse("loan-list")
        self.authenticate_user(client, loan_owner)

        loan1 = LoanFactory(owner=loan_owner, amount=5000)
        loan2 = LoanFactory(owner=loan_owner, amount=10000)
        loan3 = LoanFactory(owner=loan_owner, amount=15000)

        # Act
        response = client.get(url, {"ordering": "amount"})

        # Assert
        assert response.status_code == 200
        assert len(response.data["results"]) == 3
        assert response.data["results"][0]["uuid"] == str(loan1.uuid)
        assert response.data["results"][1]["uuid"] == str(loan2.uuid)
        assert response.data["results"][2]["uuid"] == str(loan3.uuid)
