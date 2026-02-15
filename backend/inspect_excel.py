import pandas as pd
import json

file_path = r"C:\Users\Brijesh\Downloads\Engineering_Skills_with_UJR_Band_and_Function.xlsx"

try:
    df = pd.read_excel(file_path)
    print("UNIQUE_BANDS:" + json.dumps(df['Band'].dropna().unique().tolist()))
    print("UNIQUE_TYPES:" + json.dumps(df['Competency Type'].dropna().unique().tolist()))
    print("UNIQUE_PROFICIENCIES:" + json.dumps(df['Proficiency Level'].dropna().unique().tolist()))
except Exception as e:
    print(f"ERROR: {e}")
