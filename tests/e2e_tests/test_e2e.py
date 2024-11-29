from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def test_e2e_prediction():
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:5000/predict")

    # Fill out the form
    driver.find_element(By.NAME, "age").send_keys("45")
    driver.find_element(By.NAME, "hypertension").send_keys("0")
    driver.find_element(By.NAME, "heart_disease").send_keys("0")
    driver.find_element(By.NAME, "avg_glucose_level").send_keys("120.0")
    driver.find_element(By.NAME, "bmi").send_keys("22.5")

    # Submit the form
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)

    # Check the result
    assert "Prediction" in driver.page_source

    # Close the browser
    driver.quit()
