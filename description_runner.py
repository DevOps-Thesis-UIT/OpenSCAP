import json
from bs4 import BeautifulSoup

with open("remediated_report.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

with open("descriptions.json", "r", encoding="utf-8") as f:
    descriptions = json.load(f)

tables = soup.find_all("table")

# Locate the table with "Title", "Severity", "Result" headers
for table in tables:
    headers = table.find_all("th")
    if not headers:
        continue

    header_texts = [h.get_text(strip=True) for h in headers]
    if "Title" in header_texts and "Result" in header_texts:
        # Add "Description" header after "Result"
        result_index = header_texts.index("Result")
        new_th = soup.new_tag("th")
        new_th.string = "Why fail/error?"
        headers[result_index].insert_after(new_th)

        # Add description to each row only if result is fail/error
        for row in table.find_all("tr")[1:]:  # Skip header row
            cols = row.find_all("td")
            if len(cols) > result_index:
                result_text = cols[result_index].get_text(strip=True).lower()
                if result_text in ("fail", "error"):
                    title = cols[0].get_text(strip=True)
                    desc = descriptions.get(title, "N/A")
                    new_td = soup.new_tag("td")
                    new_td.string = desc
                    cols[result_index].insert_after(new_td)
                else:
                    # Insert empty cell to maintain table structure
                    empty_td = soup.new_tag("td")
                    empty_td.string = ""
                    cols[result_index].insert_after(empty_td)

with open("modified_report.html", "w", encoding="utf-8") as f:
    f.write(str(soup.prettify()))
