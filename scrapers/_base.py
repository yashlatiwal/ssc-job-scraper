import re

# ── Pay level keyword map ─────────────────────────────────────────────────────
PAY_KEYWORDS = [
    # Level 10 — IAS-grade (~₹80–90k)
    (r'\b(IAS|IPS|IFS|deputy\s*collector|UPSC\s*civil|UPSC\s*CMSE|CMSE\b|UPSC\s*CAPF|CAPF\b|civil\s*services)\b', "Level 10"),
    # Level 9 — Gazetted Group A (~₹75–85k)
    (r'\b(section\s*officer|DSP\b|deputy\s*superintendent|senior\s*accounts?\s*officer|administrative\s*officer|MPPSC|NPSC|PCS\b|pollution\s*control|HKRN\b|UPSSSC\s*pollution)\b', "Level 9"),
    # Level 8 — Group B Gazetted (~₹68–75k)
    (r'\b(assistant\s*audit\s*officer|AAO\b|assistant\s*accounts?\s*officer|enforcement\s*(?:officer|directorate)|OPSC\b|dental\s*surgeon|VAS\b|VEO\b|assistant\s*director|NIB\b)\b', "Level 8"),
    # Level 7 — Inspector grade (~₹63–70k)
    (r'\b(income\s*tax\s*inspector|GST\s*inspector|CBI\b|NIA\b|preventive\s*officer|station\s*master|assistant\s*manager|IBPS\s*deputy|excise\s*inspector|sub\s*inspector|SI\b|CGL\b|ALP\b|RRB\s*ALP|loco\s*pilot|APSSB\b)\b', "Level 7"),
    # Level 6 — JE / Graduate posts (~₹50–55k)
    (r'\b(junior\s*engineer|JE\b|JJA\b|junior\s*judicial\s*assistant|stenographer\s*grade[\s-]?c|auditor\b|accountant\b|RBI\s*assistant|IBPS\b|bank\s*(PO|officer)|AFCAT\b|deputy\s*manager|graduate\s*engineer|CEL\b|guest\s*instructor|paramedical\b|RRB\s*paramedical|IOCL\b|IDBI\b)\b', "Level 6"),
    (r'\b(engineer\b|doctor\b|professor\b|NEET\b)\b', "Level 6"),
    # Level 5 — Technician / Nurse (~₹42–45k)
    (r'\b(technician\b|pharmacist\b|lab\s*assistant|foreman\b|draftsman\b|fireman\b|apprentice\b|nurse\b|staff\s*nurse|nursing|AAI\b)\b', "Level 5"),
    # Level 4 — Head Constable / Steno (~₹37–40k)
    (r'\b(stenographer\b|steno\b|head\s*constable|UDC\b|upper\s*division\s*clerk|senior\s*assistant|sr\.?\s*assistant|non\s*teaching\b|NCERT\s*non\s*teaching|PSSSB\s*senior)\b', "Level 4"),
    # Level 3 — Constable / Teacher / Clerk (~₹32–35k)
    (r'\b(constable\b|DEO\b|data\s*entry|tax\s*assistant|Agniveer\b|NTPC\b|SSR\b|MR\b|GDS\b|teacher\b|JBT\b|PSTET\b|CTET\b|anganwadi\b|KVS\b|NVS\b|punjab\s*police|police\s*constable|ITI\b|HPRCA\b|navy\b)\b', "Level 3"),
    # Level 2 — LDC / Clerk / Junior Assistant (~₹30–32k)
    (r'\b(LDC\b|lower\s*division\s*clerk|court\s*clerk|clerk\b|JSA\b|CHSL\b|junior\s*assistant|jr\.?\s*assistant|bank\s*assistant\b|SBI\s*clerk|SSB\s*clerk|SSB\s*junior)\b', "Level 2"),
    # Level 1 — MTS / Group D (~₹28–30k)
    (r'\b(MTS\b|multi\s*tasking|peon\b|attendant\b|helper\b|group[\s-]?[dD]\b|4th[\s-]?grade|RSSB\s*4th)\b', "Level 1"),
]

PAY_DISPLAY = {
    "Level 1":  "₹28–30k",
    "Level 2":  "₹30–32k",
    "Level 3":  "₹32–35k",
    "Level 4":  "₹37–40k",
    "Level 5":  "₹42–45k",
    "Level 6":  "₹50–55k",
    "Level 7":  "₹63–70k",
    "Level 8":  "₹68–75k",
    "Level 9":  "₹75–85k",
    "Level 10": "₹80–90k",
}

def infer_pay_from_text(text):
    if not text:
        return None
    for pattern, level in PAY_KEYWORDS:
        if re.search(pattern, text, re.I):
            return level
    return None

def clean(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def find_vacancies(text):
    if not text:
        return 0
    patterns = [
        r'(\d[\d,]+)\s*(?:posts?|vacancies|vacancy|seats?|positions?)',
        r'(?:posts?|vacancies|vacancy|seats?)\s*[:\-]?\s*(\d[\d,]+)',
        r'(\d[\d,]+)\s*(?:nos?\.?|numbers?)',
        r'total\s*[:\-]?\s*(\d[\d,]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            v = int(m.group(1).replace(',', ''))
            if 1 <= v <= 200000 and not (2020 <= v <= 2030):
                return v
    return 0

def find_age(text):
    if not text:
        return ""
    patterns = [
        r'age\s*(?:limit)?\s*[:\-]?\s*(\d{2})\s*(?:to|-)\s*(\d{2})\s*years?',
        r'(\d{2})\s*(?:to|-)\s*(\d{2})\s*years?\s*(?:of\s*age|age\s*limit)',
        r'age\s*[:\-]\s*(\d{2})',
        r'below\s*(\d{2})\s*years?',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            groups = m.groups()
            if len(groups) == 2 and groups[1]:
                a, b = int(groups[0]), int(groups[1])
                if 14 <= a <= 65 and 14 <= b <= 65:
                    return f"{a}-{b}"
            elif groups[0]:
                a = int(groups[0])
                if 14 <= a <= 65:
                    return str(a)
    return ""

def find_lastdate(text):
    if not text:
        return ""
    months = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
    patterns = [
        rf'last\s*date\s*[:\-]?\s*(\d{{1,2}}\s*{months}\s*\d{{4}})',
        rf'apply\s*(?:by|before|till|until)\s*[:\-]?\s*(\d{{1,2}}\s*{months}\s*\d{{4}})',
        rf'closing\s*date\s*[:\-]?\s*(\d{{1,2}}\s*{months}\s*\d{{4}})',
        rf'(\d{{1,2}}[\\/\-]\d{{1,2}}[\\/\-]\d{{4}})',
        rf'({months}\s*\d{{1,2}},?\s*\d{{4}})',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            d = m.group(1).strip()
            if re.search(r'\d{4}', d):
                return d
    return ""

def find_pay(text):
    if not text:
        return ""
    m = re.search(r'pay\s*(?:level|matrix|band|scale)\s*[:\-]?\s*(\d{1,2})', text, re.I)
    if m:
        level = int(m.group(1))
        if 1 <= level <= 14:
            return f"Level {level}"
    m = re.search(r'(?:rs\.?|inr|₹)\s*([\d,]+)\s*(?:to|-)\s*([\d,]+)', text, re.I)
    if m:
        lo = int(m.group(1).replace(',', ''))
        hi = int(m.group(2).replace(',', ''))
        if lo > 5000 and hi > lo:
            for basic, level in [(56100,10),(53100,9),(47600,8),(44900,7),(35400,6),
                                  (29200,5),(25500,4),(21700,3),(19900,2),(18000,1)]:
                if abs(lo - basic) < 5000:
                    return f"Level {level}"
    return ""

def find_qualification(text):
    if not text:
        return "Graduation"
    if re.search(r'\b10th\b|\bmatric(?:ulation)?\b|\bSSLC\b', text, re.I):
        return "10th"
    if re.search(r'\b12th\b|\binter(?:mediate)?\b|\bHSC\b|\bNDA\b|\bAgniveer\b|10\+2', text, re.I):
        return "12th"
    return "Graduation"

def extract_from_tables(soup):
    detail = {"vacancies": 0, "age": "", "lastDate": "", "payLevel": ""}
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) < 2:
                continue
            key = cells[0].lower()
            val = cells[1]
            if "age" in key:
                a = find_age(val)
                if a:
                    detail["age"] = a
            elif "last" in key or "closing" in key:
                d = find_lastdate(val)
                if d:
                    detail["lastDate"] = d
            elif "pay" in key or "salary" in key or "level" in key:
                p = find_pay(val)
                if p:
                    detail["payLevel"] = p
    return detail

def merge_with_text(detail, full_text, post_title=""):
    if not detail.get("age"):
        detail["age"] = find_age(full_text)
    if not detail.get("lastDate"):
        detail["lastDate"] = find_lastdate(full_text)
    if not detail.get("payLevel"):
        detail["payLevel"] = find_pay(full_text)
    if not detail.get("payLevel") or detail["payLevel"] in ("", "Not specified"):
        inferred = infer_pay_from_text(post_title) or infer_pay_from_text(full_text[:500])
        if inferred:
            detail["payLevel"] = inferred
    return detail

def extract_fields_from_detail(url):
    """Fetch detail page for age, lastDate, pay ONLY. Never use for vacancy."""
    try:
        import requests
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        detail = extract_from_tables(soup)
        text = clean(soup.get_text(separator=" "))
        merged = merge_with_text(detail, text[:3000])
        return {
            "q": merged.get("qualification", ""),
            "age": merged.get("age", ""),
            "ld": merged.get("lastDate", ""),
            "pay": merged.get("payLevel", ""),
        }
    except Exception as e:
        print(f"    ⚠️ detail fetch failed: {e}")
        return {}
