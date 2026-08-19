from datetime import date, datetime, timedelta
from decimal import Decimal
import calendar


CURRENCY_NAMES = {
    "GBP": "Pound Sterling",
    "USD": "US Dollar",
    "EUR": "Euro"
}


def transform_currency(currency_data):
    transformed_data = []

    for currency in currency_data:
        transformed_currency = {
            "currency_id": currency["currency_id"],
            "currency_code": currency["currency_code"],
            "currency_name": CURRENCY_NAMES[currency["currency_code"]]
        }

        transformed_data.append(transformed_currency)

    return transformed_data


def transform_design(design_data):
    transformed_data = []

    for design in design_data:
        transformed_design = {
            "design_id": design["design_id"],
            "design_name": design["design_name"],
            "file_location": design["file_location"],
            "file_name": design["file_name"]
        }

        transformed_data.append(transformed_design)

    return transformed_data


def transform_location(address_data):
    transformed_data = []

    for address in address_data:
        transformed_location = {
            "location_id": address["address_id"],
            "address_line_1": address["address_line_1"],
            "address_line_2": address["address_line_2"],
            "district": address["district"],
            "city": address["city"],
            "postal_code": address["postal_code"],
            "country": address["country"],
            "phone": address["phone"]
        }

        transformed_data.append(transformed_location)

    return transformed_data


def transform_staff(staff_data, department_data):
    transformed_data = []

    department_lookup = {
        department["department_id"]: department
        for department in department_data
    }

    for staff in staff_data:
        department = department_lookup[staff["department_id"]]

        transformed_staff = {
            "staff_id": staff["staff_id"],
            "first_name": staff["first_name"],
            "last_name": staff["last_name"],
            "department_name": department["department_name"],
            "location": department["location"],
            "email_address": staff["email_address"]
        }

        transformed_data.append(transformed_staff)

    return transformed_data


def transform_counterparty(counterparty_data, address_data):
    transformed_data = []

    address_lookup = {
        address["address_id"]: address
        for address in address_data
    }

    for counterparty in counterparty_data:
        address = address_lookup[counterparty["legal_address_id"]]

        transformed_counterparty = {
            "counterparty_id": counterparty["counterparty_id"],
            "counterparty_legal_name":
                counterparty["counterparty_legal_name"],
            "counterparty_legal_address_line_1":
                address["address_line_1"],
            "counterparty_legal_address_line_2":
                address["address_line_2"],
            "counterparty_legal_district":
                address["district"],
            "counterparty_legal_city":
                address["city"],
            "counterparty_legal_postal_code":
                address["postal_code"],
            "counterparty_legal_country":
                address["country"],
            "counterparty_legal_phone_number":
                address["phone"]
        }

        transformed_data.append(transformed_counterparty)

    return transformed_data


def convert_to_date(value):
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return date.fromisoformat(value[:10])


def transform_date(sales_order_data):
    if not sales_order_data:
        return []

    dates = []

    for sales_order in sales_order_data:
        dates.append(convert_to_date(sales_order["created_at"]))
        dates.append(convert_to_date(sales_order["last_updated"]))
        dates.append(
            convert_to_date(sales_order["agreed_delivery_date"])
        )
        dates.append(
            convert_to_date(sales_order["agreed_payment_date"])
        )

    earliest_date = min(dates)
    latest_date = max(dates)

    transformed_data = []

    current_date = earliest_date

    while current_date <= latest_date:
        transformed_date = {
            "date_id": current_date,
            "year": current_date.year,
            "month": current_date.month,
            "day": current_date.day,
            "day_of_week": current_date.isoweekday(),
            "day_name": calendar.day_name[current_date.weekday()],
            "month_name": calendar.month_name[current_date.month],
            "quarter": ((current_date.month - 1) // 3) + 1
        }

        transformed_data.append(transformed_date)

        current_date = current_date + timedelta(days=1)

    return transformed_data


def transform_sales_order(sales_order_data):
    transformed_data = []

    for sales_order in sales_order_data:
        created_at = datetime.fromisoformat(
            sales_order["created_at"]
        )

        last_updated = datetime.fromisoformat(
            sales_order["last_updated"]
        )

        transformed_sales_order = {
            "sales_order_id":
                sales_order["sales_order_id"],

            "created_date":
                created_at.date(),

            "created_time":
                created_at.time(),

            "last_updated_date":
                last_updated.date(),

            "last_updated_time":
                last_updated.time(),

            "sales_staff_id":
                sales_order["staff_id"],

            "counterparty_id":
                sales_order["counterparty_id"],

            "units_sold":
                sales_order["units_sold"],

            "unit_price":
                Decimal(sales_order["unit_price"]),

            "currency_id":
                sales_order["currency_id"],

            "design_id":
                sales_order["design_id"],

            "agreed_payment_date":
                date.fromisoformat(
                    sales_order["agreed_payment_date"]
                ),

            "agreed_delivery_date":
                date.fromisoformat(
                    sales_order["agreed_delivery_date"]
                ),

            "agreed_delivery_location_id":
                sales_order["agreed_delivery_location_id"]
        }

        transformed_data.append(transformed_sales_order)

    return transformed_data
