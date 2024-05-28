from flask import Flask, render_template, request, flash
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  


def get_taric_codes(varukod, ursprungsland, preferensland):
    tullvarde = "1000"
    vikt = "1000"
    driver = webdriver.Chrome()
    driver.get("https://tulltaxan.tullverket.se/#!/taric/duty/calculate")

    wait = WebDriverWait(driver, 20)

    vara_input = wait.until(EC.presence_of_element_located((By.ID, "commodityCode")))
    vara_input.send_keys(varukod)
    vara_input.send_keys(Keys.RETURN)

    data_tab = wait.until(EC.element_to_be_clickable((By.ID, "btnCalculateDutyNext")))
    data_tab.click()

    tullvarde_input = wait.until(EC.presence_of_element_located((By.ID, "customsValue")))
    tullvarde_input.send_keys(tullvarde)

    vikt_input = wait.until(EC.presence_of_element_located((By.ID, "netWeight")))
    vikt_input.send_keys(vikt)

    ursprungsland_select = wait.until(EC.presence_of_element_located((By.ID, "countryCode")))
    ursprungsland_select.send_keys(ursprungsland)

    preferensland_select = wait.until(EC.presence_of_element_located((By.ID, "countryOfPreferentialOriginCode")))
    preferensland_select.send_keys(preferensland)

    time.sleep(5)

    results = []
    try:
        forhandskoder_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='preferenceCode']")))
        options = forhandskoder_dropdown.find_elements(By.TAG_NAME, "option")

        for option in options:
            value = option.get_attribute('value')
            text = option.text
            if value and text:
                extra_info = ""
                if value == "100":
                    extra_info = "No certificate required"
                elif value == "200":
                    extra_info = "Certificate of origin"
                elif value == "300":
                    extra_info = "Euro certificate"
                elif value == "400":
                    extra_info = "ATR certificate"
                elif value == "320":
                    extra_info = "Euro certificate with quota"
                elif value == "420":
                    extra_info = "ATR certificate with quota"
                results.append(f"Förmånskod: {value} - {extra_info}")
    except Exception as e:
        results.append(f"Ett fel inträffade: {e}")

    driver.quit()
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        varukod = request.form['varukod']
        ursprungsland = request.form['ursprungsland']
        preferensland = request.form['preferensland']

        if not varukod.isdigit() or len(varukod) != 10:
            flash("Varukoden måste vara exakt 10 siffror lång")
            return render_template("index.html", results= None)


        results = get_taric_codes(varukod, ursprungsland, preferensland)
        return render_template('index.html', results=results)
    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)
