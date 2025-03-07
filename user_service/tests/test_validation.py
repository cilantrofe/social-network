import pytest
from pydantic import ValidationError
from app.main import UserCreate, UserAuth, UserUpdate


def test_user_create_valid():
    data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "birth_date": "1990-01-01",
        "phone": "1234567890",
    }
    user = UserCreate(**data)
    assert user.username == "john_doe"
    assert user.email == "john@example.com"


def test_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            username="john_doe",
            email="invalid-email",
            password="Password123",
            first_name="John",
            last_name="Doe",
            birth_date="1990-01-01",
            phone="+1234567890",
        )


def test_invalid_phone():
    with pytest.raises(ValidationError):
        UserCreate(
            username="john_doe",
            email="john@example.com",
            password="Password123",
            first_name="John",
            last_name="Doe",
            birth_date="1990-01-01",
            phone="123-abc-456",
        )


def test_invalid_password():
    with pytest.raises(ValidationError):
        UserCreate(
            username="john_doe",
            email="john@example.com",
            password="word",
            first_name="John",
            last_name="Doe",
            birth_date="1990-01-01",
            phone="+1234567890",
        )


def test_invalid_birth_date():
    with pytest.raises(ValidationError):
        UserCreate(
            username="john_doe",
            email="john@example.com",
            password="Password123",
            first_name="John",
            last_name="Doe",
            birth_date="01-01-1990",
            phone="+1234567890",
        )


def test_user_auth_valid():
    data = {"username": "john_doe", "password": "password123"}
    auth = UserAuth(**data)
    assert auth.username == "john_doe"
    assert auth.password == "password123"


def test_user_auth_short_username():
    with pytest.raises(ValidationError):
        UserAuth(username="jd", password="password123")


def test_user_update_valid():
    data = {
        "first_name": "Johnny",
        "last_name": "Doe",
        "birth_date": "1990-01-01",
        "phone": "0987654321",
    }
    update = UserUpdate(**data)
    assert update.first_name == "Johnny"
    assert update.phone == "0987654321"
