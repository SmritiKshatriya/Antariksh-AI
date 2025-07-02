from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import csv

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    wait = WebDriverWait(driver, 60)
    driver.get("https://www.mosdac.gov.in")
    print("🌐 MOSDAC homepage loaded")

    # Hover and click 'Insitu (AWS)'
    catalog_menu = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Catalog')]")))
    webdriver.ActionChains(driver).move_to_element(catalog_menu).perform()
    print("🖱️ Hovering over 'Catalog'...")
    
    insitu_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Insitu (AWS)")))
    print("📡 Clicking on 'Insitu (AWS)' link...")
    insitu_link.click()

    # Wait for iframe and switch
    print("🔍 Waiting for iframe to appear...")
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
    print("🔄 Switched to iframe")

    # Save iframe HTML for debugging
    with open("scraper/iframe_debug.html", "w", encoding="utf-8") as debug_f:
        debug_f.write(driver.page_source)
    print("📝 Saved iframe HTML to scraper/iframe_debug.html (inspect this file if errors persist)")

    # Wait for any <select> dropdown to appear first
    print("🔽 Waiting for <select> elements...")
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "select")))

    # Specifically wait for station dropdown
    station_dropdown = wait.until(
        EC.presence_of_element_located((By.XPATH, "//select[contains(@name, 'station')]"))
    )
    select_station = Select(station_dropdown)

    station_options = [opt for opt in select_station.options if "Select" not in opt.text and opt.text.strip()]
    if not station_options:
        raise Exception("⚠️ No valid stations found in dropdown.")
    print(f"📍 Found {len(station_options)} stations.")

    # Save data
    with open("scraper/insitu_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["S.No", "Station", "Lat", "Lon", "Parameter", "Level", "Observation Time"])
        total_rows = 0

        for station_opt in station_options:
            station_name = station_opt.text.strip()
            print(f"➡️ Selecting station: {station_name}")
            select_station.select_by_visible_text(station_name)
            time.sleep(3)

            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tabledata tbody tr")))
                rows = driver.find_elements(By.CSS_SELECTOR, "#tabledata tbody tr")
            except TimeoutException:
                print(f"⚠️ No data for station: {station_name}")
                continue

            print(f"   ↳ Found {len(rows)} rows.")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    s_no = cells[0].text.strip()
                    lat = cells[1].text.strip()
                    lon = cells[2].text.strip()
                    param = cells[3].text.strip()
                    level = cells[4].text.strip()
                    obs_time = cells[5].text.strip()
                    writer.writerow([s_no, station_name, lat, lon, param, level, obs_time])
                    total_rows += 1

        print(f"📁 Data saved to scraper/insitu_data.csv with {total_rows} rows.")

except TimeoutException as te:
    print(f"⏱️ Timeout occurred: {te}")
except Exception as e:
    print(f"❌ Scraping failed: {e}")
finally:
    driver.quit()
    print("✅ Scraping finished.")
