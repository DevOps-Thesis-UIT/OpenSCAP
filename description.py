import argparse
from bs4 import BeautifulSoup
import re

# -------- Argument Parsing --------
parser = argparse.ArgumentParser(description="Extract descriptions from HTML report")
parser.add_argument("input_file", help="Path to input HTML file")
parser.add_argument("output_file", help="Path to output HTML file")
args = parser.parse_args()

input_file = args.input_file
output_file = args.output_file

# -------- Description Extraction Function --------
def extract_description(rule_detail):
    detail_table = rule_detail.find("table")
    if not detail_table:
        return None

    for tr in detail_table.find_all("tr"):
        td_first = tr.find("td")
        if td_first and "Description" in td_first.get_text(strip=True):
            all_tds = tr.find_all("td")
            if len(all_tds) > 1:
                desc_cell = all_tds[1]
                desc_div = desc_cell.find("div", class_="description")
                if desc_div:
                    desc_text = ""
                    for p in desc_div.find_all("p"):
                        desc_text += p.get_text(strip=True) + " "
                    return desc_text.strip()[:500]
    return None

# -------- Main Processing --------
print(f"[INFO] Reading file: {input_file}")
with open(input_file, "r", encoding="utf-8") as file:
    html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")

all_rule_details = soup.find_all("div", class_="rule-detail")
rule_details_dict = {}

print(f"[INFO] Found {len(all_rule_details)} rule details in the HTML file")
for rule_detail in all_rule_details:
    rule_id_element = rule_detail.find("td", class_="rule-id")
    if rule_id_element:
        rule_id = rule_id_element.get_text(strip=True)
        rule_details_dict[rule_id] = rule_detail
        short_rule_id = rule_id.split("_")[-1] if "_" in rule_id else rule_id
        rule_details_dict[short_rule_id] = rule_detail

print(f"[INFO] Created mapping for {len(rule_details_dict)} rule details")

tables = soup.find_all("table")
found_overview_table = False

for table in tables:
    headers = table.find_all("th")
    if not headers:
        continue

    header_texts = [h.get_text(strip=True).lower() for h in headers]
    if "title" in header_texts and "result" in header_texts:
        print("[INFO] Found table containing rule overview")
        found_overview_table = True

        title_index = header_texts.index("title")
        result_index = header_texts.index("result")

        new_th = soup.new_tag("th")
        new_th.string = "Why fail/error?"
        headers[result_index].insert_after(new_th)

        rows = table.find_all("tr")[1:]
        success_count = 0
        fail_count = 0
        error_count = 0
        found_desc_count = 0

        for i, row in enumerate(rows):
            cols = row.find_all("td")
            if len(cols) <= result_index:
                continue

            rule_title = cols[title_index].get_text(strip=True)
            result = cols[result_index].get_text(strip=True).lower()

            if "fail" in result:
                fail_count += 1
            elif "error" in result:
                error_count += 1
            else:
                success_count += 1

            if "fail" not in result and "error" not in result:
                new_td = soup.new_tag("td")
                new_td.string = "—"
                cols[result_index].insert_after(new_td)
                continue

            reason = "Description not found"
            found_match = False

            link_elements = cols[title_index].find_all("a")
            for link in link_elements:
                if link.has_attr("href"):
                    href = link["href"].lstrip("#")
                    if href:
                        rule_detail_div = soup.find(id=href)
                        if rule_detail_div and "rule-detail" in rule_detail_div.get("class", []):
                            description = extract_description(rule_detail_div)
                            if description:
                                reason = description
                                found_desc_count += 1
                                found_match = True
                                break

            if not found_match:
                normalized_title = rule_title.lower().replace(" ", "").strip()
                for rule_detail in all_rule_details:
                    title_element = rule_detail.find("h3", class_="panel-title")
                    if title_element:
                        detail_title = title_element.get_text(strip=True)
                        if normalized_title == detail_title.lower().replace(" ", "").strip():
                            description = extract_description(rule_detail)
                            if description:
                                reason = description
                                found_desc_count += 1
                                break

            new_td = soup.new_tag("td")
            new_td.string = reason
            cols[result_index].insert_after(new_td)

        print(f"[INFO] Summary: {fail_count} fail, {error_count} error, {success_count} success")
        print(f"[INFO] Found descriptions for {found_desc_count}/{fail_count + error_count} failed/error rules")
        break

if not found_overview_table:
    print("[ERROR] Could not find the rule overview table!")

print(f"[INFO] Writing results to file: {output_file}")
with open(output_file, "w", encoding="utf-8") as out:
    out.write(str(soup))
print("✅ Done.")
