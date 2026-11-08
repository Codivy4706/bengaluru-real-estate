"""
WhatsApp Number Verification Script (No Messaging)
-------------------------------------------------
Checks previously processed rows to separate valid WhatsApp accounts ('sent') 
from non-WhatsApp accounts ('no whatsapp') without sending any text or image.

Dependencies:
    pip install openpyxl pyautogui pandas
"""

import os
import re
import time
import random
import webbrowser
import openpyxl
from openpyxl import load_workbook
import pyautogui

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "Exposys Real Estate Bangalore.xlsx")

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
# MAIN VERIFICATION PIPELINE
# =============================================================================
def verify_sheet_numbers(sheet_name):
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: Spreadsheet '{EXCEL_FILE}' not found.")
        return

    wb = load_workbook(EXCEL_FILE)
    
    # Case-insensitive sheet lookup
    matched_sheet_name = None
    for s in wb.sheetnames:
        if s.strip().lower() == sheet_name.strip().lower():
            matched_sheet_name = s
            break

    if not matched_sheet_name:
        print(f"Sheet '{sheet_name}' not found. Available sheets: {wb.sheetnames}")
        return

    sheet = wb[matched_sheet_name]
    cols = get_column_indices(sheet)
    
    status_col = cols.get("status")
    response_col = cols.get("response")

    if not status_col or not response_col:
        print("Error: Could not locate 'status' or 'Response' columns.")
        return

    print(f"--- Starting WhatsApp Verification for Sheet: [{matched_sheet_name}] ---")
    
    reverified_count = 0
    total_rows = sheet.max_row
    
    for row in range(2, total_rows + 1):
        existing_status = sheet.cell(row=row, column=status_col).value
        existing_response = sheet.cell(row=row, column=response_col).value
        
        # TARGET CONDITION: Traverse ONLY visited rows (status != null OR response == 'no')
        is_visited = (existing_status and str(existing_status).strip() != "") or \
                     (existing_response and str(existing_response).strip().lower() == "no")
                     
        if not is_visited:
            continue

        raw_phone = sheet.cell(row=row, column=cols.get("contact_number", 3)).value
        company_name = sheet.cell(row=row, column=cols.get("company_name", 1)).value or "Client"
        formatted_phone = format_phone_number(raw_phone)

        if not formatted_phone:
            sheet.cell(row=row, column=status_col).value = "invalid number"
            wb.save(EXCEL_FILE)
            continue

        print(f"Verifying [{reverified_count + 1}]: {company_name} ({formatted_phone})...")

        try:
            # Directly open WhatsApp Web via browser tab
            url = f"https://web.whatsapp.com/send?phone={formatted_phone}"
            webbrowser.open(url)

            # INCREASED WAIT TIME: Give WhatsApp Web 14 seconds to fully load and render
            time.sleep(14)

            # Inspect center region for WhatsApp's green "OK" button signature (#00a884 modal popup)
            screenshot = pyautogui.screenshot()
            width, height = screenshot.size
            center_region = screenshot.crop((int(width * 0.35), int(height * 0.35), int(width * 0.65), int(height * 0.65)))
            
            invalid_popup_found = False
            for x in range(0, center_region.width, 15):
                for y in range(0, center_region.height, 15):
                    r, g, b = center_region.getpixel((x, y))
                    if r < 40 and 140 < g < 210 and 90 < b < 170:
                        invalid_popup_found = True
                        break
                if invalid_popup_found:
                    break

            if invalid_popup_found:
                # Dismiss modal by pressing enter (clicks OK) and raise exception
                pyautogui.press('enter')
                time.sleep(0.5)
                raise ValueError("Number is not on WhatsApp")

            # Number is valid on WhatsApp - update status to 'sent'
            sheet.cell(row=row, column=status_col).value = "sent"
            print(f"  --> CONFIRMED: Valid WhatsApp number.")

        except Exception as e:
            print(f"  --> INVALID: No WhatsApp ({e})")
            sheet.cell(row=row, column=status_col).value = "no whatsapp"

        # Close the open browser tab cleanly
        pyautogui.hotkey('ctrl', 'w')
        
        reverified_count += 1
        wb.save(EXCEL_FILE)

        # Pause between checks
        time.sleep(random.uniform(3, 5))

    wb.save(EXCEL_FILE)
    print(f"\n--- Verification Finished ---")
    print(f"Re-verified {reverified_count} total visited leads on sheet '{matched_sheet_name}'. Excel file updated.")


if __name__ == "__main__":
    target_sheet = input("Enter target sheet name to verify (e.g. Divyansh, Akash, Mahesh, Vinuthna): ").strip()
    verify_sheet_numbers(sheet_name=target_sheet)