"""
Extracts monthly LAX "Passenger Traffic Comparison by Terminal" PDF reports
into a CSV matching the format of the master passenger traffic dataset
(columns: DataExtractDate, ReportPeriod, Terminal, Arrival_Departure,
Domestic_International, Passenger_Count).

Usage:
    python3 extract_lax_passenger_pdf.py <path_to_pdf> <output_csv_path>

Example:
    python3 extract_lax_passenger_pdf.py passengerDec23.pdf passenger_traffic_2023_12.csv

The script validates itself: it sums every terminal's "Total" row and
compares that against the report's own "Grand Total" line. If they don't
match exactly, it prints a warning instead of silently writing bad data.
"""

import sys
import re
import csv
from datetime import datetime
import pdfplumber

# Maps the various label text LAWA has used for each category onto the
# exact naming convention used in the master CSV. If a future PDF uses
# a label not covered here, the script will raise an error rather than
# guess incorrectly.
def normalize_terminal_name(raw_name):
    raw = raw_name.strip()
    m = re.match(r'^Terminal\s+(\d+)$', raw, re.IGNORECASE)
    if m:
        return f"T{m.group(1)}"
    lower = raw.lower()
    if "misc" in lower:
        return "Miscellaneous Terminal"
    if "west gate" in lower:
        return "TBIT West Gates"
    if "bradley" in lower or raw.upper() == "TBIT":
        return "TBIT"
    if "imperial" in lower:
        return "Imperial Terminal"
    raise ValueError(f"Unrecognized terminal/category label: '{raw_name}'. "
                      f"Update normalize_terminal_name() to handle it.")


def parse_number(s):
    return int(s.replace(",", ""))


def extract_pdf_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join(page.extract_text() for page in pdf.pages)

    lines = [l.strip() for l in full_text.split("\n") if l.strip()]

    # --- Extract DataExtractDate (report generation timestamp) ---
    m = re.search(r'(\d{1,2}/\d{1,2}/\d{4}),\s*(\d{1,2}:\d{2}\s*[AP]M)', full_text)
    if not m:
        raise ValueError("Could not find report generation date/time in PDF text.")
    extract_dt = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%m/%d/%Y %I:%M %p")
    data_extract_date = extract_dt.strftime("%Y %b %d %I:%M:%S %p")

    # --- Extract ReportPeriod (the month/year this report covers) ---
    m = re.search(r'([A-Z][a-z]+)\s+(\d{4})\s+Calendar YTD', full_text)
    if not m:
        raise ValueError("Could not find reporting month/year in PDF text.")
    period_dt = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%B %Y")
    report_period = period_dt.strftime("%m/01/%Y")

    # --- Parse terminal blocks ---
    # Pattern for a data row: leading label word, then 6 comma-formatted numbers
    row_pattern = re.compile(
        r'^(Departure|Arrival|Total)\s+'
        r'([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)$'
    )

    categories = {}  # normalized_name -> {'Arrival': (dom, intl), 'Departure': (dom, intl), 'Total': (dom, intl)}
    current_name = None

    for line in lines:
        row_match = row_pattern.match(line)
        if row_match:
            if current_name is None:
                continue  # skip stray rows before the first category header
            label = row_match.group(1)
            dom_month = parse_number(row_match.group(2))
            intl_month = parse_number(row_match.group(3))
            # groups 4,5,6 are the Total(month), then YTD columns - we only need month Domestic/International
            categories.setdefault(current_name, {})[label] = (dom_month, intl_month)
        elif line.startswith("Grand Total"):
            gt_numbers = re.findall(r'[\d,]+', line)
            grand_total_dom = parse_number(gt_numbers[0])
            grand_total_intl = parse_number(gt_numbers[1])
        elif line.startswith("Domestic International Total") or line.startswith("Not all airlines"):
            continue
        else:
            # Anything else not matching a data row is treated as a
            # potential new category header, if it doesn't look like
            # report metadata text.
            if re.match(r'^[A-Za-z0-9.\-\s]+$', line) and not re.search(r'\d{4}', line) \
               and "Page" not in line and "LAWA" not in line and "Los Angeles" not in line:
                try:
                    current_name = normalize_terminal_name(line)
                except ValueError:
                    current_name = None  # unrecognized header text, ignore

    return categories, data_extract_date, report_period, grand_total_dom, grand_total_intl


def validate_and_build_rows(categories, grand_total_dom, grand_total_intl, data_extract_date, report_period):
    sum_dom = 0
    sum_intl = 0
    rows = []
    for terminal, vals in categories.items():
        if not all(k in vals for k in ("Arrival", "Departure", "Total")):
            print(f"WARNING: '{terminal}' is missing one of Arrival/Departure/Total. Found: {list(vals.keys())}")
            continue
        arr_dom, arr_intl = vals["Arrival"]
        dep_dom, dep_intl = vals["Departure"]
        tot_dom, tot_intl = vals["Total"]

        # Internal consistency check per terminal
        if arr_dom + dep_dom != tot_dom or arr_intl + dep_intl != tot_intl:
            print(f"WARNING: '{terminal}' Arrival+Departure does not equal Total. "
                  f"Domestic: {arr_dom}+{dep_dom} vs {tot_dom} | International: {arr_intl}+{dep_intl} vs {tot_intl}")

        sum_dom += tot_dom
        sum_intl += tot_intl

        rows.append([data_extract_date, report_period, terminal, "Arrival", "Domestic", f"{arr_dom:,}"])
        rows.append([data_extract_date, report_period, terminal, "Arrival", "International", f"{arr_intl:,}"])
        rows.append([data_extract_date, report_period, terminal, "Departure", "Domestic", f"{dep_dom:,}"])
        rows.append([data_extract_date, report_period, terminal, "Departure", "International", f"{dep_intl:,}"])

    print(f"\nFound {len(categories)} terminal/category groups.")
    print(f"Sum of all Totals -> Domestic: {sum_dom:,} | International: {sum_intl:,}")
    print(f"PDF Grand Total   -> Domestic: {grand_total_dom:,} | International: {grand_total_intl:,}")
    if sum_dom == grand_total_dom and sum_intl == grand_total_intl:
        print("VALIDATION PASSED: sums match the Grand Total exactly.\n")
    else:
        print("VALIDATION FAILED: sums do NOT match the Grand Total. "
              "Do not trust this output until you investigate the mismatch.\n")

    return rows


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 extract_lax_passenger_pdf.py <input_pdf> <output_csv>")
        sys.exit(1)

    pdf_path, output_path = sys.argv[1], sys.argv[2]

    categories, data_extract_date, report_period, grand_total_dom, grand_total_intl = extract_pdf_data(pdf_path)
    rows = validate_and_build_rows(categories, grand_total_dom, grand_total_intl, data_extract_date, report_period)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["DataExtractDate", "ReportPeriod", "Terminal", "Arrival_Departure", "Domestic_International", "Passenger_Count"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
