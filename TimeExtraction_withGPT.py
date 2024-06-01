import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from io import StringIO
import time


def stdAbziehen(zeit_str):
    try:
        zeit_obj = pd.to_datetime(zeit_str, format='%H:%M')
        zeit_obj -= pd.Timedelta(hours=1)
        return zeit_obj.strftime('%H:%M')
    except ValueError:
        return zeit_str


# Initialize WebDriver
treiber = webdriver.Chrome()
quelle = 'https://diegebetszeiten.de/chemnitz-de-diyanet-methode/'
treiber.get(quelle)

try:
    # Wait until the radio button is clickable
    radio = WebDriverWait(treiber, 10).until(EC.element_to_be_clickable((By.ID, 'slts-calendar-gregorian')))
    print("Radio button found, attempting to click.")

    # Scroll to the radio button
    treiber.execute_script("arguments[0].scrollIntoView(true);", radio)
    time.sleep(1)  # Wait for the scroll to finish

    # Click the radio button using JavaScript
    treiber.execute_script("arguments[0].click();", radio)
    time.sleep(6)
except Exception as e:
    print(f"An error occurred: {e}")
    treiber.quit()
    exit()

html = treiber.page_source
treiber.quit()

if html:
    neuSpalte = ['0', '1', '2', '3', '4', '5', '7', '8', '9']
    neuReihe = ['Day', 'Fajr', 'Shuruk', 'Duhr', 'Asr', 'Maghrib', 'Isha']

    # Read HTML tables using pandas
    zeitTafel_df = pd.concat(pd.read_html(StringIO(html)), axis=1)
    zeitTafel_df.columns = neuSpalte
    spaltLoeschen = ['1', '2']
    zeitTafel_df = zeitTafel_df.drop(columns=spaltLoeschen)
    zeitTafel_df.columns = neuSpalte[:7]
    zeitTafel_df_mit_dst = zeitTafel_df.copy()
    zeitTafel_df_mit_dst.iloc[:, 1:] = zeitTafel_df_mit_dst.iloc[:, 1:].apply(lambda x: x.map(stdAbziehen))
    zeitTafel_df.loc[0] = neuReihe
    zeitTafel_df_mit_dst.loc[0] = neuReihe

    print("\nGebetszeiten (Normal):")
    print(zeitTafel_df)
    zeitTafel_df.to_excel('GebetszeitenStundenPlan_normal.xlsx', index=False)
    print("GebetszeitenStundenPlan_normal.xlsx'")

    print("\nGebetszeiten (Sommerzeit/Daylight):")
    print(zeitTafel_df_mit_dst)
    zeitTafel_df_mit_dst.to_excel('GebetszeitenStundenPlan_Daylight.xlsx', index=False)
    print("'GebetszeitenStundenPlan_dst.xlsx'")
else:
    print("Keine Tabellen gefunden.")
