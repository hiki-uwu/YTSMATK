import re

def preprocess_text(data):
    """
    Preprocess text data. If data is a list (comments), clean each comment.
    If data is a string (transcript), clean it.
    """
    if isinstance(data, list):
        cleaned = []
        for item in data:
            # Assuming comment text is stored under the 'text' key
            text = item.get('text', '')
            text = re.sub(r'http\S+', '', text)  # Remove URLs
            text = re.sub(r'\s+', ' ', text).strip()
            cleaned.append(text)
        return cleaned
    elif isinstance(data, str):
        text = re.sub(r'http\S+', '', data)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    else:
        return str(data)
