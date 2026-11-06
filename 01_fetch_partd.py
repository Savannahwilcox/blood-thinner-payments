# downloads medicare part D prescribing for TX physicians
# only ELIQUIS and XARELTO

import csv
import time
from pathlib import Path

import requests 

# the 2024 version of part d presvsribers by providor and drug dataset 
URL = "https://data.cms.gov/data-api/v1/dataset/d5aa71a8-dcc0-4570-8bcf-bd39deac69fe/data"
PAGE_SIZE = 5000
DRUGS = ["Eliquis", "Xarelto"]

def fetch_drug(drug_name):
    all_rows = []
    offset = 0

    while True:
        params = {
            "filter[Prscrbr_State_Abrvtn]": "TX",
            "filter[Brnd_Name]": drug_name, 
            "size": PAGE_SIZE, 
            "offset": offset,
        }
        response = requests.get(URL, params=params, timeout=60)
        response.raise_for_status()

        batch = response.json()
        print("  got", len(batch), "rows starting at row", offset)

        if len(batch) == 0:
            break

        for row in batch:
            all_rows.append(row)

## a short page (<5000 rows) means that was the last one
        if len(batch) < PAGE_SIZE:
            break

        offset = offset + PAGE_SIZE
        time.sleep(1)

    return all_rows

out_dir = Path("data/raw")
out_dir.mkdir(parents=True, exist_ok=True)

all_drug_rows = []

for drug in DRUGS:
    print("fetching", drug)
    rows = fetch_drug(drug)
    print(drug, "total:", len(rows))

    for row in rows:
        all_drug_rows.append(row)

if len(all_drug_rows) == 0:
    print("no rows returned, check the URL and filters")
else:
    out_path = out_dir / "partd_tx_2024.csv"

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_drug_rows[0].keys())
        writer.writeheader()
        for row in all_drug_rows:
            writer.writerow(row)
    
    print("saved", len(all_drug_rows), "rows to", out_path)