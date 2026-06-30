import re
from typing import Optional

def extract_page_number(text: str) -> Optional[int]:
    match = re.search(r"(\d+)\s*페이지", text)
    if match:
        return int(match.group(1))
    return None