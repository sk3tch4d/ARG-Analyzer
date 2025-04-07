from analyzer.swaps import detect_shift_swaps
import os 
import re 
import pdfplumber 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns from collections 
import defaultdict from datetime 
import datetime, timedelta from openpyxl 
import Workbook from openpyxl.styles 
import Alignment, Border, Side, Font, PatternFill from openpyxl.formatting.rule 
import FormulaRule

=== Constants ===

VALID_NAMES = { "Adeniyi, Oluwaseyi", "Bhardwaj, Liam", "Donovan, Patrick", "Gallivan, David", "Janaway, Alexander", "Robichaud, Richard", "Santo, Jaime", "Tobin, James", "Ukwesa, Jennifer", "Vanderputten, Richard", "Woodland, Nathaniel" } PAY_PERIOD_START_DATE = datetime(2025, 1, 13)

=== Helpers ===

def get_pay_period(date_obj): return (date_obj - PAY_PERIOD_START_DATE.date()).days // 14

def extract_shift_ids(line): return [t for t in line.split() if re.match(r'(SA[1-4]|[A-Z]*\d{3,4})$', t, re.IGNORECASE)]

def classify_shift(start, end, shift_ids): if "313" in shift_ids: return "Day" s = datetime.strptime(start, "%H:%M").time() if datetime.strptime("07:00", "%H:%M").time() <= s < datetime.strptime("11:00", "%H:%M").time(): return "Day" if datetime.strptime("14:00", "%H:%M").time() <= s <= datetime.strptime("16:00", "%H:%M").time(): return "Evening" if datetime.strptime("22:00", "%H:%M").time() <= s <= datetime.strptime("23:59", "%H:%M").time(): return "Night" return "Other"

=== Parser ===

def parse_pdf(pdf_path): records = [] with pdfplumber.open(pdf_path) as pdf: for page in pdf.pages: text = page.extract_text() lines = text.splitlines() if text else [] current_date = None for line in lines: if "Inventory Services" in line: try: current_date = datetime.strptime(line.split()[-1], "%d/%b/%Y").date() except: continue continue if any(x in line for x in ["Off:", "On Call", "Relief"]): continue tokens = line.strip().split() if len(tokens) >= 5: try: start_time = tokens[-4] end_time = tokens[-3] full_name = f"{tokens[-2].rstrip(',')}, {tokens[-1]}" if full_name not in VALID_NAMES: continue shift_ids = extract_shift_ids(line) full_shift_id = " ".join(shift_ids).strip() dt_start = datetime.strptime(f"{current_date} {start_time}", "%Y-%m-%d %H:%M") dt_end = datetime.strptime(f"{current_date} {end_time}", "%Y-%m-%d %H:%M") if dt_end <= dt_start: dt_end += timedelta(days=1) hours = round((dt_end - dt_start).seconds / 3600, 1) shift_type = classify_shift(start_time, end_time, shift_ids) records.append({ "Name": full_name, "Date": current_date.strftime("%a, %b %d"), "DateObj": current_date, "Shift": full_shift_id, "Type": shift_type, "Hours": hours, "Start": start_time, "End": end_time }) except: continue return pd.DataFrame(records)

=== Writer ===

def write_argx_v2(df, output_path): # [Snipped for now — will paste in next step if needed] wb = Workbook() # ... implement writing like before ... wb.save(output_path)

=== Heatmap ===

def generate_heatmap_png(df, date_label): df["WeekStart"] = df["DateObj"].apply(lambda d: d - timedelta(days=d.weekday())) pivot = df.pivot_table(index="Name", columns="WeekStart", values="Hours", aggfunc="sum", fill_value=0) pivot = pivot.round(0).astype(int) plt.figure(figsize=(10, 6)) sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues") path = f"/tmp/ARGM_{date_label}.png" plt.title("Weekly Hours per Person") plt.tight_layout() plt.savefig(path) plt.close() return path

=== Main Generator ===

def generate_argx_and_heatmap(pdf_paths): frames = [parse_pdf(p) for p in pdf_paths] df = pd.concat(frames, ignore_index=True) if df.empty: return [], {}

df = df.drop_duplicates(subset=["Name", "DateObj", "Shift"], keep="last")
df["WeekStart"] = df["DateObj"].apply(lambda d: d - timedelta(days=d.weekday()))
first_date = df["DateObj"].min().strftime("%Y-%m-%d")

output_xlsx = os.path.join("/tmp", f"ARGX_{first_date}.xlsx")
heatmap_path = generate_heatmap_png(df, first_date)
write_argx_v2(df, output_xlsx)

swaps = detect_shift_swaps(df.to_dict(orient="records"))
return [output_xlsx, heatmap_path], {
    "total": len(df),
    "swaps": swaps
}

Future: detect_shift_swaps(df) to be implemented

