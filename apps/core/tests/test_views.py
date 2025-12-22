import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_check(client):
    # Arrange
    url = reverse("health-check")
    # Act
    response = client.get(url)
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "project_name": "credit-track",
        "version": "0.6.3",
        "message": "API is running",
        "status": "ok",
    }
