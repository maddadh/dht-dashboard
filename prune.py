import csv
from datetime import datetime, timedelta, timezone

CUTOFF = datetime.now(timezone.utc) - timedelta(days=30)

with open("data.csv", newline="") as f:
    rows = list(csv.reader(f))

header = rows[0]
kept   = [r for r in rows[1:] if r and datetime.fromisoformat(r[0].replace("Z", "+00:00")) >= CUTOFF]

with open("data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(kept)

print(f"✅ Pruned to {len(kept)} rows")
