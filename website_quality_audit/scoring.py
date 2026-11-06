def calculate_score(data):

    score = 0
    remarks = []

    # 1. Website availability – 30 marks
    if data["website_status"] == "Working":
        score += 30
    else:
        remarks.append("Website availability issue")

    # 2. HTTPS security – 25 marks
    if data["https_enabled"]:
        score += 25
    else:
        remarks.append("HTTPS security improvement required")

    # 3. Page title – 20 marks
    if data["page_title"]:
        score += 20
    else:
        remarks.append("Page title missing")

    # 4. Meta description – 15 marks
    if data["meta_description"]:
        score += 15
    else:
        remarks.append("Meta description missing")

    # 5. Response time – 10 marks
    response_time = data["response_time_seconds"]

    if response_time is not None:

        if response_time <= 2:
            score += 10
        elif response_time <= 4:
            score += 7
        elif response_time <= 6:
            score += 4
        else:
            remarks.append("Website response time is slow")
    else:
        remarks.append("Response time unavailable")

    # Rating
    if score >= 90:
        rating = "Excellent"
    elif score >= 75:
        rating = "Good"
    elif score >= 50:
        rating = "Average"
    else:
        rating = "Poor"

    if not remarks:
        remarks.append("All basic website checks passed")

    return {
        "website_score": score,
        "website_rating": rating,
        "final_remarks": "; ".join(remarks)
    }