arg_analyzer/core.py

from .parser import parse_pdf from .logic import deduplicate_records, detect_shift_swaps from .excel_writer import write_argx from .visuals import generate_heatmap from datetime import datetime, timedelta import os

UPLOAD_TMP_DIR = "/tmp"

def generate_argx_and_heatmap(pdf_paths): frames = [parse_pdf(p) for p in pdf_paths]

# Apply deduplication and swap detection
df = deduplicate_records(frames, pdf_paths)
swaps = detect_shift_swaps(frames, pdf_paths)

# Early exit if empty
if df.empty:
    return [], {}

# Generate Excel and Heatmap
df["WeekStart"] = df["DateObj"].apply(lambda d: d - timedelta(days=d.weekday()))
first_date = df["DateObj"].min().strftime("%Y-%m-%d")

output_files = []
excel_path = os.path.join(UPLOAD_TMP_DIR, f"ARGX_{first_date}.xlsx")
write_argx(df, excel_path)
output_files.append(excel_path)

heatmap_path = generate_heatmap(df, first_date)
output_files.append(heatmap_path)

# Generate statistics
today = datetime.now().date()
week_start = today - timedelta(days=today.weekday())

stats = {
    "working_today": group_by_shift(df, today),
    "working_tomorrow": group_by_shift(df, today + timedelta(days=1)),
    "shift_swaps": swaps,
    "total_hours_week": round(df[df["WeekStart"] == week_start]["Hours"].sum()),
    "top_day": df.groupby("DateObj")["Hours"].sum().idxmax(),
    "top_day_hours": int(df.groupby("DateObj")["Hours"].sum().max()),
    "rankings": build_rankings(df, week_start, today)
}

return output_files, stats

def group_by_shift(df, target_date): from collections import defaultdict from datetime import datetime

shifts = defaultdict(list)
for _, row in df.iterrows():
    start_time = datetime.strptime(row["Start"], "%H:%M").time()
    start_datetime = datetime.combine(row["DateObj"], start_time)
    if start_datetime.date() == target_date:
        shifts[row["Type"]].append((row["Name"], row["Shift"]))
return dict(shifts)

def build_rankings(df, week_start, today): get_pay_period = lambda d: (d - datetime(2025, 1, 13).date()).days // 14 current_period = get_pay_period(today)

return {
    "weekly": df[df["WeekStart"] == week_start].groupby("Name")["Hours"].sum().sort_values(ascending=False).astype(int).items(),
    "period": df[df["DateObj"].apply(get_pay_period) == current_period].groupby("Name")["Hours"].sum().sort_values(ascending=False).astype(int).items(),
    "total": df.groupby("Name")["Hours"].sum().sort_values(ascending=False).astype(int).items(),
}


