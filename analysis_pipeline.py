import duckdb
import pandas as pd

print("Initializing DuckDB SQL pipeline...")

# Connect to DuckDB (in-memory database for this session)
con = duckdb.connect(database=":memory:")

# Load CSV files into DuckDB tables
con.execute(
    "CREATE TABLE stores AS SELECT * FROM read_csv_auto('stores.csv');"
)
con.execute("CREATE TABLE skus AS SELECT * FROM read_csv_auto('skus.csv');")
con.execute(
    "CREATE TABLE interventions AS SELECT * FROM read_csv_auto('interventions.csv');"
)
con.execute(
    "CREATE TABLE inventory_shrink AS SELECT * FROM read_csv_auto('inventory_shrink.csv');"
)

print("Tables loaded successfully: stores, skus, interventions, inventory_shrink")

# Run an analytical SQL query to evaluate the Net Impact of Locked Cases
# We calculate total shrink value and total sales units by store and whether they have locked cases.
analysis_query = """
WITH store_performance AS (
    SELECT 
        s.store_id,
        s.region,
        s.store_format,
        i.has_locked_cases,
        SUM(inv.shrink_value) AS total_shrink_value,
        SUM(inv.units_sold) AS total_units_sold
    FROM stores s
    JOIN interventions i ON s.store_id = i.store_id
    JOIN inventory_shrink inv ON s.store_id = inv.store_id
    GROUP BY s.store_id, s.region, s.store_format, i.has_locked_cases
)
SELECT 
    has_locked_cases,
    COUNT(store_id) AS store_count,
    ROUND(AVG(total_shrink_value), 2) AS avg_shrink_value_per_store,
    ROUND(AVG(total_units_sold), 2) AS avg_units_sold_per_store
FROM store_performance
GROUP BY has_locked_cases;
"""

print("\n--- Asset Protection Intervention Summary ---")
result_df = con.execute(analysis_query).fetchdf()
print(result_df)

# Save processed analytics table for our upcoming dashboard step
summary_query = """
CREATE TABLE store_summary AS
SELECT 
    s.store_id,
    s.region,
    s.store_format,
    s.weekly_foot_traffic,
    i.has_locked_cases,
    i.deployment_week,
    SUM(inv.shrink_value) AS total_shrink,
    SUM(inv.units_sold * sk.unit_price) AS total_estimated_revenue
FROM stores s
JOIN interventions i ON s.store_id = i.store_id
JOIN inventory_shrink inv ON s.store_id = inv.store_id
JOIN skus sk ON inv.sku_id = sk.sku_id
GROUP BY s.store_id, s.region, s.store_format, s.weekly_foot_traffic, i.has_locked_cases, i.deployment_week;
"""
con.execute(summary_query)

# Export summarized data to a new CSV for the dashboard
dashboard_df = con.execute("SELECT * FROM store_summary;").fetchdf()
dashboard_df.to_csv("store_summary_analytics.csv", index=False)
print(
    "\nSQL pipeline execution complete! Processed summary saved to 'store_summary_analytics.csv'."
)
