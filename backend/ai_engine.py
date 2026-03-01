def detect_category(text):
    text = text.lower()

    if "pothole" in text:
        return "Road Issue"
    elif "garbage" in text:
        return "Waste Management"
    elif "water" in text:
        return "Water Supply"
    else:
        return "General"

def detect_severity(text):
    text = text.lower()

    if "accident" in text or "danger" in text:
        return "High"
    elif "urgent" in text:
        return "Medium"
    else:
        return "Low"