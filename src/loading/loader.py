from src.loading.connect_RDS import get_connection

def load_staff(cur, staff_data):
    for staff in staff_data:
        cur.execute(
            """
            INSERT INTO dim_staff (
                staff_id,
                first_name,
                last_name,
                department_name,
                location,
                email_address
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (staff_id)
            DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                department_name = EXCLUDED.department_name,
                location = EXCLUDED.location,
                email_address = EXCLUDED.email_address;
            """,
            (
                staff["staff_id"],
                staff["first_name"],
                staff["last_name"],
                staff["department_name"],
                staff["location"],
                staff["email_address"]
            )
        )

def load_location(cur, location_data):
    for location in location_data:
        cur.execute(
            """
            INSERT INTO dim_location (
                location_id,
                address_line_1,
                address_line_2,
                district,
                city,
                postal_code,
                country,
                phone
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (location_id)
            DO UPDATE SET
                address_line_1 = EXCLUDED.address_line_1,
                address_line_2 = EXCLUDED.address_line_2,
                district = EXCLUDED.district,
                city = EXCLUDED.city,
                postal_code = EXCLUDED.postal_code,
                country = EXCLUDED.country,
                phone = EXCLUDED.phone;
            """,
            (
                location["location_id"],
                location["address_line_1"],
                location["address_line_2"],
                location["district"],
                location["city"],
                location["postal_code"],
                location["country"],
                location["phone"]
            )
        )

def load_design(cur, design_data):
    for design in design_data:
        cur.execute(
            """
            INSERT INTO dim_design (
                design_id,
                design_name,
                file_location,
                file_name
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (design_id)
            DO UPDATE SET
                design_name = EXCLUDED.design_name,
                file_location = EXCLUDED.file_location,
                file_name = EXCLUDED.file_name;
            """,
            (
                design["design_id"],
                design["design_name"],
                design["file_location"],
                design["file_name"]
            )
        )

def load_currency(cur, currency_data):
    for currency in currency_data:
        cur.execute(
            """
            INSERT INTO dim_currency (
                currency_id,
                currency_code,
                currency_name
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (currency_id)
            DO UPDATE SET
                currency_code = EXCLUDED.currency_code,
                currency_name = EXCLUDED.currency_name;
            """,
            (
                currency["currency_id"],
                currency["currency_code"],
                currency["currency_name"]
            )
        )

def load_counterparty(cur, counterparty_data):
    for counterparty in counterparty_data:
        cur.execute(
            """
            INSERT INTO dim_counterparty (
                counterparty_id,
                counterparty_legal_name,
                counterparty_legal_address_line_1,
                counterparty_legal_address_line_2,
                counterparty_legal_district,
                counterparty_legal_city,
                counterparty_legal_postal_code,
                counterparty_legal_country,
                counterparty_legal_phone_number
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (counterparty_id)
            DO UPDATE SET
                counterparty_legal_name =
                    EXCLUDED.counterparty_legal_name,
                counterparty_legal_address_line_1 =
                    EXCLUDED.counterparty_legal_address_line_1,
                counterparty_legal_address_line_2 =
                    EXCLUDED.counterparty_legal_address_line_2,
                counterparty_legal_district =
                    EXCLUDED.counterparty_legal_district,
                counterparty_legal_city =
                    EXCLUDED.counterparty_legal_city,
                counterparty_legal_postal_code =
                    EXCLUDED.counterparty_legal_postal_code,
                counterparty_legal_country =
                    EXCLUDED.counterparty_legal_country,
                counterparty_legal_phone_number =
                    EXCLUDED.counterparty_legal_phone_number;
            """,
            (
                counterparty["counterparty_id"],
                counterparty["counterparty_legal_name"],
                counterparty["counterparty_legal_address_line_1"],
                counterparty["counterparty_legal_address_line_2"],
                counterparty["counterparty_legal_district"],
                counterparty["counterparty_legal_city"],
                counterparty["counterparty_legal_postal_code"],
                counterparty["counterparty_legal_country"],
                counterparty["counterparty_legal_phone_number"]
            )
        )

def load_date(cur, date_data):
    for date_record in date_data:
        cur.execute(
            """
            INSERT INTO dim_date (
                date_id,
                year,
                month,
                day,
                day_of_week,
                day_name,
                month_name,
                quarter
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date_id) DO NOTHING;
            """,
            (
                date_record["date_id"],
                date_record["year"],
                date_record["month"],
                date_record["day"],
                date_record["day_of_week"],
                date_record["day_name"],
                date_record["month_name"],
                date_record["quarter"]
            )
        )

def load_sales_order(cur, sales_order_data):
    for sales_order in sales_order_data:
        cur.execute(
            """
            INSERT INTO fact_sales_order (
                sales_order_id,
                created_date,
                created_time,
                last_updated_date,
                last_updated_time,
                sales_staff_id,
                counterparty_id,
                units_sold,
                unit_price,
                currency_id,
                design_id,
                agreed_payment_date,
                agreed_delivery_date,
                agreed_delivery_location_id
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            );
            """,
            (
                sales_order["sales_order_id"],
                sales_order["created_date"],
                sales_order["created_time"],
                sales_order["last_updated_date"],
                sales_order["last_updated_time"],
                sales_order["sales_staff_id"],
                sales_order["counterparty_id"],
                sales_order["units_sold"],
                sales_order["unit_price"],
                sales_order["currency_id"],
                sales_order["design_id"],
                sales_order["agreed_payment_date"],
                sales_order["agreed_delivery_date"],
                sales_order["agreed_delivery_location_id"]
            )
        )

def load_all(
    staff_data,
    location_data,
    design_data,
    currency_data,
    counterparty_data,
    date_data,
    sales_order_data
):
    connection = get_connection()

    try:
        with connection.cursor() as cur:

            # Dimensions
            load_staff(cur, staff_data)
            load_location(cur, location_data)
            load_design(cur, design_data)
            load_currency(cur, currency_data)
            load_counterparty(cur, counterparty_data)
            load_date(cur, date_data)

            # Fact - INSERT ONLY
            load_sales_order(cur, sales_order_data)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()