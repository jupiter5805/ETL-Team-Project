import json
import os

import boto3
import pandas as pd
import streamlit as st


REGION = os.getenv(
    "AWS_REGION",
    "eu-west-2",
)

FUNCTION_NAME = os.getenv(
    "DASHBOARD_QUERY_FUNCTION",
    "warehouse-dashboard-query",
)


@st.cache_data(ttl=60)
def query_warehouse(
    currency_code=None,
    countries=None,
):
    """Query the RDS warehouse through AWS Lambda."""
    lambda_client = boto3.client(
        "lambda",
        region_name=REGION,
    )

    payload = {}

    if currency_code:
        payload["currency_code"] = currency_code

    if countries:
        payload["countries"] = countries

    response = lambda_client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode(
            "utf-8"
        ),
    )

    response_body = json.loads(
        response["Payload"].read()
    )

    if "FunctionError" in response:
        raise RuntimeError(
            response_body
        )

    return response_body


def to_dataframe(records):
    """Convert Lambda records to a DataFrame."""
    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


def prepare_numeric_column(
    dataframe,
    column_name,
):
    """Convert a DataFrame column to numeric values."""
    if (
        dataframe.empty
        or column_name not in dataframe.columns
    ):
        return dataframe

    dataframe[column_name] = pd.to_numeric(
        dataframe[column_name],
        errors="coerce",
    )

    return dataframe


def display_metrics(
    data,
    currency_code,
):
    """Display headline warehouse metrics."""
    summary = data.get(
        "summary",
        {},
    )

    sales_orders = int(
        summary.get(
            "sales_orders",
            0,
        )
        or 0
    )

    fact_versions = int(
        data.get(
            "fact_version_count",
            0,
        )
        or 0
    )

    units_sold = float(
        summary.get(
            "units_sold",
            0,
        )
        or 0
    )

    sales_value = float(
        summary.get(
            "sales_value",
            0,
        )
        or 0
    )

    column_1, column_2, column_3, column_4 = (
        st.columns(4)
    )

    column_1.metric(
        "Sales Orders",
        f"{sales_orders:,}",
    )

    column_2.metric(
        "Fact Records",
        f"{fact_versions:,}",
    )

    column_3.metric(
        "Units Sold",
        f"{units_sold:,.0f}",
    )

    column_4.metric(
        f"Sales Value ({currency_code})",
        f"{sales_value:,.2f}",
    )


def display_daily_sales(data):
    """Display warehouse sales value over time."""
    st.subheader(
        "Sales Value Over Time"
    )

    daily_sales = to_dataframe(
        data.get(
            "daily_sales",
            [],
        )
    )

    daily_sales = prepare_numeric_column(
        daily_sales,
        "sales_value",
    )

    if daily_sales.empty:
        st.info(
            "No daily sales data available."
        )
        return

    daily_sales["created_date"] = (
        pd.to_datetime(
            daily_sales["created_date"],
            errors="coerce",
        )
    )

    daily_sales = (
        daily_sales
        .dropna(
            subset=["created_date"]
        )
        .sort_values("created_date")
    )

    st.line_chart(
        daily_sales.set_index(
            "created_date"
        )["sales_value"]
    )


def display_top_designs(data):
    """Display top designs by sales value."""
    st.subheader("Top Designs")

    dataframe = to_dataframe(
        data.get(
            "top_designs",
            [],
        )
    )

    dataframe = prepare_numeric_column(
        dataframe,
        "sales_value",
    )

    if dataframe.empty:
        st.info(
            "No design data available."
        )
        return

    st.bar_chart(
        dataframe.set_index(
            "design_name"
        )["sales_value"]
    )


def display_top_counterparties(data):
    """Display top counterparties by sales value."""
    st.subheader(
        "Top Counterparties"
    )

    dataframe = to_dataframe(
        data.get(
            "top_counterparties",
            [],
        )
    )

    dataframe = prepare_numeric_column(
        dataframe,
        "sales_value",
    )

    if dataframe.empty:
        st.info(
            "No counterparty data available."
        )
        return

    st.bar_chart(
        dataframe.set_index(
            "counterparty_legal_name"
        )["sales_value"]
    )


def display_staff_sales(data):
    """Display sales value by staff member."""
    st.subheader("Sales by Staff")

    dataframe = to_dataframe(
        data.get(
            "staff_sales",
            [],
        )
    )

    dataframe = prepare_numeric_column(
        dataframe,
        "sales_value",
    )

    if dataframe.empty:
        st.info(
            "No staff sales data available."
        )
        return

    st.bar_chart(
        dataframe.set_index(
            "staff_name"
        )["sales_value"]
    )


def display_country_orders(data):
    """Display sales-order counts by country."""
    st.subheader("Orders by Country")

    dataframe = to_dataframe(
        data.get(
            "country_orders",
            [],
        )
    )

    dataframe = prepare_numeric_column(
        dataframe,
        "sales_orders",
    )

    if dataframe.empty:
        st.info(
            "No country data available."
        )
        return

    st.bar_chart(
        dataframe.set_index(
            "country"
        )["sales_orders"]
    )


def display_recent_orders(data):
    """Display recent warehouse sales orders."""
    st.subheader(
        "Recent Sales Orders"
    )

    dataframe = to_dataframe(
        data.get(
            "recent_orders",
            [],
        )
    )

    if dataframe.empty:
        st.info(
            "No recent sales orders available."
        )
        return

    dataframe = prepare_numeric_column(
        dataframe,
        "unit_price",
    )

    dataframe = prepare_numeric_column(
        dataframe,
        "sales_value",
    )

    dataframe = prepare_numeric_column(
        dataframe,
        "units_sold",
    )

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )


def get_filters():
    """Load available filters from the warehouse."""
    data = query_warehouse()

    filters = data.get(
        "filters",
        {},
    )

    currency_records = filters.get(
        "currencies",
        [],
    )

    currencies = [
        record["currency_code"]
        for record in currency_records
        if record.get("currency_code")
    ]

    countries = filters.get(
        "countries",
        [],
    )

    return currencies, countries


def display_dashboard():
    """Render the RDS-backed sales dashboard."""
    st.title(
        "ToteSys Sales Dashboard"
    )

    st.caption(
        "Live analytics queried directly from "
        "the PostgreSQL data warehouse on "
        "Amazon RDS."
    )

    st.sidebar.header("Filters")

    currencies, countries = get_filters()

    if not currencies:
        st.warning(
            "No currencies were found "
            "in the warehouse."
        )
        return

    default_currency_index = 0

    if "GBP" in currencies:
        default_currency_index = (
            currencies.index("GBP")
        )

    selected_currency = (
        st.sidebar.selectbox(
            "Currency",
            currencies,
            index=default_currency_index,
        )
    )

    selected_countries = (
        st.sidebar.multiselect(
            "Counterparty country",
            countries,
        )
    )

    if st.sidebar.button(
        "Refresh warehouse data"
    ):
        st.cache_data.clear()
        st.rerun()

    data = query_warehouse(
        selected_currency,
        selected_countries,
    )

    st.success(
        "Connected to the RDS warehouse"
    )

    display_metrics(
        data,
        selected_currency,
    )

    st.divider()

    display_daily_sales(data)

    left_column, right_column = (
        st.columns(2)
    )

    with left_column:
        display_top_designs(data)

    with right_column:
        display_top_counterparties(data)

    left_column, right_column = (
        st.columns(2)
    )

    with left_column:
        display_staff_sales(data)

    with right_column:
        display_country_orders(data)

    st.divider()

    display_recent_orders(data)

    st.caption(
        "Headline analytics use the latest "
        "version of each sales order. "
        "Fact Records represents all matching "
        "historical fact versions stored in "
        "the warehouse."
    )


def main():
    """Start the Streamlit application."""
    st.set_page_config(
        page_title=(
            "ToteSys Sales Dashboard"
        ),
        page_icon="📊",
        layout="wide",
    )

    try:
        display_dashboard()

    except Exception as error:
        st.error(
            "Unable to query the "
            "RDS warehouse."
        )

        st.exception(error)


if __name__ == "__main__":
    main()
