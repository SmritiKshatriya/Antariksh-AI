from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import csv

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

try:
    wait = WebDriverWait(driver, 30)
    driver.get("https://www.mosdac.gov.in")
    print("🌐 MOSDAC homepage loaded")

    # Hover over "Catalog"
    catalog_menu = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Catalog')]")))
    print("🖱️ Hovering over 'Catalog' tile...")
    actions = ActionChains(driver)
    actions.move_to_element(catalog_menu).perform()

    # Click Satellite under dropdown
    satellite_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Satellite")))
    print("📡 Clicking on 'Satellite' link...")
    satellite_link.click()

    # ✅ Step 2: Language selection
    try:
        lang_dropdown = wait.until(EC.presence_of_element_located((By.ID, "lang-dropdown-select-language_content")))
        Select(lang_dropdown).select_by_visible_text("English")
        print("🌐 Language selected: English")

        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Submit']")))
        submit_btn.click()
        print("➡️ Submitted language form")

        # Wait for satellite dropdown to load
        wait.until(EC.presence_of_element_located((By.XPATH, "//select[contains(@name, 'satellite')]")))
        print("🛰️ Satellite dropdown loaded")

    except TimeoutException:
        print("ℹ️ Language selection not required. Waiting for catalog page...")
        wait.until(EC.presence_of_element_located((By.XPATH, "//select[contains(@name, 'satellite')]")))
        print("🛰️ Satellite dropdown loaded")

    # ✅ Step 3: Access dropdowns
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"🔍 Found {len(selects)} <select> elements")
    for i, sel in enumerate(selects):
        print(f"   [{i}] name={sel.get_attribute('name')}, id={sel.get_attribute('id')}")

    if len(selects) < 2:
        raise Exception("Not enough <select> dropdowns found to proceed.")

    satellite_select = Select(selects[0])
    sensor_select = Select(selects[1])

    # ✅ Step 4: Save data
    with open("scraper/satellite_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Satellite", "Sensor", "Product", "Resolution", "File Format", "Temporal Frequency", "Description"])

        for sat_option in satellite_select.options:
            satellite = sat_option.text.strip()
            if satellite == "Select Satellite":
                continue
            satellite_select.select_by_visible_text(satellite)
            time.sleep(1)

            for sen_option in sensor_select.options:
                sensor = sen_option.text.strip()
                if sensor == "Select Sensor":
                    continue
                sensor_select.select_by_visible_text(sensor)
                print(f"🔄 Fetching for Satellite: {satellite}, Sensor: {sensor}")
                time.sleep(2)

                try:
                    wait.until(EC.presence_of_element_located((By.ID, "tabledata")))
                    rows = driver.find_elements(By.CSS_SELECTOR, "#tabledata tbody tr")

                    if not rows:
                        print(f"⚠️ No data found for {satellite}-{sensor}")
                        continue

                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 6:
                            data = [satellite, sensor] + [cell.text.strip() for cell in cells[:5]]
                            writer.writerow(data)

                except TimeoutException:
                    print(f"⏱️ Timeout for {satellite}-{sensor}, skipping...")

except Exception as e:
    print(f"❌ Scraping failed: {e}")

finally:
    driver.quit()
    print("✅ Scraping finished.")
