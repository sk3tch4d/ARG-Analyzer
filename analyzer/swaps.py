import re from collections import defaultdict

def detect_shift_swaps(records): """ Given parsed shift records, identify shift swaps based on: - One person listed as Off with a reason like Sick or Schedule Adjustm - Another person On at the same time covering a vacancy """ swaps = [] off_shifts = defaultdict(list)

for r in records:
    if r.get("status", "").lower() == "off" and "covering" not in r.get("note", "").lower():
        key = (r["unit"], r["date"], r["start"], r["end"])
        off_shifts[key].append(r)

for r in records:
    if r.get("status", "").lower() == "on" and "covering" in r.get("note", "").lower():
        key = (r["unit"], r["date"], r["start"], r["end"])
        off_group = off_shifts.get(key, [])
        if off_group:
            off_person = off_group.pop(0)
            swaps.append({
                "date": r["date"],
                "unit": r["unit"],
                "off": off_person["name"],
                "on": r["name"],
                "time": f"{r['start']} - {r['end']}",
                "reason": off_person.get("note", "")
            })

return swaps

