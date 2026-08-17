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
