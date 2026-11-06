# 03_explore.py
# looking at both datasets before filtering or joining anything

import pandas as pd

partd = pd.read_csv("data/raw/partd_tx_2024.csv", dtype=str)
payments = pd.read_csv("data/raw/payments_tx_2024.csv", dtype=str)

print("part d rows and columns:", partd.shape)
print("payments rows and columns:", payments.shape)
print()

print("part d columns:")
print(list(partd.columns))
print()

print("first 3 part d rows:")
print(partd.head(3))

print()
print("brand names:")
print(partd["Brnd_Name"].value_counts())
print()

print("top 10 prescriber types:")
print(partd["Prscrbr_Type"].value_counts().head(10))
print()

partd["Tot_Clms"] = pd.to_numeric(partd["Tot_Clms"])
print("claims per row:")
print(partd["Tot_Clms"].describe())
print()

drugs_per_npi = partd.groupby("Prscrbr_NPI")["Brnd_Name"].nunique()
print("how many of the 2 drugs each prescriber shows up for:")
print(drugs_per_npi.value_counts())

print()
print("companies making the payments:")
print(payments["applicable_manufacturer_or_applicable_gpo_making_payment_name"].value_counts())
print()

print("product in slot 1:")
print(payments["name_of_drug_or_biological_or_device_or_medical_supply_1"].value_counts())
print()

print("type of payment:")
print(payments["nature_of_payment_or_transfer_of_value"].value_counts())
print()

payments["amount"] = pd.to_numeric(payments["total_amount_of_payment_usdollars"])
print("payment amounts in dollars:")
print(payments["amount"].describe())
print()

print("total dollars:", payments["amount"].sum())
print("unique providers paid:", payments["covered_recipient_npi"].nunique())