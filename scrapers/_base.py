"""Shared extraction utilities for all scrapers."""
import re

PAY_MATRIX = {
    1:  {"basic": "₹18,000", "inhand": "₹28,000–₹30,000"},
    2:  {"basic": "₹19,900", "inhand": "₹30,000–₹32,000"},
    3:  {"basic": "₹21,700", "inhand": "₹32,000–₹35,000"},
    4:  {"basic": "₹25,500", "inhand": "₹37,000–₹40,000"},
    5:  {"basic": "₹29,200", "inhand": "₹42,000–₹45,000"},
    6:  {"basic": "₹35,400", "inhand": "₹50,000–₹55,000"},
    7:  {"basic": "₹44,900", "inhand": "₹63,000–₹70,000"},
    8:  {"basic": "₹47,600", "inhand": "₹68,000–₹75,000"},
    9:  {"basic": "₹53,100", "inhand": "₹75,000–₹85,000"},
    10: {"basic": "₹56,100", "inhand": "₹80,000–₹90,000"},
    11: {"basic": "₹67,700", "inhand": "₹95,000–₹1,05,000"},
    12: {"basic": "₹78,800", "inhand": "₹1,10,000–₹1,25,000"},
    13: {"basic": "₹1,23,100", "inhand": "₹1,70,000–₹1,90,000"},
    14: {"basic": "₹1,44,200", "inhand": "₹2,00,000–₹2,20,000"},
}

def clean(s):
    return re.sub(r'\s+', ' ', str(s)).strip()

def find_vacancies(text):
    patterns = [
        r'total\s+(?:no\.?\s*of\s+)?(?:posts?|vacancies?|seats?)[:\s]+(\d[\d,]+)',
        r'(?:no\.?\s*of\s+)?(?:posts?|vacancies?)[:\s]+(\d[\d,]+)',
        r'(\d[\d,]+)\s+(?:posts?|vacancies?)\s+(?:available|notified|announced)',
        r'recruitment\s+(?:of\s+)?(\d[\d,]+)\s+(?:posts?|vacancies?)',
        r'(\d{2,6})\s+(?:posts?|vacancies?)',
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            v = int(m.group(1).replace(",",""))
            if 1 <= v <= 200000: return v
    return 0

def find_age(text):
    patterns = [
        r'age\s*limit[:\s]+(\d{2})\s*(?:years?)?\s*(?:to|-|–|and)\s*(\d{2})\s*years?',
        r'age[:\s]+(\d{2})\s*(?:to|-|–)\s*(\d{2})\s*years?',
        r'(\d{2})\s*(?:to|-|–)\s*(\d{2})\s*years?\s*(?:\(age\)|age|\(as on)',
        r'minimum\s*age[:\s]+(\d{2}).*?maximum\s*age[:\s]+(\d{2})',
        r'age\s*(?:should be|must be)[:\s]+(\d{2})\s*(?:to|-)\s*(\d{2})',
        r'(\d{2})\s*-\s*(\d{2})\s*years?\s*(?:as on|as of)',
        r'(\d{2})\s*(?:to|-)\s*(\d{2})\s*(?:yrs|years)',
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            if 14 <= lo <= 50 and lo < hi <= 65: return f"{lo}-{hi} Years"
    return "Not specified"

def find_lastdate(text):
    months = r'(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)'
    patterns = [
        rf'last\s*date[:\s]+(\d{{1,2}}\s+{months}\w*\s+\d{{4}})',
        r'last\s*date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        rf'closing\s*date[:\s]+(\d{{1,2}}\s+{months}\w*\s+\d{{4}})',
        r'closing\s*date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        rf'apply.*?(?:before|by|till|upto)[:\s]+(\d{{1,2}}\s+{months}\w*\s+\d{{4}})',
        r'apply.*?(?:before|by|till|upto)[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        rf'(?:submit|submission).*?(?:by|before|till)[:\s]+(\d{{1,2}}\s+{months}\w*\s+\d{{4}})',
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            val = m.group(1).strip()
            if re.search(r'\d{4}', val) and len(val) > 4: return val
    return "TBD"

def find_pay(text):
    m = re.search(r'pay\s*(?:level|matrix)[:\s]*(?:level[- ]?)?(\d+)', text, re.I)
    if not m: m = re.search(r'level[- ]?(\d+)\s+(?:of\s+)?(?:pay|7th\s*cpc)', text, re.I)
    if m:
        lvl = int(m.group(1))
        if lvl in PAY_MATRIX:
            p = PAY_MATRIX[lvl]
            return f"Level {lvl} | {p['inhand']}/mo"
        elif 1 <= lvl <= 18: return f"Level {lvl}"

    m = re.search(r'(?:rs\.?|₹)\s*([\d,]+)\s*(?:to|-|–)\s*(?:rs\.?|₹)?\s*([\d,]+)', text, re.I)
    if m:
        lo, hi = int(m.group(1).replace(",","")), int(m.group(2).replace(",",""))
        # Must be plausible salary, not a date or ID number
        if 5000 <= lo <= 500000 and hi > lo and hi <= 1000000:
            return f"₹{lo//1000}k-{hi//1000}k/mo"

    m = re.search(r'(?:fixed\s*pay|consolidated|stipend)[:\s]+(?:rs\.?|₹)\s*([\d,]+)', text, re.I)
    if m:
        amt = int(m.group(1).replace(",",""))
        if 5000 < amt <= 500000: return f"₹{amt//1000}k/mo"

    return "Not specified"

def find_qualification(text):
    if re.search(r'\b10th\b|matriculation|sslc|class\s*10|10\s*pass|high\s*school|\b8th\b', text, re.I): return "10th"
    if re.search(r'\b12th\b|intermediate|hsc|class\s*12|10\+2|12\s*pass|higher\s*secondary', text, re.I): return "12th"
    if re.search(r'graduation|degree|bachelor|b\.?sc|b\.?a\.?\b|b\.?com|b\.?tech|graduate\b', text, re.I): return "Graduation"
    return "Graduation"

def extract_from_tables(soup):
    """Extract details from structured HTML tables."""
    detail = {"vacancies":0,"age":"Not specified","lastDate":"TBD","payLevel":"Not specified","qualification":"Graduation"}
    for row in soup.select("table tr"):
        cells = [clean(td.get_text(" ")) for td in row.find_all(["td","th"])]
        if len(cells) < 2: continue
        key = cells[0].lower()
        val = " ".join(cells[1:]).strip()
        if not val or val in ["-","–","na","n/a","nil"]: continue

        if any(k in key for k in ["vacanc","no. of post","total post","number of post"]):
            v = find_vacancies(val + " posts")
            if v: detail["vacancies"] = v
        elif "age" in key:
            a = find_age(val + " years")
            if a != "Not specified": detail["age"] = a
        elif any(k in key for k in ["last date","closing date","end date","apply before","final date","application date"]):
            ld = find_lastdate("last date: " + val)
            if ld != "TBD": detail["lastDate"] = ld
            elif re.search(r'\d{4}', val) and len(val) > 4: detail["lastDate"] = val[:40]
        elif any(k in key for k in ["pay level","pay scale","pay matrix","salary","pay band","remuneration","ctc","emolument","stipend"]):
            # Skip if value looks like a date
            if not re.match(r'^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$', val.strip()):
                p = find_pay(val)
                if p != "Not specified": detail["payLevel"] = p
        elif any(k in key for k in ["qualif","education","academic","eligib"]):
            detail["qualification"] = find_qualification(val)

    return detail

def merge_with_text(detail, text):
    """Fill in any remaining blanks using full page text."""
    if detail["vacancies"] == 0:       detail["vacancies"] = find_vacancies(text)
    if detail["age"] == "Not specified": detail["age"] = find_age(text)
    if detail["lastDate"] == "TBD":    detail["lastDate"] = find_lastdate(text)
    if detail["payLevel"] == "Not specified": detail["payLevel"] = find_pay(text)
    detail["lastDateFull"] = detail["lastDate"]
    return detail
