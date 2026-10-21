import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

print("Generating synthetic retail asset protection datasets...")

# 1. Store Master Data (50 stores)
n_stores = 50
store_ids = [f"ST-{1000 + i}" for i in range(n_stores)]
regions = np.random.choice(["North", "South", "East", "West", "Central"], size=n_stores)
store_formats = np.random.choice(
    ["Flagship", "Standard", "Express"], size=n_stores, p=[0.2, 0.6, 0.2]
)
foot_traffic = np.random.randint(5000, 25000, size=n_stores)

stores_df = pd.DataFrame(
    {
        "store_id": store_ids,
        "region": regions,
        "store_format": store_formats,
        "weekly_foot_traffic": foot_traffic,
    }
)

# 2. Product SKU Master Data (High-risk categories like Health, Beauty, OTC)
n_skus = 30
sku_ids = [f"SKU-{500 + i}" for i in range(n_skus)]
categories = np.random.choice(
    ["OTC Medicine", "Cosmetics & Beauty", "Personal Care", "Infant Care"],
    size=n_skus,
)
base_unit_prices = np.round(np.random.uniform(8.0, 45.0, size=n_skus), 2)
is_high_risk = np.random.choice([0, 1], size=n_skus, p=[0.4, 0.6])

skus_df = pd.DataFrame(
    {
        "sku_id": sku_ids,
        "category": categories,
        "unit_price": base_unit_prices,
        "is_high_risk": is_high_risk,
    }
)

# 3. Asset Protection Deployment Logs (Which stores locked up high-risk items)
# Let's say 60% of stores implemented locked cases in Q1/Q2
intervention_stores = np.random.choice(
    store_ids, size=int(n_stores * 0.6), replace=False
)
interventions_data = []
for s_id in store_ids:
    has_locked_cases = 1 if s_id in intervention_stores else 0
    deployment_week = np.random.randint(1, 15) if has_locked_cases else 0
    interventions_data.append(
        {
            "store_id": s_id,
            "has_locked_cases": has_locked_cases,
            "deployment_week": deployment_week,
        }
    )

interventions_df = pd.DataFrame(interventions_data)

# 4. Weekly Store-SKU Inventory & Shrink Logs (Simulating 26 weeks of data)
# To keep file size manageable, we sample store-sku pairs across weeks
records = []
weeks = range(1, 27)

for s_id in store_ids:
    store_info = stores_df[stores_df["store_id"] == s_id].iloc[0]
    store_intervention = interventions_df[
        interventions_df["store_id"] == s_id
    ].iloc[0]

    for sku_id in sku_ids:
        sku_info = skus_df[skus_df["sku_id"] == sku_id].iloc[0]

        for w in weeks:
            # Baseline weekly sales units
            base_sales = np.random.poisson(lam=35)

            # Friction effect: If store has locked cases and SKU is high risk, sales drop slightly due to customer friction
            friction_penalty = 0.0
            if (
                store_intervention["has_locked_cases"] == 1
                and w >= store_intervention["deployment_week"]
                and sku_info["is_high_risk"] == 1
            ):
                friction_penalty = np.random.uniform(
                    0.15, 0.35
                )  # 15-35% sales drop from friction

            adjusted_sales = max(
                1, int(base_sales * (1 - friction_penalty))
            )

            # Shrink rate calculation (units stolen/damaged)
            base_shrink_rate = (
                0.04 if sku_info["is_high_risk"] == 1 else 0.015
            )

            # Protection effect: locked cases reduce shrink significantly
            if (
                store_intervention["has_locked_cases"] == 1
                and w >= store_intervention["deployment_week"]
                and sku_info["is_high_risk"] == 1
            ):
                base_shrink_rate *= 0.3  # 70% reduction in shrink

            shrink_units = np.random.binomial(
                n=max(10, adjusted_sales), p=min(0.5, base_shrink_rate)
            )
            shrink_value = round(shrink_units * sku_info["unit_price"], 2)

            records.append(
                {
                    "week": w,
                    "store_id": s_id,
                    "sku_id": sku_id,
                    "units_sold": adjusted_sales,
                    "shrink_units": shrink_units,
                    "shrink_value": shrink_value,
                }
            )

inventory_shrink_df = pd.DataFrame(records)

# Save datasets to CSV
stores_df.to_csv("stores.csv", index=False)
skus_df.to_csv("skus.csv", index=False)
interventions_df.to_csv("interventions.csv", index=False)
inventory_shrink_df.to_csv("inventory_shrink.csv", index=False)

print("Dataset generation complete! Files created:")
print("- stores.csv")
print("- skus.csv")
print("- interventions.csv")
print("- inventory_shrink.csv")
