"""
Extracts LAX monthly "Ground Transportation Monthly Report" PDFs into a
single CSV: ReportPeriod, OperatorType, Monthly_Trips.

Validates itself using the report's own internal totals:
  Total Charter = TCP + TNC
  Total Courtesy = Hotel/Motel + Private Parking + Rentcar-On Airport
  Total PSC = Scheduled Service + Shared-Ride
  Total Taxi = Taxi
  Total LAWA = FlyAway + LAX Shuttle
  COMMERCIAL TOTAL = Total Charter + Total Courtesy + Total PSC + Total Taxi + Total LAWA
  Total Vehicle Volumes = COMMERCIAL TOTAL + PRIVATE VEHICLES
"""
import sys
import re
import csv
from datetime import datetime
import pdfplumber

ROW_PATTERN = re.compile(r'^([A-Za-z][A-Za-z0-9\s/().\-]*?)\s+([\d,]+|-)\s+\S.*$')

def parse_number(s):
    if s == "-":
        return 0
    return int(s.replace(",", ""))

def get_pdf_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        if len(page.chars) > 0:
            return "\n".join(p.extract_text() for p in pdf.pages), "direct"
        import pytesseract
        all_text = []
        for p in pdf.pages:
            im = p.to_image(resolution=400)
            text = pytesseract.image_to_string(im.original, config='--psm 6')
            all_text.append(text)
        return "\n".join(all_text), "ocr"

def extract_gt_data(pdf_path):
    full_text, method = get_pdf_text(pdf_path)
    lines = [l.strip() for l in full_text.split("\n") if l.strip()]

    # Find ReportPeriod, e.g. "June 2022 Current Month Year Prior..." or standalone "June 2022"
    m = re.search(r'([A-Z][a-z]+)\s+(\d{4})\s+Current Month', full_text)
    if not m:
        m = re.search(r'^([A-Z][a-z]+)\s+(\d{4})\s*$', full_text, re.MULTILINE)
    if not m:
        raise ValueError("Could not find reporting month/year in PDF text.")
    period_dt = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%B %Y")
    report_period = period_dt.strftime("%m/%d/%Y")

    categories = {}
    for line in lines:
        row_match = ROW_PATTERN.match(line)
        if row_match:
            # Real data rows have 12 numeric tokens (Monthly, Daily Avg, Market
            # Share%, prior-year equivalents, %Change, YTD columns). Header/
            # footer text that incidentally contains 1-2 numbers (page counts,
            # the "Month Year" line) won't have anywhere near that many, so
            # require at least 6 as a safety margin against OCR noise.
            numeric_tokens = re.findall(r'[\d,]+\.?\d*%?', line)
            if len(numeric_tokens) < 6:
                continue
            label = row_match.group(1).strip()
            monthly = parse_number(row_match.group(2))
            categories[label] = monthly

    return categories, report_period, method


def validate(categories):
    checks = []
    def get(name):
        return categories.get(name)

    tcp = get("TRANSPORTATION CHARTER PARTY (TCP)")
    tnc = get("TRANSPORTATION NETWORK COMPANY (TNC)")
    total_charter = get("Total Charter")
    if None not in (tcp, tnc, total_charter):
        checks.append(("Total Charter", tcp + tnc, total_charter))

    hotel = get("HOTEL/MOTEL")
    priv_park = get("PRIVATE PARKING")
    rentcar = get("RENTCAR-ON AIRPORT")
    total_courtesy = get("Total Courtesy")
    if None not in (hotel, priv_park, rentcar, total_courtesy):
        checks.append(("Total Courtesy", hotel + priv_park + rentcar, total_courtesy))

    sched = get("SCHEDULED SERVICE")
    shared = get("SHARED-RIDE")
    total_psc = get("Total PSC")
    if None not in (sched, shared, total_psc):
        checks.append(("Total PSC", sched + shared, total_psc))

    taxi = get("TAXI")
    total_taxi = get("Total Taxi")
    if None not in (taxi, total_taxi):
        checks.append(("Total Taxi", taxi, total_taxi))

    flyaway = get("FLYAWAY")
    shuttle = get("LAX SHUTTLE")
    total_lawa = get("Total LAWA")
    if None not in (flyaway, shuttle, total_lawa):
        checks.append(("Total LAWA", flyaway + shuttle, total_lawa))

    commercial_total = get("COMMERCIAL TOTAL")
    if None not in (total_charter, total_courtesy, total_psc, total_taxi, total_lawa, commercial_total):
        checks.append(("COMMERCIAL TOTAL", total_charter + total_courtesy + total_psc + total_taxi + total_lawa, commercial_total))

    private_vehicles = get("PRIVATE VEHICLES")
    total_vehicle_volumes = get("Total Vehicle Volumes")
    if None not in (commercial_total, private_vehicles, total_vehicle_volumes):
        checks.append(("Total Vehicle Volumes", commercial_total + private_vehicles, total_vehicle_volumes))

    all_passed = True
    for name, computed, reported in checks:
        if computed != reported:
            print(f"  WARNING: {name} mismatch - computed {computed:,} vs reported {reported:,}")
            all_passed = False
    return all_passed, len(checks)


def process_one(pdf_path):
    categories, report_period, method = extract_gt_data(pdf_path)
    passed, num_checks = validate(categories)
    status = "PASSED" if passed else "FAILED"
    print(f"{pdf_path} [{method}] -> {report_period}: {len(categories)} categories, "
          f"{num_checks} validation checks {status}")
    return report_period, categories, passed


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 extract_gt_pdf.py <input_pdf> <output_csv>")
        sys.exit(1)
    pdf_path, output_path = sys.argv[1], sys.argv[2]
    report_period, categories, passed = process_one(pdf_path)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["ReportPeriod", "OperatorType", "Monthly_Trips"])
        for label, value in categories.items():
            writer.writerow([report_period, label, value])
    print(f"Wrote {len(categories)} rows to {output_path}")


if __name__ == "__main__":
    main()
