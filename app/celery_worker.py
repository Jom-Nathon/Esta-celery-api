from celery import Celery
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from app.core.config import settings
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from functools import wraps
import json

from app.models.plot import Plot
from app.db.database import get_session

celery = Celery(
    "plot_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery Configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_timeout=10,  # Add timeout
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=3,
    worker_prefetch_multiplier=1,  # Reduce if tasks are heavy
    task_acks_late=True,  # Only acknowledge after task completion
    worker_concurrency=2  # Adjust based on your CPU cores
)

def retry_on_exception(retries, delay):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try :
                    return func(*args, **kwargs)
                except (TimeoutException, StaleElementReferenceException) as e:
                    if attempt == retries - 1 :  # Last attempt
                        print(f"Failed after {retries} attempts. Error: {e}")
                        raise  # Re-raise the last exception
                    print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                    sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_exception(3, 1)
def hasNext(driver):
    page = driver.find_element(By.XPATH, "/html/body/div[4]/div/div[2]/table[1]/tbody/tr/td[2]/div")
    currPage, lastPage = (page.text).replace("หน้าที่ ","").split("/")
    print(f"{currPage}, {lastPage}")
    if currPage != lastPage:
        navigationEle = driver.find_element(By.CSS_SELECTOR, "[aria-label=pagenext]")
        navElements = navigationEle.find_elements(By.XPATH, ".//ul/li")

        if len(navElements) >= 2:
            nextPageBtn = navElements[-2]
        return True, nextPageBtn

    return False, None

@retry_on_exception(3, 1)
def safe_click_next(driver, next_btn):
    next_btn.click()
    wait = WebDriverWait(driver, 10)
    wait.until(expected_conditions.staleness_of(next_btn))
    return True

@retry_on_exception(3, 1)
def searchFor(driver, area):
    capchaInputEle = driver.find_element(By.ID, 'pass')
    confirmEle = driver.find_element(By.ID, 'GFG_Button')
    capchaEle = driver.find_element(By.XPATH, '/html/body/div[4]/div/div[1]/table/tbody/tr[1]/td[1]/strong/font/font')
    capchaInputEle.send_keys(capchaEle.text)
    regionEle = driver.find_element(By.NAME, 'region_name')
    ActionChains(driver)\
        .send_keys_to_element(regionEle, area)\
        .send_keys(Keys.ENTER)\
        .perform()

    confirmEle.click()
    print("redirecting...")

@retry_on_exception(3, 1)
def cardScrape(driver, link):
    original_window = driver.current_window_handle
    link.click()
    wait.until(EC.number_of_windows_to_be(2))
    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: driver.current_url != "https://asset.led.go.th/newbidreg/")
    chrome_options = webdriver.ChromeOptions()
    settings = {
    "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
    prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--kiosk-printing')
    CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=CHROMEDRIVER_PATH)

@celery.task
def getPlotInfo(area): 

    driver = None
    session = next(get_session())  # Get database session

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.page_load_strategy = 'normal'
    # options.add_experimental_option("detach", True)

    driver = webdriver.Remote(command_executor = "http://localhost:4444", options = options)
    driver.get('https://asset.led.go.th/newbidreg/')

    searchFor(driver, area)

    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: driver.current_url != "https://asset.led.go.th/newbidreg/")

    page_number = 1
    
    while True:
        try:
            jsonPlot = []
            print(f"Processing page {page_number}")
            wait = WebDriverWait(driver, 10)
            allPlotEle = driver.find_elements(By.XPATH, "//*[@id='box-table-a']/table/tbody/tr")
            
            for plot in allPlotEle:
                plotTableInfo = plot.find_elements(By.XPATH, ".//td")
                lot = plotTableInfo[0].text
                saleOrder = plotTableInfo[1].text
                case = plotTableInfo[2].text
                type = plotTableInfo[3].text
                size = (f"{plotTableInfo[4].text}/{plotTableInfo[5].text}/{plotTableInfo[6].text}")
                price = plotTableInfo[7].text
                district = plotTableInfo[8].text
                subDistrict = plotTableInfo[9].text
                province = plotTableInfo[10].text
                isAvailable = plot.get_attribute("bgcolor") == "#FEE6E6"

                new_plot = Plot(
                    lot = lot.strip(),
                    saleOrder = saleOrder.strip(),
                    case = case.strip(),
                    type = type.strip(),
                    size = size.strip(),
                    price = float(price.replace(',', '').replace(' ', '')),
                    district = district.strip(),
                    subDistrict = subDistrict.strip(),
                    province = province.strip(),
                    created_at = datetime.now(),
                    isAvailable = isAvailable
                )
                session.add(new_plot)
                session.commit()

            has_next, next_btn = hasNext(driver)
            if not has_next:
                print("Reached last page")
                break
                
            # Try to click next with retry mechanism
            if safe_click_next(driver, next_btn):
                page_number += 1
            else:
                print("Failed to navigate to next page")
                break
                
        except Exception as e:
            print(f"Unexpected error on page {page_number}: {str(e)}")

    print(f"Done looping! Processed {page_number} pages")
    session.close()

    return jsonPlot
