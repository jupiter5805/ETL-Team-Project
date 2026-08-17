import pytest

from src.transformation.transform import (
    transform_currency,
    transform_design,
    transform_location,
    transform_staff,
    transform_counterparty,
)


def test_transform_currency():
    currency_data = [
        {
            "currency_id": 1,
            "currency_code": "GBP",
            "created_at": "2022-11-03",
            "last_updated": "2022-11-03",
        }
    ]

    result = transform_currency(currency_data)

    expected = [
        {
            "currency_id": 1,
            "currency_code": "GBP",
            "currency_name": "Pound Sterling",
        }
    ]

    assert result == expected


def test_transform_currency_removes_unwanted_columns():
    currency_data = [
        {
            "currency_id": 2,
            "currency_code": "USD",
            "created_at": "2022-11-03",
            "last_updated": "2022-11-03",
        }
    ]

    result = transform_currency(currency_data)

    assert "created_at" not in result[0]
    assert "last_updated" not in result[0]


def test_transform_design():
    design_data = [
        {
            "design_id": 8,
            "created_at": "2022-11-03",
            "design_name": "Wooden",
            "file_location": "/usr",
            "file_name": "wooden-20220717-npgz.json",
            "last_updated": "2022-11-03",
        }
    ]

    result = transform_design(design_data)

    expected = [
        {
            "design_id": 8,
            "design_name": "Wooden",
            "file_location": "/usr",
            "file_name": "wooden-20220717-npgz.json",
        }
    ]

    assert result == expected


def test_transform_design_removes_unwanted_columns():
    design_data = [
        {
            "design_id": 8,
            "created_at": "2022-11-03",
            "design_name": "Wooden",
            "file_location": "/usr",
            "file_name": "wooden.json",
            "last_updated": "2022-11-03",
        }
    ]

    result = transform_design(design_data)

    assert "created_at" not in result[0]
    assert "last_updated" not in result[0]


def test_transform_location():
    address_data = [
        {
            "address_id": 1,
            "address_line_1": "6826 Herzog Via",
            "address_line_2": None,
            "district": "Avon",
            "city": "New Patienceburgh",
            "postal_code": "28441",
            "country": "Turkey",
            "phone": "1803 637401",
        }
    ]

    result = transform_location(address_data)

    expected = [
        {
            "location_id": 1,
            "address_line_1": "6826 Herzog Via",
            "address_line_2": None,
            "district": "Avon",
            "city": "New Patienceburgh",
            "postal_code": "28441",
            "country": "Turkey",
            "phone": "1803 637401",
        }
    ]

    assert result == expected


def test_transform_location_renames_address_id():
    address_data = [
        {
            "address_id": 10,
            "address_line_1": "49967 Kaylah Flat",
            "address_line_2": None,
            "district": "Bedfordshire",
            "city": "Beaulahcester",
            "postal_code": "89470",
            "country": "Korea",
            "phone": "4949 998070",
        }
    ]

    result = transform_location(address_data)

    assert result[0]["location_id"] == 10
    assert "address_id" not in result[0]


def test_transform_location_keeps_nullable_fields():
    address_data = [
        {
            "address_id": 2,
            "address_line_1": "179 Alexie Cliffs",
            "address_line_2": None,
            "district": None,
            "city": "Aliso Viejo",
            "postal_code": "99305-7380",
            "country": "San Marino",
            "phone": "9621 880720",
        }
    ]

    result = transform_location(address_data)

    assert result[0]["address_line_2"] is None
    assert result[0]["district"] is None


def test_transform_staff():
    staff_data = [
        {
            "staff_id": 1,
            "first_name": "Jeremie",
            "last_name": "Franey",
            "department_id": 2,
            "email_address": "jeremie.franey@terrifictotes.com",
        }
    ]

    department_data = [
        {
            "department_id": 2,
            "department_name": "Purchasing",
            "location": "Manchester",
        }
    ]

    result = transform_staff(staff_data, department_data)

    expected = [
        {
            "staff_id": 1,
            "first_name": "Jeremie",
            "last_name": "Franey",
            "department_name": "Purchasing",
            "location": "Manchester",
            "email_address": "jeremie.franey@terrifictotes.com",
        }
    ]

    assert result == expected


def test_transform_staff_uses_correct_department():
    staff_data = [
        {
            "staff_id": 13,
            "first_name": "Stan",
            "last_name": "Lehner",
            "department_id": 4,
            "email_address": "stan.lehner@terrifictotes.com",
        }
    ]

    department_data = [
        {
            "department_id": 3,
            "department_name": "Production",
            "location": "Leeds",
        },
        {
            "department_id": 4,
            "department_name": "Dispatch",
            "location": "Leds",
        },
    ]

    result = transform_staff(staff_data, department_data)

    assert result[0]["department_name"] == "Dispatch"
    assert result[0]["location"] == "Leds"


def test_transform_staff_removes_unwanted_columns():
    staff_data = [
        {
            "staff_id": 1,
            "first_name": "Jeremie",
            "last_name": "Franey",
            "department_id": 2,
            "email_address": "jeremie.franey@terrifictotes.com",
            "created_at": "2022-11-03",
            "last_updated": "2022-11-03",
        }
    ]

    department_data = [
        {
            "department_id": 2,
            "department_name": "Purchasing",
            "location": "Manchester",
            "manager": "Naomi Lapaglia",
        }
    ]

    result = transform_staff(staff_data, department_data)

    assert "department_id" not in result[0]
    assert "created_at" not in result[0]
    assert "last_updated" not in result[0]
    assert "manager" not in result[0]


def test_transform_counterparty():
    counterparty_data = [
        {
            "counterparty_id": 1,
            "counterparty_legal_name": "Fahey and Sons",
            "legal_address_id": 15,
            "commercial_contact": "Micheal Toy",
            "delivery_contact": "Mrs. Lucy Runolfsdottir",
        }
    ]

    address_data = [
        {
            "address_id": 15,
            "address_line_1": "605 Haskell Trafficway",
            "address_line_2": "Axel Freeway",
            "district": None,
            "city": "East Bobbie",
            "postal_code": "88253-4257",
            "country": "Heard Island and McDonald Islands",
            "phone": "9687 937447",
        }
    ]

    result = transform_counterparty(
        counterparty_data,
        address_data,
    )

    expected = [
        {
            "counterparty_id": 1,
            "counterparty_legal_name": "Fahey and Sons",
            "counterparty_legal_address_line_1":
                "605 Haskell Trafficway",
            "counterparty_legal_address_line_2":
                "Axel Freeway",
            "counterparty_legal_district": None,
            "counterparty_legal_city": "East Bobbie",
            "counterparty_legal_postal_code": "88253-4257",
            "counterparty_legal_country":
                "Heard Island and McDonald Islands",
            "counterparty_legal_phone_number": "9687 937447",
        }
    ]

    assert result == expected


def test_transform_counterparty_uses_correct_address():
    counterparty_data = [
        {
            "counterparty_id": 1,
            "counterparty_legal_name": "Fahey and Sons",
            "legal_address_id": 15,
        }
    ]

    address_data = [
        {
            "address_id": 2,
            "address_line_1": "Wrong Address",
            "address_line_2": None,
            "district": None,
            "city": "Wrong City",
            "postal_code": "00000",
            "country": "Wrong Country",
            "phone": "0000",
        },
        {
            "address_id": 15,
            "address_line_1": "605 Haskell Trafficway",
            "address_line_2": "Axel Freeway",
            "district": None,
            "city": "East Bobbie",
            "postal_code": "88253-4257",
            "country": "Heard Island and McDonald Islands",
            "phone": "9687 937447",
        },
    ]

    result = transform_counterparty(
        counterparty_data,
        address_data,
    )

    assert (
        result[0]["counterparty_legal_address_line_1"]
        == "605 Haskell Trafficway"
    )


def test_transform_counterparty_keeps_nullable_address_fields():
    counterparty_data = [
        {
            "counterparty_id": 3,
            "counterparty_legal_name": "Armstrong Inc",
            "legal_address_id": 2,
        }
    ]

    address_data = [
        {
            "address_id": 2,
            "address_line_1": "179 Alexie Cliffs",
            "address_line_2": None,
            "district": None,
            "city": "Aliso Viejo",
            "postal_code": "99305-7380",
            "country": "San Marino",
            "phone": "9621 880720",
        }
    ]

    result = transform_counterparty(
        counterparty_data,
        address_data,
    )

    assert result[0]["counterparty_legal_address_line_2"] is None
    assert result[0]["counterparty_legal_district"] is None


def test_transform_counterparty_removes_unwanted_columns():
    counterparty_data = [
        {
            "counterparty_id": 1,
            "counterparty_legal_name": "Fahey and Sons",
            "legal_address_id": 15,
            "commercial_contact": "Micheal Toy",
            "delivery_contact": "Mrs. Lucy Runolfsdottir",
            "created_at": "2022-11-03",
            "last_updated": "2022-11-03",
        }
    ]

    address_data = [
        {
            "address_id": 15,
            "address_line_1": "605 Haskell Trafficway",
            "address_line_2": "Axel Freeway",
            "district": None,
            "city": "East Bobbie",
            "postal_code": "88253-4257",
            "country": "Heard Island and McDonald Islands",
            "phone": "9687 937447",
        }
    ]

    result = transform_counterparty(
        counterparty_data,
        address_data,
    )

    assert "legal_address_id" not in result[0]
    assert "commercial_contact" not in result[0]
    assert "delivery_contact" not in result[0]
    assert "created_at" not in result[0]
    assert "last_updated" not in result[0]


@pytest.mark.parametrize(
    "transform_function",
    [
        transform_currency,
        transform_design,
        transform_location,
    ],
)
def test_single_source_transform_returns_empty_list(
    transform_function,
):
    assert transform_function([]) == []


def test_transform_staff_returns_empty_list():
    assert transform_staff([], []) == []


def test_transform_counterparty_returns_empty_list():
    assert transform_counterparty([], []) == []
