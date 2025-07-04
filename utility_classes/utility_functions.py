import re

def detect_language(text: str) -> str:
    text = re.sub(r'\s+|[^\w\u4e00-\u9fff]', '', text)

    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    english_chars = re.findall(r'[A-Za-z]', text)

    if not chinese_chars and english_chars:
        return "English"
    elif chinese_chars and not english_chars:
        return "Chinese"
    elif len(chinese_chars) > len(english_chars):
        return "Chinese"
    elif len(english_chars) > len(chinese_chars):
        return "English"
    else:
        return "Unknown"