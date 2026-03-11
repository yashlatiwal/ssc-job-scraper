import re

# ── Pay level keyword map ─────────────────────────────────────────────────────
PAY_KEYWORDS = [
    # Level 10 — Senior gazetted / IAS-grade (~₹90k+)
    (r'\b(IAS|IPS|IFS|deputy\s*collector|assistant\s*commandant|UPSC\s*civil|CGL\s*group\s*a|combined\s*graduate\s*level\s*group\s*a)\b', "Level 10"),

    # Level 9 — Gazetted officers (~₹75k–₹85k)
    (r'\b(section\s*officer|DSP\b|deputy\s*superintendent|senior\s*accounts?\s*officer|administrative\s*officer|MPPSC|NPSC|PCS\b|NPSC\b|combined\s*technical\s*service|CTS\b)\b', "Level 9"),

    # Level 8 — Group B Gazetted (~₹65k–₹75k)
    (r'\b(assistant\s*audit\s*officer|AAO\b|assistant\s*accounts?\s*officer|enforcement\s*(?:officer|directorate)|OPSC\b|dental\s*surgeon|VAS\b|VEO\b|assistant\s*director)\b', "Level 8"),

    # Level 7 — Inspector / Sub-Inspector grade (~₹55k–₹65k)
    (r'\b(income\s*tax\s*inspector|GST\s*inspector|CBI\b|NIA\b|preventive\s*officer|station\s*master|assistant\s*manager|IBPS\s*deputy|IDBI\s*assistant\s*manager|excise\s*inspector|security\s*officer|sub\s*inspector|SI\b|CGL\b)\b', "Level 7"),

    # Level 6 — JE / Bank PO / Graduate posts (~₹45k–₹55k)
    (r'\b(junior\s*engineer|JE\b|JJA\b|junior\s*judicial\s*assistant|stenographer\s*grade[\s-]?c|auditor\b|accountant\b|RBI\s*(assistant|bank\s*assistant)|IBPS\b|bank\s*(PO|officer)|AFCAT\b|deputy\s*manager|IDBI\s*(?:jr|junior)\.?\s*(?:asst|assistant)\.?\s*manager|junior\s*asst\.?\s*manager|graduate\s*engineer|CEL\b|APSSB\s*CGL|APSSB\b)\b', "Level 6"),
    # Also catch standalone "engineer" / "doctor" / "professor" but only when not already matched
    (r'\b(engineer\b|doctor\b|professor\b|IOCL\b|NEET\b|IDBI\b)\b', "Level 6"),

    # Level 5 — Technician / Pharmacist / Nurse (~₹38k–₹45k)
    (r'\b(technician\b|pharmacist\b|lab\s*assistant|foreman\b|draftsman\b|fireman\b|fire\s*officer|junior\s*technical|apprentice\b|nurse\b|staff\s*nurse|UPSSSC\s*pharmacist|KMC\s*staff\s*nurse|nursing)\b', "Level 5"),

    # Level 4 — Head Constable / UDC / Senior Steno (~₹30k–₹38k)
    (r'\b(stenographer\s*grade[\s-]?d|head\s*constable|UDC\b|upper\s*division\s*clerk|steno[\s-]?typist|senior\s*scale\s*steno|senior\s*stenograph|stenographer\b|steno\b|senior\s*assistant|sr\.?\s*assistant|PSSSB\s*sr\.?\s*assistant|PSSSB\s*senior\b|non\s*teaching\b|NCERT\s*non\s*teaching)\b', "Level 4"),

    # Level 3 — Constable / Clerk / Teacher / DEO (~₹25k–₹32k)
    (r'\b(constable\b|postal\s*assistant|sorting\s*assistant|DEO\b|data\s*entry\s*operator|tax\s*assistant|Agniveer\b|NTPC\b|SSR\b|MR\b|GDS\b|teacher\b|JBT\b|PSTET\b|CTET\b|anganwadi\b|HPRCA|KVS\b|NVS\b|navy\s*(?:agniveer|SSR|MR)|punjab\s*police|police\s*constable|PSSSB\s*clerk|IT\s*clerk|IOCL\s*apprentice)\b', "Level 3"),

    # Level 2 — LDC / JSA / Clerk / Junior Assistant (~₹22k–₹28k)
    (r'\b(LDC\b|lower\s*division\s*clerk|junior\s*secretariat|court\s*clerk|clerk\b|JSA\b|CHSL\b|junior\s*assistant|jr\.?\s*assistant|bank\s*assistant\b|RBI\s*assistant\b|SBI\s*clerk|IDBI\s*jr\.?\s*asst\.?\s*manager|IDBI\s*junior\s*assistant|SSB\s*clerk|SSB\s*junior\s*assistant|palwal\s*court|chandigarh\s*court|nuh\s*court|high\s*court\s*clerk)\b', "Level 2"),

    # Level 1 — MTS / Group D / Peon / 4th Grade (~₹18k–₹22k)
    (r'\b(MTS\b|multi\s*tasking|peon\b|attendant\b|safai\b|helper\b|mali\b|messenger\b|chowkidar\b|group[\s-]?[dD]\b|4th[\s-]?grade|RSSB\s*4th|fourth\s*grade)\b', "Level 1"),
]

# Actual in-hand salary (CTC with DA ~53%, HRA, TA)
PAY_DISPLAY = {
    "Level 1":  "₹28–₹30k",
    "Level 2":  "₹30–₹32k",
    "Level 3":  "₹32–₹35k",
    "Level 4":  "₹37–₹40k",
    "Level 5":  "₹42–₹45k",
    "Level 6":  "₹50–₹55k",
    "Level 7":  "₹63–₹70k",
    "Level 8":  "₹68–₹75k",
    "Level 9":  "₹75–₹85k",
    "Level 10": "₹80–₹90k",
}


def infer_pay_from_text(text):
    """Infer pay level from job title using keyword matching."""
    if not text:
        return None
    for pattern, level in PAY_KEYWORDS:
        if re.search(pattern, text, re.I):
            return level
    return None


def find_vacancies(text):
    if not text:
        return 0
    patterns = [
        r'(\d[\d,]+)\s*(?:posts?|vacancies|vacancy|seats?|positions?)',
        r'(?:posts?|vacancies|vacancy|seats?)\s*[:\-]?\s*(\d[\d,]+)',
        r'(\d[\d,]+)\s*(?:nos?\.?|numbers?)',
        r'total\s*[:\-]?\s*(\d[\d,]+)',
        r'recruitment\s+(?:of\s+)?(\d[\d,]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            v = int(m.group(1).replace(',', ''))
            if 1 <= v <= 200000:
                return v
    return 0


def find_age(text):
    if not text:
        return ""
    patterns = [
        r'age\s*(?:limit)?\s*[:\-]?\s*(\d{2})\s*(?:to|-)\s*(\d{2})\s*years?',
        r'(\d{2})\s*(?:to|-)\s*(\d{2})\s*years?\s*(?:of\s*age|age\s*limit)',
        r'minimum\s*age\s*[:\-]?\s*(\d{2}).*?maximum\s*age\s*[:\-]?\s*(\d{2})',
        r'age\s*[:\-]\s*(\d{2})',
        r'(\d{2})\s*years?\s*(?:and|&)\s*above',
        r'below\s*(\d{2})\s*years?',
        r'not\s*exceed(?:ing)?\s*(\d{2})\s*years?',
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
        rf'(\d{{1,2}}\s*{months}\s*\d{{4}})\s*(?:is\s*the\s*last\s*date|last\s*date)',
        rf'(\d{{1,2}}[\/\-]\d{{1,2}}[\/\-]\d{{4}})',
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
    """Extract explicit pay level or salary range from page text."""
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
                if abs(lo - basic) < 3000:
                    return f"Level {level}"
    return ""


def find_qualification(text):
    if not text:
        return "Graduation"
    if re.search(r'\b10th\b|\bmatric(?:ulation)?\b|\bSSLC\b', text, re.I):
        return "10th"
    if re.search(r'\b12th\b|\binter(?:mediate)?\b|\bHSC\b|\bNDA\b|\bAgniveer\b', text, re.I):
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
            if "vacanc" in key or "post" in key:
                v = find_vacancies(val)
                if v:
                    detail["vacancies"] = v
            elif "age" in key:
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


def clean(text):
    """Collapse whitespace and strip a block of text."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def extract_fields_from_detail(url):
    """Fetch a job detail page and extract fields. Returns dict with keys:
    vac, q, age, ld, pay."""
    try:
        import requests
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        detail = extract_from_tables(soup)
        text = clean(soup.get_text(separator=" "))
        merged = merge_with_text(detail, text)
        return {
            "vac": merged.get("vacancies", 0),
            "q": merged.get("qualification", ""),
            "age": merged.get("age", ""),
            "ld": merged.get("lastDate", ""),
            "pay": merged.get("payLevel", ""),
        }
    except Exception as e:
        print(f"    ⚠️ extract_fields_from_detail: {e}")
        return {}


def merge_with_text(detail, full_text, post_title=""):
    """Fill blank fields using full page text, then keyword inference as last resort."""
    if not detail.get("vacancies"):
        detail["vacancies"] = find_vacancies(full_text)
    if not detail.get("age"):
        detail["age"] = find_age(full_text)
    if not detail.get("lastDate"):
        detail["lastDate"] = find_lastdate(full_text)
    if not detail.get("payLevel"):
        detail["payLevel"] = find_pay(full_text)
    # Last resort: keyword inference from title
    if not detail.get("payLevel") or detail["payLevel"] in ("", "Not specified"):
        inferred = infer_pay_from_text(post_title) or infer_pay_from_text(full_text[:500])
        if inferred:
            detail["payLevel"] = inferred
    return detail
