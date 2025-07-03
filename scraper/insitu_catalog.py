from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time
import os

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    wait = WebDriverWait(driver, 30)
    driver.get("https://www.mosdac.gov.in")
    print("🌐 MOSDAC homepage loaded")

    # Hover over 'Catalog'
    catalog_menu = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Catalog')]")))
    ActionChains(driver).move_to_element(catalog_menu).perform()
    print("🖱️ Hovering over 'Catalog'...")

    # Click on 'Insitu (AWS)'
    insitu_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Insitu (AWS)")))
    print("📡 Clicking on 'Insitu (AWS)' link...")
    insitu_link.click()

    # Switch to iframe
    print("🔍 Waiting for iframe to appear...")
    iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    driver.switch_to.frame(iframe)
    print("🔄 Switched to iframe")

    # Debug: Save initial iframe HTML
    os.makedirs("scraper", exist_ok=True)
    with open("scraper/iframe_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("📝 Saved iframe HTML to scraper/iframe_debug.html")

    # Locate and select 'Latest' from dropdown with JS event dispatch
    print("🔽 Listing <select> elements to find one with 'Latest'...")
    all_selects = driver.find_elements(By.TAG_NAME, "select")
    frame_dropdown = None

    for idx, sel in enumerate(all_selects):
        options = [opt.text.strip() for opt in sel.find_elements(By.TAG_NAME, "option")]
        print(f"\n🔢 Dropdown {idx}: {options}")
        if "Latest" in options:
            frame_dropdown = Select(sel)
            frame_dropdown.select_by_visible_text("Latest")
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", sel)
            print(f"✅ Selected 'Latest' from dropdown {idx} with JS event triggered.")
            time.sleep(3)  # Allow time for JS to update the DOM
            break

    if not frame_dropdown:
        raise Exception("❌ 'Latest' dropdown not found")

    # Save updated HTML after selecting "Latest"
    with open("scraper/iframe_after_latest.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("📝 Saved iframe HTML after selecting 'Latest'")

    # Wait for data table rows with retry
    print("🔍 Waiting for data table rows to load...")
    success = False
    rows = []
    for attempt in range(15):
        rows = driver.find_elements(By.CSS_SELECTOR, "#tabledata tbody tr")
        if rows:
            print(f"✅ Found {len(rows)} rows on attempt {attempt + 1}")
            success = True
            break
        print(f"⏳ Attempt {attempt + 1}/15: Rows not loaded yet...")
        time.sleep(2)

    if not success:
        raise TimeoutException("⏱️ Timeout: Table rows did not load.")

    # Save to CSV
    csv_file = "scraper/insitu_data.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["S.No", "Station", "Lat", "Lon", "Parameter", "Level", "Observation Time"])
        total_rows = 0
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 6:
                s_no = cells[0].text.strip()
                lat = cells[1].text.strip()
                lon = cells[2].text.strip()
                param = cells[3].text.strip()
                level = cells[4].text.strip()
                obs_time = cells[5].text.strip()
                writer.writerow([s_no, "NA", lat, lon, param, level, obs_time])
                total_rows += 1

    print(f"📁 Data saved to {csv_file} with {total_rows} rows.")

except TimeoutException as te:
    print(f"⏱️ Timeout occurred: {te}")
except Exception as e:
    print(f"❌ Scraping failed: {e}")
finally:
    driver.quit()
    print("✅ Scraping finished.")
