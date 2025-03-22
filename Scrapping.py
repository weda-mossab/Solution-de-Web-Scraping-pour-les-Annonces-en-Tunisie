from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd
from bs4 import BeautifulSoup

# Configurer Selenium avec Chrome
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(120)
driver.implicitly_wait(10)

# Définition des URLs pour Vente et Location
urls = {
    "Vente": "https://www.mubawab.tn/fr/ct/tunis/immobilier-a-vendre:p:{}",
    "Location": "https://www.mubawab.tn/fr/ct/tunis/immobilier-a-louer:p:{}"
}

# Liste pour stocker toutes les annonces
annonces_list = []

# Boucle sur Vente et Location
for type_annonce, base_url in urls.items():
    print(f"Scraping les annonces de {type_annonce}...")

    # Charger la première page pour récupérer le nombre total de pages
    driver.get(base_url.format(1))
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Trouver le nombre total de pages
    try:
        total_pages = int(soup.select_one("#lastPageSpan").text.strip())
        print(f"Nombre total de pages pour {type_annonce} : {total_pages}")
    except:
        total_pages = 1  

    # Boucle sur toutes les pages
    for page in range(1, total_pages + 1):
        print(f"Scraping page {page}/{total_pages} pour {type_annonce}...")

        driver.get(base_url.format(page))
        time.sleep(5)  

        # Scroll automatique pour charger toutes les annonces
        for _ in range(5):  
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # Sélectionner les annonces
        annonces = soup.select("div.listingBox.feat, div.listingBox")

        for annonce in annonces:
            titre = annonce.select_one("h2.listingTit a")
            prix = annonce.select_one("span.priceTag")
            localisation = annonce.select_one("span.listingH3")
            superficie = annonce.select("div.adDetailFeature span")[0] if len(annonce.select("div.adDetailFeature span")) > 0 else None
            nb_pieces = annonce.select("div.adDetailFeature span")[1] if len(annonce.select("div.adDetailFeature span")) > 1 else None
            nb_chambres = annonce.select("div.adDetailFeature span")[2] if len(annonce.select("div.adDetailFeature span")) > 2 else None
            nb_sdb = annonce.select("div.adDetailFeature span")[3] if len(annonce.select("div.adDetailFeature span")) > 3 else None
            lien = annonce.select_one("h2.listingTit a")["href"] if annonce.select_one("h2.listingTit a") else None

            annonce_data = {
                "Type": type_annonce,  # Ajout du type d'annonce
                "Titre": titre.text.strip() if titre else "N/A",
                "Prix": prix.text.strip() if prix else "N/A",
                "Localisation": localisation.text.strip() if localisation else "N/A",
                "Superficie": superficie.text.strip() if superficie else "N/A",
                "Pièces": nb_pieces.text.strip() if nb_pieces else "N/A",
                "Chambres": nb_chambres.text.strip() if nb_chambres else "N/A",
                "Salles de bain": nb_sdb.text.strip() if nb_sdb else "N/A",
                "Lien": f"https://www.mubawab.tn{lien}" if lien else "N/A",
            }
            
            # Vérifie si l'annonce contient un titre et un prix avant de l'ajouter
            if titre and prix:
                annonces_list.append(annonce_data)

driver.quit()

# Vérification des résultats
print(f"{len(annonces_list)} annonces extraites ✅")

# Sauvegarde en fichier Excel
df = pd.DataFrame(annonces_list)
df.to_excel("Mubawab_Annonces.xlsx", index=False)

print("Fichier Excel généré ✅")
