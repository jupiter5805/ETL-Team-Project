def delete_tables(connection):
     with connection.cursor() as cursor:
        cur.execute("""
            DROP TABLE IF EXISTS fact_sales_order CASCADE;
            DROP TABLE IF EXISTS dim_staff CASCADE;
            DROP TABLE IF EXISTS dim_date CASCADE;
            DROP TABLE IF EXISTS dim_location CASCADE;
            DROP TABLE IF EXISTS dim_counterparty CASCADE;
            DROP TABLE IF EXISTS dim_currency CASCADE;
            DROP TABLE IF EXISTS dim_design CASCADE;   
        """)