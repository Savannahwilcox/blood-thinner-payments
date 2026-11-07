# checks if the eliquis vs xarelto gap still shows up inside each specialty
# or if its just that different specialties get paid by different companies

import pandas as pd

table = pd.read_csv("data/processed/prescribers_tx_2024.csv", dtype={"Prscrbr_NPI": str})
both = table[table["both_drugs"] == True]

# who is actually getting paid
paid = both[both["pay_group"] != "none"]
print("paid prescribers by specialty:")
print(paid["specialty"].value_counts().head(8))
print()

# the 4 biggest specialties among both-drug prescribers
top = list(both["specialty"].value_counts().head(4).index)
print("top 4 specialties:", top)
print()

big = both[both["specialty"].isin(top)]

medians = big.pivot_table(
    index="specialty",
    columns="pay_group",
    values="eliquis_share",
    aggfunc="median",
)
counts = big.pivot_table(
    index="specialty",
    columns="pay_group",
    values="eliquis_share",
    aggfunc="count",
)

print("median eliquis share:")
print(medians.round(3))
print()
print("prescribers in each group:")
print(counts)