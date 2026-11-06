import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time


def check_website(url):

    result = {
        "website_status": "Not Checked",
        "http_status": None,
        "response_time_seconds": None,
        "https_enabled": False,
        "page_title": None,
        "meta_description": None,
        "remarks": ""
    }

    if not isinstance(url, str) or not url.strip():
        result["website_status"] = "Missing URL"
        result["remarks"] = "Website URL not provided"
        return result

    url = url.strip()

    # Add HTTPS if no protocol is provided
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        start_time = time.time()

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; WebsiteAuditBot/1.0)"
            },
            allow_redirects=True
        )

        elapsed = round(time.time() - start_time, 2)

        result["http_status"] = response.status_code
        result["response_time_seconds"] = elapsed
        result["https_enabled"] = (
            urlparse(response.url).scheme == "https"
        )

        if response.status_code == 200:
            result["website_status"] = "Working"
        else:
            result["website_status"] = "HTTP Error"

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract page title
        title = soup.find("title")
        if title:
            result["page_title"] = title.get_text(strip=True)

        # Extract meta description
        description = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if description:
            result["meta_description"] = description.get("content", "")

        remarks = []

        if response.status_code != 200:
            remarks.append(f"HTTP status {response.status_code}")

        if not result["https_enabled"]:
            remarks.append("HTTPS not enabled")

        if not result["page_title"]:
            remarks.append("Missing page title")

        if not result["meta_description"]:
            remarks.append("Missing meta description")

        if not remarks:
            remarks.append("Basic website checks passed")

        result["remarks"] = "; ".join(remarks)

    except requests.exceptions.Timeout:
        result["website_status"] = "Timeout"
        result["remarks"] = "Website took too long to respond"

    except requests.exceptions.SSLError:
        result["website_status"] = "SSL Error"
        result["remarks"] = "SSL certificate verification failed"

    except requests.exceptions.RequestException as error:
        result["website_status"] = "Connection Failed"
        result["remarks"] = str(error)[:200]

    return result

