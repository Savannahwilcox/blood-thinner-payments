# compares eliquis share across the 4 payment groups 

import pandas as pd

table = pd.read_csv("data/processed/prescribers_tx_2024.csv", dtype={"Prscrbr_NPI": str})

# main analysis: only prescribers who show up for both drugs
both = table[table["both_drugs"] == True]
print("prescribers with both drugs:", len(both))
print()

print("eliquis share by payment group (both-drug prescribers):")
print(both.groupby("pay_group")["eliquis_share"].agg(["count", "median", "mean"]))
print()

# same thing with everyone, just as a check
print("eliquis share by payment group (everyone):")
print(table.groupby("pay_group")["eliquis_share"].agg(["count", "median", "mean"]))