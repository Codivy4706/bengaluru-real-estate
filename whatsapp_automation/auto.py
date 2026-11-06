"""
Automated WhatsApp Outreach Script for Real Estate Leads
-------------------------------------------------------

Dependencies:
    pip install openpyxl pywhatkit pyautogui pandas
"""

import os
import re
import time
import random
from pathlib import Path
import openpyxl
from openpyxl import load_workbook
import pywhatkit as pwk

# =============================================================================
# CONFIGURATION & TEMPLATES
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "Exposys Real Estate Bangalore.xlsx"
IMAGE_PATH = str(BASE_DIR / "banner.jpeg")  # Path to image attachment file

MESSAGE_TEMPLATE = """Hello,

Greetings from Exposys Data Labs! 

We came across {company_name} in {area} {zone} Zone, and we would love to help you showcase properties and attract more buyers. We're offering selected real estate businesses a FREE Real Estate Digital Starter Kit.

🎁 FREE STARTER PACKAGE
✅ Professional property website
✅ Property listing page
✅ About your business page
✅ Property gallery
✅ Contact and WhatsApp integration
✅ Mobile-friendly design
✅ 2-page website profile PDF

👑 PREMIUM SERVICES (optional, to grow even more)
- Website showcase videos (30–90 sec)
- Virtual property tours
- SEO and Google Business Profile optimization
- Advanced property search and filters
- Social media marketing
- Website maintenance and support

WEBSITE FEATURES: property listings, advanced search, agent profiles, location with Google Maps, property gallery, WhatsApp enquiry, lead capture forms and a mobile-friendly design.

Free development slots are limited and subject to eligibility.

To claim your free website for {company_name}, reply here or call:
+91 7892053145 | +91 7993207065
www.exposysdata.com
hr@exposysdata.com

Thank you,
Exposys Data Labs

If you'd rather not receive messages from us, just reply STOP.
"""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def format_phone_number(raw_number, default_country_code="+91"):
    """
    Cleans raw phone numbers into standard E.164 international format.
    Returns None for invalid, missing, or 'Not Listed' entries.
    """
    if not raw_number or str(raw_number).strip().lower() in ["not listed", "none", "nan", ""]:
        return None
    
    digits = re.sub(r"\D", "", str(raw_number))
    
    if len(digits) == 10:
        return f"{default_country_code}{digits}"
    elif len(digits) == 11 and digits.startswith("0"):
        return f"{default_country_code}{digits[1:]}"
    elif len(digits) >= 11 and str(raw_number).strip().startswith("+"):
        return f"+{digits}"
    elif len(digits) >= 11:
        return f"+{digits}"
    
    return None


def get_column_indices(sheet):
    """
    Finds column indices for existing sheet headers (case-insensitive & stripped).
    """
    col_map = {}
    for col in range(1, sheet.max_column + 1):
        val = sheet.cell(row=1, column=col).value
        if val is not None:
            col_map[str(val).strip().lower()] = col
    return col_map


# =============================================================================
# MAIN OUTREACH PIPELINE
# =============================================================================
def process_sheet_outreach(sheet_name, max_leads=2, image_path=IMAGE_PATH):
    excel_path_obj = Path(EXCEL_FILE)
    if not excel_path_obj.exists():
        print(f"❌ Error: Spreadsheet '{EXCEL_FILE}' not found.")
        return

    wb = load_workbook(str(excel_path_obj))
    
    # Case-insensitive sheet lookup
    matched_sheet_name = None
    for s in wb.sheetnames:
        if s.strip().lower() == sheet_name.strip().lower():
            matched_sheet_name = s
            break

    if not matched_sheet_name:
        print(f"❌ Sheet '{sheet_name}' not found. Available sheets: {wb.sheetnames}")
        return

    sheet = wb[matched_sheet_name]
    cols = get_column_indices(sheet)
    
    status_col = cols.get("status")
    response_col = cols.get("response")

    # Fallback to create columns if missing
    if not status_col:
        status_col = sheet.max_column + 1
        sheet.cell(1, status_col).value = "status"
        cols["status"] = status_col
    if not response_col:
        response_col = sheet.max_column + 1
        sheet.cell(1, response_col).value = "Response"
        cols["response"] = response_col

    print(f"--- Processing Sheet: [{matched_sheet_name}] ---")
    
    processed_count = 0
    total_rows = sheet.max_row
    
    for row in range(2, total_rows + 1):
        if processed_count >= max_leads:
            print(f"Target limit of {max_leads} working leads reached.")
            break

        existing_status = sheet.cell(row=row, column=status_col).value
        
        # Skip rows already processed or sent
        if existing_status and str(existing_status).strip() != "":
            continue

        # Fetch lead details
        raw_phone = sheet.cell(row=row, column=cols.get("contact_number", 3)).value
        company_name = sheet.cell(row=row, column=cols.get("company_name", 1)).value or "Valued Client"
        contact_person = sheet.cell(row=row, column=cols.get("contact_person", 10)).value or "Team"
        area = sheet.cell(row=row, column=cols.get("area", 5)).value or "Bengaluru"
        zone = sheet.cell(row=row, column=cols.get("zone", 6)).value or "Central"
        
        formatted_phone = format_phone_number(raw_phone)

        # Skip invalid or missing phone numbers
        if not formatted_phone:
            sheet.cell(row=row, column=status_col).value = "invalid number"
            sheet.cell(row=row, column=response_col).value = "no"
            continue

        # Format message template
        custom_msg = MESSAGE_TEMPLATE.format(
            contact_person=contact_person,
            company_name=company_name,
            area=area,
            zone=zone
        )

        print(f"[{processed_count + 1}/{max_leads}] Sending message to {company_name} ({formatted_phone})...")

        try:
            # Send message with image attachment
            if image_path and os.path.exists(image_path):
                pwk.sendwhats_image(
                    receiver=formatted_phone,
                    img_path=image_path,
                    caption=custom_msg,
                    wait_time=10,
                    tab_close=True,
                    close_time=3
                )
            else:
                pwk.sendwhats_msg_instantly(
                    phone_no=formatted_phone,
                    message=custom_msg,
                    wait_time=10,
                    tab_close=True,
                    close_time=3
                )

            # Update existing columns on success
            sheet.cell(row=row, column=status_col).value = "sent"
            sheet.cell(row=row, column=response_col).value = "no"
            processed_count += 1
            
        except Exception as e:
            print(f"⚠️ Error or popup encountered for {formatted_phone}: {e}")
            sheet.cell(row=row, column=status_col).value = "no whatsapp"
            sheet.cell(row=row, column=response_col).value = "no"

        # Save spreadsheet immediately after every attempt
        wb.save(str(excel_path_obj))
            
        # Incremental save every 5 leads
        if processed_count % 5 == 0:
            wb.save(str(excel_path_obj))

        # Anti-spam delay: random sleep between 1 and 3 seconds (minimum safe threshold for WhatsApp automation)
        delay = random.uniform(1, 3)
        print(f"Sleeping for {delay:.1f} seconds to protect account standing...")
        time.sleep(delay)

    wb.save(str(excel_path_obj))
    print(f"✅ Completed! {processed_count} messages sent on sheet '{matched_sheet_name}'. Excel file updated.")


if __name__ == "__main__":
    target_sheet = input("Enter target sheet name (e.g. Divyansh, Akash, Mahesh, Vinuthna): ").strip()
    process_sheet_outreach(sheet_name=target_sheet, max_leads=2, image_path=IMAGE_PATH)
