import os
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_PATH = BASE_DIR / "data" / "bengaluru_real_estate_master.xlsx"

def save_to_excel(new_records_df: pd.DataFrame, target_path: Path = EXCEL_PATH):
    if new_records_df.empty:
        print("⚠️ Warning: Empty DataFrame passed to save_to_excel. Skipping.")
        return

    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Load existing data if available
    if target_path.exists():
        try:
            existing_df = pd.read_excel(target_path, sheet_name="All_Companies")
            combined_df = pd.concat([existing_df, new_records_df], ignore_index=True)
        except Exception as e:
            print(f"⚠️ Could not read existing Excel sheet (Creating new): {e}")
            combined_df = new_records_df
    else:
        combined_df = new_records_df

    # 2. Clean and deduplicate safely
    dedup_cols = [col for col in ['company_name', 'area'] if col in combined_df.columns]
    if dedup_cols:
        combined_df = combined_df.drop_duplicates(subset=dedup_cols, keep='first')

    # Strip empty spaces from strings
    string_cols = combined_df.select_dtypes(include=['object']).columns
    combined_df[string_cols] = combined_df[string_cols].apply(lambda x: x.str.strip() if hasattr(x, 'str') else x)

    # 3. Write back to Excel with multiple sheets
    try:
        with pd.ExcelWriter(target_path, engine='openpyxl') as writer:
            # Master Sheet
            combined_df.to_excel(writer, sheet_name="All_Companies", index=False)

            # Zone-wise sheets
            if 'zone' in combined_df.columns:
                for zone_name, zone_data in combined_df.groupby('zone'):
                    # Sanitize sheet name for Excel rules (max 31 chars, no special chars)
                    clean_sheet_name = str(zone_name)[:31].replace(":", "").replace("/", "")
                    zone_data.to_excel(writer, sheet_name=clean_sheet_name, index=False)

        print(f"✅ Data successfully updated and saved in {target_path}")

    except ModuleNotFoundError:
        print("❌ Error: 'openpyxl' module not found. Run: pip install openpyxl")
    except Exception as e:
        print(f"❌ Failed to save Excel file: {e}")
