import sys
from pathlib import Path
import pandas as pd

# Project folders
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from website_checker import check_website
    from scoring import calculate_score
except ImportError:
    from website_quality_audit.website_checker import check_website
    from website_quality_audit.scoring import calculate_score

# Look for input file in local input/ folder first, then fallback to shared data/ folder
INPUT_FILE = BASE_DIR / "input" / "bengaluru_real_estate_master.xlsx"
if not INPUT_FILE.exists():
    shared_data_path = BASE_DIR.parent / "data" / "bengaluru_real_estate_master.xlsx"
    if shared_data_path.exists():
        INPUT_FILE = shared_data_path

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Full audit output file
OUTPUT_FILE = OUTPUT_DIR / "website_audit_full.xlsx"


def main():
    print("Starting Full Website Quality Audit...")

    if not INPUT_FILE.exists():
        print(f"❌ Excel input file not found at {INPUT_FILE}!")
        return

    print(f"Using input file: {INPUT_FILE}")

    # Read the main worksheet
    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="All_Companies"
    )

    if "website" not in df.columns:
        print("❌ 'website' column not found in input sheet!")
        return

    # Create result columns
    result_columns = [
        "website_status",
        "http_status",
        "response_time_seconds",
        "https_enabled",
        "page_title",
        "meta_description",
        "remarks",
        "website_score",
        "website_rating",
        "final_remarks"
    ]

    for column in result_columns:
        df[column] = None

    # Select rows containing website URLs
    valid_rows = df.index[
        df["website"].notna() &
        df["website"].astype(str).str.strip().ne("")
    ].tolist()

    # Process ALL available website URLs
    rows_to_check = valid_rows
    total_websites = len(rows_to_check)

    print(f"Total companies: {len(df)}")
    print(f"Websites available: {total_websites}")
    print("Starting full audit...")

    # Check each website
    for count, index in enumerate(rows_to_check, start=1):
        company = df.at[index, "company_name"]
        website = df.at[index, "website"]

        print(
            f"\n[{count}/{total_websites}] "
            f"Checking: {company}"
        )

        try:
            # Basic website analysis
            result = check_website(website)

            # Calculate website quality score
            score_result = calculate_score(result)
            result.update(score_result)

            # Save results in DataFrame
            for column, value in result.items():
                if column in df.columns:
                    df.at[index, column] = value

            print("Status:", result.get("website_status"))
            print("Score:", result.get("website_score"))
            print("Rating:", result.get("website_rating"))

        except Exception as error:
            print("Error checking website:", error)
            df.at[index, "website_status"] = "Error"
            df.at[index, "remarks"] = str(error)

        # Progress update
        if count % 25 == 0 or count == total_websites:
            print(f"\nProgress: {count}/{total_websites} websites completed")

    # Preserve all original worksheets
    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl"
    ) as writer:
        excel_file = pd.ExcelFile(INPUT_FILE)

        for sheet in excel_file.sheet_names:
            if sheet == "All_Companies":
                df.to_excel(
                    writer,
                    sheet_name=sheet,
                    index=False
                )
            else:
                original_sheet = pd.read_excel(
                    INPUT_FILE,
                    sheet_name=sheet
                )
                original_sheet.to_excel(
                    writer,
                    sheet_name=sheet,
                    index=False
                )

    print("\n🎉 FULL WEBSITE AUDIT COMPLETED!")
    print(f"Companies processed: {total_websites}")
    print(f"Output saved at: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
