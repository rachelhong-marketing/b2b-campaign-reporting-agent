"""Read ad platform exports and the CRM leads export, each with its own column names, into one shape."""
import csv
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# file name -> (platform, {internal column: [accepted header labels]})
AD_FILES = {
    "google_ads.csv": ("Google Ads", {"date": ["Day", "Week", "Date", "Month"], "campaign": ["Campaign"],
                                      "spend": ["Cost", "Spend"], "impressions": ["Impr.", "Impressions"],
                                      "clicks": ["Clicks"]}),
    "linkedin_ads.csv": ("LinkedIn", {"date": ["Start Date (in UTC)", "Date"], "campaign": ["Campaign Name", "Campaign"],
                                      "spend": ["Total Spent", "Amount Spent", "Spend"], "impressions": ["Impressions"],
                                      "clicks": ["Clicks"]}),
    "meta_ads.csv": ("Meta", {"date": ["Reporting starts", "Day", "Date"], "campaign": ["Campaign name", "Campaign"],
                              "spend": ["Amount spent (USD)", "Amount spent", "Spend"], "impressions": ["Impressions"],
                              "clicks": ["Link clicks", "Clicks"]}),
    "display_ads.csv": ("Display", {"date": ["Date", "Week", "Day"], "campaign": ["Campaign", "Campaign Name"],
                                    "spend": ["Spend", "Cost"], "impressions": ["Impressions"], "clicks": ["Clicks"]}),
}
LEAD_COLUMNS = {
    "lead_id": ["Lead ID", "Id"], "email": ["Email"], "created": ["Created Date", "Create Date"],
    "utm_source": ["UTM Source"], "utm_medium": ["UTM Medium"], "utm_campaign": ["UTM Campaign"],
    "utm_content": ["UTM Content"], "form": ["Form", "Form Name", "Asset"],
    "mql_date": ["MQL Date"], "sal_date": ["SAL Date"], "sql_date": ["SQL Date"],
}
LEADS_FILE = "crm_leads.csv"
DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %I:%M %p", "%b %d, %Y", "%Y-%m"]


def _key(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def to_date(v):
    v = (v or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            pass
    return None


def to_number(v):
    v = re.sub(r"[^0-9.\-]", "", v or "")
    return float(v) if v not in ("", "-", ".") else 0.0


def _read(path, columns):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        by_key = {_key(h): h for h in (reader.fieldnames or [])}
        mapping = {c: next((by_key[_key(l)] for l in [c] + labels if _key(l) in by_key), None)
                   for c, labels in columns.items()}
        rows = [{c: (r.get(src) or "").strip() if src else "" for c, src in mapping.items()}
                for r in reader if any((v or "").strip() for v in r.values() if isinstance(v, str))]
    return rows, [c for c, src in mapping.items() if src is None]


def read_ads(folder):
    """Returns (rows, notes). Each row: platform, date, campaign, spend, impressions, clicks."""
    rows, notes = [], []
    for name, (platform, cols) in AD_FILES.items():
        path = Path(folder) / name
        if not path.exists():
            notes.append(f"{name} not found; {platform} is left out.")
            continue
        raw, missing = _read(path, cols)
        if missing:
            notes.append(f"{name} is missing columns: {', '.join(missing)}.")
        for r in raw:
            rows.append({"platform": platform, "date": to_date(r["date"]), "date_text": r["date"],
                         "campaign": r["campaign"], "spend": to_number(r["spend"]),
                         "impressions": to_number(r["impressions"]), "clicks": to_number(r["clicks"]), "file": name})
    return rows, notes


def read_leads(folder):
    path = Path(folder) / LEADS_FILE
    if not path.exists():
        return [], [f"{LEADS_FILE} not found; leads and stages can't be reported."]
    raw, missing = _read(path, LEAD_COLUMNS)
    notes = [f"{LEADS_FILE} is missing columns: {', '.join(missing)}."] if missing else []
    for r in raw:
        r["created"] = to_date(r["created"])
        for s in ("mql_date", "sal_date", "sql_date"):
            r[s] = to_date(r[s])
        r["email"] = r["email"].lower()
        r["utm_source"], r["utm_medium"] = r["utm_source"].lower(), r["utm_medium"].lower()
    return raw, notes


def read_map(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(fh)]


def read_control(path):
    """Optional control totals: channel, metric, value (e.g. from a CRM report you trust)."""
    rows = read_map(path)
    return {(r["channel"], r["metric"].lower()): to_number(r["value"]) for r in rows}


def period_label(start, end):
    """'Q3 2026 (Jul 1 - Sep 30, 2026)' for a full quarter, otherwise the date range."""
    from datetime import timedelta
    q = (start.month - 1) // 3 + 1
    q_start = date(start.year, 3 * q - 2, 1)
    q_end = (date(start.year + 1, 1, 1) if q == 4 else date(start.year, 3 * q + 1, 1)) - timedelta(days=1)
    rng = f"{start:%b} {start.day} – {end:%b} {end.day}, {end.year}"
    return f"Q{q} {start.year} ({rng})" if (start, end) == (q_start, q_end) else rng
