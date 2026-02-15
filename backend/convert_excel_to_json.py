import pandas as pd
import json
import random

input_file = r"C:\Users\Brijesh\Downloads\Engineering_Skills_with_UJR_Band_and_Function.xlsx"
output_file = "mock_db.json"

def clean_proficiency(val):
    try:
        if pd.isna(val):
            return 0
        # Extract first digit from string like "4-Expert..."
        s = str(val).strip()
        if s and s[0].isdigit():
            return int(s[0])
        return 0
    except:
        return 0

try:
    print(f"Reading {input_file}...")
    df = pd.read_excel(input_file)
    df = df.fillna('') # Replace NaN with empty string
    
    records = []
    for idx, row in df.iterrows():
        # Generate a stable-ish ID based on index
        record = {
            "id": idx + 1,
            "Group": row.get('Group', ''),
            "SBU": row.get('SBU', ''),
            "BU": row.get('BU', ''),
            "Function": row.get('Function', ''),
            "UJR_in_UJR_Master": row.get('UJR in UJR Master', ''),
            "Job_Role_Name_without_concat": row.get('Job Role Name  without  concat', ''),
            "L1_UJR": row.get('L1 UJR', ''),
            "Competency_Type": row.get('Competency Type', ''),
            "Skill_Name": row.get('Skill Name', ''),
            "Skill_Definition": row.get('Skill Definition', ''),
            "Proficiency_Level": clean_proficiency(row.get('Proficiency Level')),
            "Band": row.get('Band', '')
        }
        records.append(record)
    
    print(f"Processed {len(records)} records.")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=4)
        
    print(f"Successfully saved to {output_file}")

except Exception as e:
    print(f"Error converting data: {e}")
    import traceback
    traceback.print_exc()
