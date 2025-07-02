import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup
chrome_path = "drivers/chromedriver.exe"  # Update if needed
url = "https://mosdac.gov.in/catalog/satellite.php"
output_file = "scraper/satellite_catalog.csv"

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(executable_path=chrome_path, options=options)
driver.get(url)

try:
    wait = WebDriverWait(driver, 10)

    # Wait for dropdown to appear
    dropdown = wait.until(EC.presence_of_element_located((By.ID, "satellite_name")))
    select = Select(dropdown)

    satellites = [option.get_attribute("value") for option in select.options if option.get_attribute("value")]
    print(f"Found {len(satellites)} satellites")

    all_data = []

    for sat in satellites:
        print(f"🔄 Selecting satellite: {sat}")
        select.select_by_value(sat)

        # Wait for table data to load (table body should have rows)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main_table tbody tr")))

        rows = driver.find_elements(By.CSS_SELECTOR, "#main_table tbody tr")
        print(f"✅ {len(rows)} rows found for {sat}")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            all_data.append([sat] + [col.text.strip() for col in cols])

        time.sleep(1)  # Short delay to avoid too rapid switching

    # Save to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Satellite", "Product", "Start Date", "End Date", "Frequency", "Description"])
        writer.writerows(all_data)

    print(f"\n✅ Data saved to {output_file}")

except Exception as e:
    print("❌ Scraping failed:", str(e))

finally:
    driver.quit()
