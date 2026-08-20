import json
import logging

from loading.connect_RDS import get_connection


logger = logging.getLogger()
logger.setLevel(logging.INFO)


LATEST_SALES_CTE = """
WITH latest_sales AS (
    SELECT
        f.*,
        ROW_NUMBER() OVER (
            PARTITION BY f.sales_order_id
            ORDER BY
                f.last_updated_date DESC,
                f.last_updated_time DESC,
                f.sales_record_id DESC
        ) AS row_number
    FROM fact_sales_order AS f
)
"""


CURRENT_SALES_FROM = """
FROM latest_sales AS f
JOIN dim_currency AS c
    ON f.currency_id = c.currency_id
JOIN dim_design AS d
    ON f.design_id = d.design_id
JOIN dim_counterparty AS cp
    ON f.counterparty_id = cp.counterparty_id
JOIN dim_staff AS s
    ON f.sales_staff_id = s.staff_id
JOIN dim_location AS l
    ON f.agreed_delivery_location_id = l.location_id
"""


HISTORY_FROM = """
FROM fact_sales_order AS f
JOIN dim_currency AS c
    ON f.currency_id = c.currency_id
JOIN dim_counterparty AS cp
    ON f.counterparty_id = cp.counterparty_id
"""


def rows_to_dicts(cursor):
    """Convert database rows into dictionaries."""
    columns = [
        column[0]
        for column in cursor.description
    ]

    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def fetch_rows(cursor, query, parameters=None):
    """Execute a query and return all rows as dictionaries."""
    cursor.execute(
        query,
        parameters or [],
    )

    return rows_to_dicts(cursor)


def fetch_value(cursor, query, parameters=None):
    """Execute a query and return the first value."""
    cursor.execute(
        query,
        parameters or [],
    )

    row = cursor.fetchone()

    if row is None:
        return 0

    return row[0]


def build_filters(event):
    """Build safe SQL filters from dashboard selections."""
    clauses = []
    parameters = []

    currency_code = event.get("currency_code")

    if currency_code:
        clauses.append(
            "c.currency_code = %s"
        )
        parameters.append(currency_code)

    countries = event.get("countries") or []

    if isinstance(countries, list) and countries:
        clauses.append(
            "cp.counterparty_legal_country = ANY(%s)"
        )
        parameters.append(countries)

    if not clauses:
        return "", parameters

    filter_sql = (
        " AND "
        + " AND ".join(clauses)
    )

    return filter_sql, parameters


def get_filter_options(cursor):
    """Get available dashboard filter values."""
    currencies = fetch_rows(
        cursor,
        """
        SELECT
            currency_code,
            currency_name
        FROM dim_currency
        ORDER BY currency_code;
        """,
    )

    countries = fetch_rows(
        cursor,
        """
        SELECT DISTINCT
            counterparty_legal_country AS country
        FROM dim_counterparty
        WHERE counterparty_legal_country IS NOT NULL
        ORDER BY counterparty_legal_country;
        """,
    )

    return {
        "currencies": currencies,
        "countries": [
            row["country"]
            for row in countries
        ],
    }


def get_summary(
    cursor,
    filter_sql,
    parameters,
):
    """Get headline sales metrics."""
    query = (
        LATEST_SALES_CTE
        + """
        SELECT
            COUNT(*) AS sales_orders,
            COALESCE(
                SUM(f.units_sold),
                0
            ) AS units_sold,
            COALESCE(
                SUM(
                    f.units_sold
                    * f.unit_price
                ),
                0
            ) AS sales_value
        """
        + CURRENT_SALES_FROM
        + """
        WHERE f.row_number = 1
        """
        + filter_sql
    )

    rows = fetch_rows(
        cursor,
        query,
        parameters,
    )

    if not rows:
        return {
            "sales_orders": 0,
            "units_sold": 0,
            "sales_value": 0,
        }

    return rows[0]


def get_history_count(
    cursor,
    filter_sql,
    parameters,
):
    """Count all historical fact versions."""
    query = (
        """
        SELECT COUNT(*)
        """
        + HISTORY_FROM
        + """
        WHERE 1 = 1
        """
        + filter_sql
    )

    return fetch_value(
        cursor,
        query,
        parameters,
    )


def get_daily_sales(
    cursor,
    filter_sql,
    parameters,
):
    """Get current-state sales value by date."""
    query = (
        LATEST_SALES_CTE
        + """
        SELECT
            f.created_date,
            SUM(
                f.units_sold
                * f.unit_price
            ) AS sales_value
        """
        + CURRENT_SALES_FROM
        + """
        WHERE f.row_number = 1
        """
        + filter_sql
        + """
        GROUP BY f.created_date
        ORDER BY f.created_date;
        """
    )

    return fetch_rows(
        cursor,
        query,
        parameters,
    )


def get_top_designs(
    cursor,
    filter_sql,
    parameters,
):
    """Get the ten highest-value designs."""
    query = (
        LATEST_SALES_CTE
        + """
        SELECT
            d.design_name,
            SUM(
                f.units_sold
                * f.unit_price
            ) AS sales_value
        """
        + CURRENT_SALES_FROM
        + """
        WHERE f.row_number = 1
        """
        + filter_sql
        + """
        GROUP BY d.design_name
        ORDER BY sales_value DESC
        LIMIT 10;
        """
    )

    return fetch_rows(
        cursor,
        query,
        parameters,
    )


def get_top_counterparties(
    cursor,
    filter_sql,
    parameters,
):
    """Get the ten highest-value counterparties."""
    query = (
        LATEST_SALES_CTE
        + """
        SELECT
            cp.counterparty_legal_name,
            SUM(
                f.units_sold
                * f.unit_price
            ) AS sales_value
        """
        + CURRENT_SALES_FROM
        + """
        WHERE f.row_number = 1
        """
        + filter_sql
        + """
        GROUP BY
            cp.counterparty_legal_name
        ORDER BY sales_value DESC
        LIMIT 10;
        """
    )

    return fetch_rows(
        cursor,
        query,
        parameters,
    )


def get_staff_sales(
    cursor,
    filter_sql,
    parameters,
):
    """Get sales value by staff member."""
    query = (
        LATEST_SALES_CTE
        + """
        SELECT
            CONCAT(
                s.first_name,
                ' ',
                s.last_name
            ) AS staff_name,
            SUM(
                f.units_sold
                * f.unit_price
            ) AS sales_value
        """
        + CURRENT_SALES_FROM
        + """
        WHERE f.row_number = 1
        """
        + filter_sql
        + """
        GROUP BY
            s.staff_id,
            s.first_name,
            s.last_name
        ORDER BY sales_value DESC
        LIMIT 10;
        """
    )

    return fetch_rows(
        cursor,
        query,
        parameters,
    )


def get_country_orders(
    cursor,
    filter_sql,
    parameters,
):
    """Get current sales-order counts by country."""
    query = (
        LATEST_SALES_CTE
        + """
        SELECT
            cp.counterparty_legal_country
                AS country,
            COUNT(*) AS sales_orders
        """
        + CURRENT_SALES_FROM
        + """
        WHERE f.row_number = 1
        """
        + filter_sql
        + """
        GROUP BY
            cp.counterparty_legal_country
        ORDER BY sales_orders DESC;
        """
    )

    return fetch_rows(
        cursor,
        query,
        parameters,
    )


def get_recent_orders(
    cursor,
    filter_sql,
    parameters,
):
    """Get the fifty most recent current sales orders."""
    query = (
        LATEST_SALES_CTE
        + """
        SELECT
            f.sales_order_id,
            f.created_date,
            cp.counterparty_legal_name,
            d.design_name,
            CONCAT(
                s.first_name,
                ' ',
                s.last_name
            ) AS staff_name,
            f.units_sold,
            f.unit_price,
            c.currency_code,
            (
                f.units_sold
                * f.unit_price
            ) AS sales_value
        """
        + CURRENT_SALES_FROM
        + """
        WHERE f.row_number = 1
        """
        + filter_sql
        + """
        ORDER BY
            f.created_date DESC,
            f.created_time DESC
        LIMIT 50;
        """
    )

    return fetch_rows(
        cursor,
        query,
        parameters,
    )


def lambda_handler(event, context):
    """Return dashboard data queried directly from RDS."""
    logger.info(
        "Warehouse dashboard query started."
    )

    event = event or {}

    connection = None

    try:
        connection = get_connection()

        filter_sql, parameters = (
            build_filters(event)
        )

        with connection.cursor() as cursor:
            result = {
                "filters": get_filter_options(
                    cursor
                ),
                "summary": get_summary(
                    cursor,
                    filter_sql,
                    parameters,
                ),
                "fact_version_count": (
                    get_history_count(
                        cursor,
                        filter_sql,
                        parameters,
                    )
                ),
                "daily_sales": get_daily_sales(
                    cursor,
                    filter_sql,
                    parameters,
                ),
                "top_designs": get_top_designs(
                    cursor,
                    filter_sql,
                    parameters,
                ),
                "top_counterparties": (
                    get_top_counterparties(
                        cursor,
                        filter_sql,
                        parameters,
                    )
                ),
                "staff_sales": get_staff_sales(
                    cursor,
                    filter_sql,
                    parameters,
                ),
                "country_orders": (
                    get_country_orders(
                        cursor,
                        filter_sql,
                        parameters,
                    )
                ),
                "recent_orders": (
                    get_recent_orders(
                        cursor,
                        filter_sql,
                        parameters,
                    )
                ),
            }

        logger.info(
            "Warehouse dashboard query completed."
        )

        return json.loads(
            json.dumps(
                result,
                default=str,
            )
        )

    except Exception:
        logger.exception(
            "Warehouse dashboard query failed."
        )
        raise

    finally:
        if connection is not None:
            connection.close()
