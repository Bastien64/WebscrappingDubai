from flask import Flask, render_template, Response
import requests
from flask import request
from bs4 import BeautifulSoup
import csv
from io import StringIO

app = Flask(__name__)

@app.route('/')
def index():
    # URL de la page à scraper
    url = 'https://edberrealestate.com/projets-neufs/'

    # Effectuer la requête HTTP
    response = requests.get(url)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Parser le contenu HTML de la page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Récupérer les textes de tous les éléments <h3 class="elementor-image-box-title">
        title_elements = soup.select('.elementor-image-box-title')
        title_texts = [element.get_text(strip=True) for element in title_elements]

        # Utiliser des CSS Selectors pour trouver les éléments
        markers = soup.select('.fas.fa-map-marker-alt')
        buildings = soup.select('.fas.fa-building')
        prices = soup.select('.fas.fa-money-bill')

        # Extraire les textes correspondants
        data = []
        for title_text, marker, building, price in zip(title_texts, markers, buildings, prices):
            location = marker.next_element.strip()
            type_appart = building.next_element.strip()
            prix = price.next_element.strip()
            data.append((title_text, location, type_appart, prix))  # Ajout de title_text ici

        # Créer un fichier CSV en mémoire
        with StringIO() as output:
            writer = csv.writer(output)
            writer.writerow(['Nom de la résidence', 'Location', 'Type d\'appartement', 'Prix'])  # Titre ajouté
            writer.writerows(data)
            output.seek(0)

            # Rendre le modèle HTML avec le bouton de téléchargement
            return render_template('index.html', csv_data=output.getvalue())
    else:
        # Si la requête a échoué, afficher un message d'erreur
        return "Erreur lors de la récupération de la page"

@app.route('/download_csv', methods=['POST'])
def download_csv():
    csv_data = request.form['csv_data']
    return Response(csv_data, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=projets_neufs.csv'})

if __name__ == '__main__':
    app.run(debug=True)
