import pytest
from pydantic import ValidationError

from app.schemas.customer import CustomerCreate, CustomerResponse


def test_customer_create_defaults():
    customer = CustomerCreate(
        name="Test Customer",
        email="test@example.com",
    )

    assert customer.name == "Test Customer"
    assert customer.email == "test@example.com"
    assert customer.phone == ""
    assert customer.segment == "standard"
    assert customer.lifetime_value == 0.0


def test_customer_create_custom_values():
    customer = CustomerCreate(
        name="Huma",
        email="huma@example.com",
        phone="9999999999",
        segment="premium",
        lifetime_value=50000.0,
    )

    assert customer.phone == "9999999999"
    assert customer.segment == "premium"
    assert customer.lifetime_value == 50000.0


def test_customer_name_cannot_be_empty():
    with pytest.raises(ValidationError):
        CustomerCreate(
            name="",
            email="test@example.com",
        )


def test_customer_lifetime_value_cannot_be_negative():
    with pytest.raises(ValidationError):
        CustomerCreate(
            name="Test Customer",
            email="test@example.com",
            lifetime_value=-100.0,
        )


def test_customer_response():
    response = CustomerResponse(
        id="customer-123",
        name="Test Customer",
        email="test@example.com",
        phone="9999999999",
        segment="standard",
        lifetime_value=1000.0,
    )

    assert response.id == "customer-123"
    assert response.name == "Test Customer"
    assert response.lifetime_value == 1000.0