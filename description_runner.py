from bs4 import BeautifulSoup

with open("remediate.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

descriptions = {
    "Disable the GNOME3 Login User List": "GNOME is not installed in CI runners. Rule fails by default and is not applicable.",
    "Disable XDMCP in GDM": "GDM is not used in CI environments. Rule is not relevant to headless pipelines.",
    "Disable GNOME3 Automounting": "No GUI session exists. This rule fails due to missing GNOME stack.",
    "Disable GNOME3 Automount Opening": "This setting requires a desktop environment, which is absent in the runner.",
    "Disable GNOME3 Automount running": "Fails because automounting services don't run without GNOME — not applicable.",
    "Set GNOME3 Screensaver Lock Delay After Activation Period": "Screensaver settings are irrelevant in non-interactive environments.",
    "Enable GNOME3 Screensaver Lock After Idle Period": "There is no screen to lock in CI runners. Rule is removed.",
    "Configure GNOME3 DConf User Profile": "DConf does not exist without GNOME. This rule is irrelevant in server/headless CI contexts.",

    "Uninstall avahi Server Package": "Avahi is not installed in CI runners. Rule fails due to missing package manager metadata.",
    "Disable Avahi Server Software": "Avahi is not present in the runner environment, so service-related checks fail.",
    "Uninstall rsync Package": "Rsync may be used by CI jobs or not installed at all. Rule skipped to avoid conflicts.",
    "Uninstall CUPS Package": "Printing system is not relevant in CI/CD pipelines. Rule skipped for cleaner scans.",
    "Disable the CUPS Service": "Print services don't run in GitHub Actions runners — rule fails by default.",

    "Limit Users' SSH Access": "SSH access is intentionally enabled for debugging and remote access during CI runs. Rule fails because access is not restricted to specific users."    
}

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
        new_th.string = "Why fail/error ?"
        headers[result_index].insert_after(new_th)

        # Add description to each row
        for row in table.find_all("tr")[1:]:  # Skip header row
            cols = row.find_all("td")
            if len(cols) >= result_index:
                title = cols[0].get_text(strip=True)
                desc = descriptions.get(title, "N/A")
                new_td = soup.new_tag("td")
                new_td.string = desc
                cols[result_index].insert_after(new_td)

with open("testreport_modified.html", "w", encoding="utf-8") as f:
    f.write(str(soup.prettify()))
