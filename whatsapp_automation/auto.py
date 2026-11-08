"""Send WhatsApp outreach from a dynamically selected Excel worksheet.

pip install -r requirements.txt
python -m playwright install chromium
python auto.py
"""

import os
import re
import time
from urllib.parse import quote

from openpyxl import load_workbook
import pywhatkit
from pywhatkit.core import core as pywhatkit_core
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "Exposys Real Estate Bangalore.xlsx")
IMAGE_PATH = os.path.join(BASE_DIR, "banner.jpeg")
BROWSER_PROFILE = os.path.join(BASE_DIR, ".whatsapp_browser_profile")
MAX_LEADS = 2
PAGE_READY_TIMEOUT_MS = 180_000
CONTACT_DELAY_SECONDS = 3
IMAGE_SEND_BUFFER_SECONDS = 3

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

If you'd rather not receive messages from us, just reply STOP."""

INVALID_DIALOG_TEXT = re.compile(
    r"phone number shared via url is invalid|isn't on whatsapp|is not on whatsapp|"
    r"not a valid phone number|invalid phone number",
    re.IGNORECASE,
)


def format_phone_number(raw_number, default_country_code="+91"):
    if raw_number is None:
        return None
    original = str(raw_number).strip()
    if original.lower() in {"not listed", "none", "nan", ""}:
        return None
    digits = re.sub(r"\D", "", original)
    if len(digits) == 10:
        return f"{default_country_code}{digits}"
    if len(digits) == 11 and digits.startswith("0"):
        return f"{default_country_code}{digits[1:]}"
    if len(digits) >= 11:
        return f"+{digits}"
    return None


def get_column_indices(sheet):
    return {
        str(sheet.cell(row=1, column=col).value).strip().lower(): col
        for col in range(1, sheet.max_column + 1)
        if sheet.cell(row=1, column=col).value is not None
    }


def find_composer(page):
    # WhatsApp changes data-tab values; contenteditable + textbox role are
    # more resilient than a single generated class name.
    candidates = page.locator('footer [contenteditable="true"]')
    if candidates.count():
        return candidates.last
    return page.get_by_role("textbox").last


def invalid_number_dialog(page):
    dialogs = page.get_by_role("dialog")
    for index in range(dialogs.count()):
        dialog = dialogs.nth(index)
        try:
            if INVALID_DIALOG_TEXT.search(dialog.inner_text(timeout=500)):
                return dialog
        except PlaywrightTimeoutError:
            continue
    # Some WhatsApp Web builds render the alert without role=dialog.
    body_text = page.locator("body").inner_text(timeout=1000)
    if INVALID_DIALOG_TEXT.search(body_text):
        return dialogs.last if dialogs.count() else True
    return None


def wait_for_chat_or_invalid(page):
    deadline = time.monotonic() + PAGE_READY_TIMEOUT_MS / 1000
    while time.monotonic() < deadline:
        if invalid_number_dialog(page):
            return False
        try:
            if page.locator('footer [contenteditable="true"]').count() > 0:
                return True
        except Exception:
            pass
        page.wait_for_timeout(500)
    raise TimeoutError(
        "WhatsApp Web did not finish loading. Check the internet connection and "
        "that WhatsApp is logged in in the opened browser."
    )


def wait_for_composer_text(page, composer, expected_text, timeout_ms=15_000):
    """Wait for URL-prefilled text, ignoring whitespace normalization by WhatsApp."""
    expected = re.sub(r"\s+", "", expected_text[:100])
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        actual = composer.inner_text(timeout=2_000)
        if expected in re.sub(r"\s+", "", actual):
            return
        page.wait_for_timeout(200)
    raise TimeoutError("WhatsApp did not finish populating the message composer.")


def send_image_with_pywhatkit_in_open_chat(page, phone, image_path, caption):
    """Use PyWhatKit's clipboard image flow without reopening the chat URL."""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image attachment not found: {image_path}")

    page.bring_to_front()
    original_open = pywhatkit_core.open
    original_sleep = pywhatkit_core.time.sleep

    def wait_longer_after_paste(seconds):
        # PyWhatKit's send_image waits one second after pasting the image.
        # Give WhatsApp three seconds to finish loading it before pressing Send.
        return original_sleep(IMAGE_SEND_BUFFER_SECONDS if seconds == 1 else seconds)

    try:
        # PyWhatKit normally opens the phone URL itself. The Playwright page is
        # already on that validated chat, so suppress only that second open.
        pywhatkit_core.open = lambda *args, **kwargs: True
        pywhatkit_core.time.sleep = wait_longer_after_paste
        pywhatkit.sendwhats_image(
            receiver=phone,
            img_path=image_path,
            caption=caption,
            wait_time=8,
            tab_close=False,
        )
    finally:
        pywhatkit_core.open = original_open
        pywhatkit_core.time.sleep = original_sleep


def send_one(page, phone, message, image_path=None):
    # Use digits in the query parameter; WhatsApp expects international format
    # without the leading plus sign here.
    digits = re.sub(r"\D", "", phone)
    url = f"https://web.whatsapp.com/send?phone={quote(digits)}&text={quote(message)}"
    page.goto(url, wait_until="domcontentloaded")
    if not wait_for_chat_or_invalid(page):
        return "no whatsapp"

    if image_path:
        composer = find_composer(page)
        composer.wait_for(state="visible", timeout=30_000)
        wait_for_composer_text(page, composer, message)
        page.wait_for_timeout(250)
        send_image_with_pywhatkit_in_open_chat(page, phone, image_path, message)
    else:
        composer = find_composer(page)
        composer.wait_for(state="visible", timeout=30_000)
        composer.fill(message)
        composer.press("Enter")

    return "sent"


def process_sheet_outreach(sheet_name, max_leads=MAX_LEADS, image_path=IMAGE_PATH):
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: Spreadsheet '{EXCEL_FILE}' not found.")
        return

    wb = load_workbook(EXCEL_FILE)
    matched_sheet_name = next(
        (name for name in wb.sheetnames if name.strip().lower() == sheet_name.strip().lower()),
        None,
    )
    if not matched_sheet_name:
        print(f"Sheet '{sheet_name}' not found. Available sheets: {wb.sheetnames}")
        wb.close()
        return

    sheet = wb[matched_sheet_name]
    cols = get_column_indices(sheet)
    status_col = cols.get("status")
    response_col = cols.get("response")
    if not status_col:
        status_col = sheet.max_column + 1
        sheet.cell(1, status_col, "Status")
    if not response_col:
        response_col = sheet.max_column + 1
        sheet.cell(1, response_col, "Response")

    processed_count = 0
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            BROWSER_PROFILE,
            headless=False,
            no_viewport=True,
            args=["--start-maximized"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            for row in range(2, sheet.max_row + 1):
                if processed_count >= max_leads:
                    break
                if sheet.cell(row, status_col).value and str(sheet.cell(row, status_col).value).strip():
                    continue

                raw_phone = sheet.cell(row, cols.get("contact_number", 3)).value
                company_name = sheet.cell(row, cols.get("company_name", 1)).value or "Valued Client"
                area = sheet.cell(row, cols.get("area", 5)).value or "Bengaluru"
                zone = sheet.cell(row, cols.get("zone", 6)).value or "Central"
                phone = format_phone_number(raw_phone)

                if not phone:
                    sheet.cell(row, status_col, "invalid")
                    sheet.cell(row, response_col, "no")
                    wb.save(EXCEL_FILE)
                    continue

                message = MESSAGE_TEMPLATE.format(company_name=company_name, area=area, zone=zone)
                print(f"[{processed_count + 1}/{max_leads}] {company_name} ({phone})")
                status = None
                try:
                    status = send_one(page, phone, message, image_path)
                    sheet.cell(row, status_col, status)
                    sheet.cell(row, response_col, "no")
                    if status == "sent":
                        processed_count += 1
                        print("  --> Message sent")
                    else:
                        print("  --> Number is not registered with WhatsApp")
                except KeyboardInterrupt:
                    wb.save(EXCEL_FILE)
                    print("Stopped by user. Spreadsheet changes saved.")
                    break
                except Exception as exc:
                    # Do not mislabel browser/network/login failures as an
                    # invalid WhatsApp number. The row can be reviewed and retried.
                    sheet.cell(row, status_col, "error")
                    sheet.cell(row, response_col, "no")
                    print(f"  --> Could not process this row: {exc}")
                    if image_path or page.is_closed():
                        print("Stopping after this failure to avoid leaving an image draft in another chat.")
                        break
                finally:
                    wb.save(EXCEL_FILE)
                try:
                    time.sleep(CONTACT_DELAY_SECONDS)
                except KeyboardInterrupt:
                    wb.save(EXCEL_FILE)
                    print("Stopped by user. Spreadsheet changes saved.")
                    break

        finally:
            try:
                context.close()
            except Exception as exc:
                print(f"Browser was already closed: {exc}")
            finally:
                wb.save(EXCEL_FILE)
                wb.close()

    print(f"Completed: {processed_count} message(s) sent on '{matched_sheet_name}'.")


if __name__ == "__main__":
    target_sheet = input("Enter target sheet name (e.g. Divyansh, Akash, Mahesh, Vinuthna): ").strip()
    process_sheet_outreach(target_sheet, max_leads=MAX_LEADS, image_path=IMAGE_PATH)
