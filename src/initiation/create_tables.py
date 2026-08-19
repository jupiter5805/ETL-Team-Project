def create_tables(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_staff
        (
            staff_id INT PRIMARY KEY NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            department_name VARCHAR(100) NOT NULL,
            location VARCHAR(100) NOT NULL,
            email_address VARCHAR(255) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS dim_date
        (
            date_id DATE PRIMARY KEY NOT NULL, 
            year INT NOT NULL,
            month INT NOT NULL,
            day INT NOT NULL,
            day_of_week INT NOT NULL,
            day_name VARCHAR(50) NOT NULL,
            month_name VARCHAR(50) NOT NULL,
            quarter INT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS dim_location
        (
            location_id INT PRIMARY KEY NOT NULL,
            address_line_1 VARCHAR(100) NOT NULL,
            address_line_2 VARCHAR(100),
            district VARCHAR(50),
            city VARCHAR(100) NOT NULL,
            postal_code VARCHAR(100) NOT NULL,
            country VARCHAR(100) NOT NULL,
            phone VARCHAR(50) NOT NULL 
        );

        CREATE TABLE IF NOT EXISTS dim_counterparty
        (
            counterparty_id INT PRIMARY KEY NOT NULL,
            counterparty_legal_name VARCHAR(100) NOT NULL,
            counterparty_legal_address_line_1 VARCHAR(100) NOT NULL,
            counterparty_legal_address_line_2 VARCHAR(100),
            counterparty_legal_district VARCHAR(50),
            counterparty_legal_city VARCHAR(100) NOT NULL,
            counterparty_legal_postal_code VARCHAR(100) NOT NULL,
            counterparty_legal_country VARCHAR(100) NOT NULL,
            counterparty_legal_phone_number VARCHAR(50) NOT NULL 
        );

        CREATE TABLE IF NOT EXISTS dim_currency
        (
            currency_id INT PRIMARY KEY NOT NULL,
            currency_code VARCHAR(100) NOT NULL, 
            currency_name VARCHAR(100) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS dim_design
        (
            design_id INT PRIMARY KEY NOT NULL,
            design_name VARCHAR(100) NOT NULL,
            file_location VARCHAR(200) NOT NULL,
            file_name VARCHAR(200) NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS fact_sales_order
        (
            sales_record_id SERIAL PRIMARY KEY,
            sales_order_id INT NOT NULL,
            created_date DATE NOT NULL REFERENCES dim_date(date_id),
            created_time TIME NOT NULL,
            last_updated_date DATE NOT NULL REFERENCES dim_date(date_id),
            last_updated_time TIME NOT NULL,
            sales_staff_id INT NOT NULL REFERENCES dim_staff(staff_id), 
            counterparty_id INT NOT NULL REFERENCES dim_counterparty(counterparty_id), 
            units_sold INT NOT NULL,
            unit_price NUMERIC(10, 2) NOT NULL,
            currency_id INT NOT NULL REFERENCES dim_currency(currency_id), 
            design_id INT NOT NULL REFERENCES dim_design(design_id),
            agreed_payment_date DATE NOT NULL REFERENCES dim_date(date_id),
            agreed_delivery_date DATE NOT NULL REFERENCES dim_date(date_id),
            agreed_delivery_location_id INT NOT NULL REFERENCES dim_location(location_id)
        );      
    """)