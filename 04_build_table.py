# 04_build_table.py
# builds one row per texas prescriber with their eliquis and xarelto claims
# and how many payments they got from each side

import pandas as pd

partd = pd.read_csv("data/raw/partd_tx_2024.csv", dtype=str)
payments = pd.read_csv("data/raw/payments_tx_2024.csv", dtype=str)

partd["Tot_Clms"] = pd.to_numeric(partd["Tot_Clms"])

# one row per prescriber, one column per drug
claims = partd.pivot_table(
    index="Prscrbr_NPI",
    columns="Brnd_Name",
    values="Tot_Clms",
    aggfunc="sum",
    fill_value=0,
)
claims = claims.rename(columns={"Eliquis": "eliquis_claims", "Xarelto": "xarelto_claims"})

print(claims.head())
print("prescribers:", len(claims))

# count payments per prescriber

payments["amount"] = pd.to_numeric(payments["total_amount_of_payment_usdollars"])

# some payments have no npi, cannot be matched to a prescriber
print("payments with no npi:", payments["covered_recipient_npi"].isna().sum())
payments = payments[payments["covered_recipient_npi"].notna()]

# which drug the payment was for. all of them are in slot 1 
# ELIQUIS and Eliquis ... upper()
payments["drug"] = payments["name_of_drug_or_biological_or_device_or_medical_supply_1"].str.upper()
print(payments["drug"].value_counts())

# how many payments each prscrbr got for each drug 
pay_counts = payments.pivot_table(
    index="covered_recipient_npi",
    columns="drug",
    values="amount", 
    aggfunc="count",
    fill_value=0,
)
pay_counts = pay_counts.rename(columns={"ELIQUIS": "eliquis_payments", "XARELTO": "xarelto_payments"})

# total dollars each prescriber got for each drug
pay_dollars = payments.pivot_table(
    index="covered_recipient_npi",
    columns="drug",
    values="amount",
    aggfunc="sum",
    fill_value=0,
)
pay_dollars = pay_dollars.rename(columns={"ELIQUIS": "eliquis_dollars", "XARELTO": "xarelto_dollars"})

print(pay_counts.head())
print(pay_dollars.head())
print("providers with at least one payment:", len(pay_counts))

# join claims and payments 

table = claims.join(pay_counts)
table = table.join(pay_dollars)

table = table.fillna(0)

table["total_payments"] = table["eliquis_payments"] + table["xarelto_payments"]

# how many paid prescribers show up in part d 
print("paid providers found in part d:", (table["total_payments"] > 0).sum(), "out of", len(pay_counts))

# make sure every prescriber only has one specialty before adding it
types_per_npi = partd.groupby("Prscrbr_NPI")["Prscrbr_Type"].nunique()
print("specialties per prescriber:")
print(types_per_npi.value_counts())

specialty = partd.groupby("Prscrbr_NPI")["Prscrbr_Type"].first()
table = table.join(specialty)

print(table.head())
print("rows:", len(table))

# build analysis columns 

from pathlib import Path

table = table.rename(columns={"Prscrbr_Type": "specialty"})

table["total_claims"] = table["eliquis_claims"] + table["xarelto_claims"]

# what share of their claims for these 2 drugs are eliquis
# 1 = all eliquis, 0 = all xarelto, 0.5 = half n half
table["eliquis_share"] = table["eliquis_claims"] / table["total_claims"]

# true if they show up for both drugs, so neither count is a hidden zero
table["both_drugs"] = (table["eliquis_claims"] > 0) & (table["xarelto_claims"] > 0)

# sorts each prescriber into a group based on who paid them
def payment_group(row):
    if row["eliquis_payments"] > 0 and row["xarelto_payments"] > 0:
        return "both"
    elif row["eliquis_payments"] > 0:
        return "eliquis only"
    elif row["xarelto_payments"] > 0:
        return "xarelto only"
    else:
        return "none"

table["pay_group"] = table.apply(payment_group, axis=1)

# checks
print()
print("prescribers with both drugs:", table["both_drugs"].sum())
print()
print("payment groups:")
print(table["pay_group"].value_counts())
print()
print("eliquis share:")
print(table["eliquis_share"].describe())

out_dir = Path("data/processed")
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "prescribers_tx_2024.csv"
table.to_csv(out_path)
print("saved", len(table), "rows to", out_path)