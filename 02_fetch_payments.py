# downloads 2024 open payments general payments to texas providers
# where eliquis or xarelto is listed in any of the 5 product slots

import csv
import time
from pathlib import Path

import requests

URL = "https://openpaymentsdata.cms.gov/api/1/datastore/query/e6b17c6a-2534-4207-a4a1-6746a14911ff/0"
PAGE_SIZE = 500  # CMS api will not send more than 500 rows at once
DRUGS = ["Eliquis", "Xarelto"]
SLOTS = [1, 2, 3, 4, 5]  # each payment can list up to 5 products

def fetch_payments(drug_name, slot):
    column = "name_of_drug_or_biological_or_device_or_medical_supply_" + str(slot)
    all_rows = []
    offset = 0

    while True:
        body = {
            "conditions": [
                {"property": "recipient_state", "value": "TX", "operator": "="},
                {"property": column, "value": drug_name, "operator": "="},
            ],
            "limit": PAGE_SIZE,
            "offset": offset,
            "schema": False,
        }
        response = requests.post(URL, json=body, timeout=120)
        response.raise_for_status()

        batch = response.json()["results"]
        print("  slot", slot, "got", len(batch), "rows starting at row", offset)

        if len(batch) == 0:
            break

        for row in batch:
            all_rows.append(row)

        # a short page means that was the last one
        if len(batch) < PAGE_SIZE:
            break

        offset = offset + PAGE_SIZE
        time.sleep(1)

    return all_rows

out_dir = Path("data/raw")
out_dir.mkdir(parents=True, exist_ok=True)

all_payment_rows = []
seen_ids = set()

for drug in DRUGS:
    for slot in SLOTS:
        print("fetching", drug, "in slot", slot)
        rows = fetch_payments(drug, slot)

        for row in rows:
            if row["record_id"] not in seen_ids:
                seen_ids.add(row["record_id"])
                all_payment_rows.append(row)

print("unique payments:", len(all_payment_rows))

if len(all_payment_rows) == 0:
    print("no payments came back, check the url and filters")
else:
    out_path = out_dir / "payments_tx_2024.csv"

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_payment_rows[0].keys())
        writer.writeheader()
        for row in all_payment_rows:
            writer.writerow(row)

    print("saved", len(all_payment_rows), "rows to", out_path)