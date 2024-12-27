import random
import requests

def fetch_random_met_artwork():
    # Endpoint API du Met
    api_base_url = "https://collectionapi.metmuseum.org/public/collection/v1"

    # Récupérer les IDs des œuvres
    response = requests.get(f"{api_base_url}/objects")
    if response.status_code != 200:
        raise Exception("Erreur lors de la récupération des œuvres du Met")
    object_ids = response.json().get("objectIDs", [])

    # Filtrer jusqu'à obtenir une œuvre avec une image
    for _ in range(10):  # Limite à 10 essais pour éviter les boucles infinies
        random_id = random.choice(object_ids)
        response = requests.get(f"{api_base_url}/objects/{random_id}")
        if response.status_code != 200:
            continue
        artwork = response.json()
        if artwork.get("primaryImage"):  # Vérifier si une image est disponible
            return {
                "title": artwork.get("title", "Œuvre inconnue"),
                "image": artwork.get("primaryImage"),
                "artist": artwork.get("artistDisplayName", "Artiste inconnu"),
                "year": artwork.get("objectDate", "Date inconnue")
            }

    # Si aucune œuvre avec image n'est trouvée, retourner une œuvre par défaut
    return {
        "title": "Œuvre inconnue",
        "image": "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg",
        "artist": "Artiste inconnu",
        "year": "Date inconnue"
    }

def generate_table(season, commits):
    themes = {
        "spring": "🌸",
        "summer": "🌞",
        "autumn": "🍂",
        "winter": "❄️"
    }

    # Récupérer une œuvre d'art du Met
    artwork = fetch_random_met_artwork()

    # Dimensions de la grille
    grid_size = 10  # Taille de la grille 10x10 (100 cases)
    total_cells = grid_size * grid_size

    # Calcul de la densité des éléments saisonniers
    theme = themes[season]
    density = min(commits // 5, total_cells)  # Ajuste la densité pour ne pas dépasser la taille de la grille

    # Générer une grille remplie de cases neutres
    grid = ["⬜"] * total_cells

    # Placer les éléments saisonniers à des positions aléatoires
    positions = random.sample(range(total_cells), density)
    for pos in positions:
        grid[pos] = theme

    # Construire la partie gauche du tableau (grille)
    left_table_html = "<table style='border-collapse: collapse; width: 100%;'>\n"
    for row in range(grid_size):
        start = row * grid_size
        end = start + grid_size
        row_html = "<tr>" + "".join(f"<td style='border: 1px solid #ccc; text-align: center;'>{cell}</td>" for cell in grid[start:end]) + "</tr>\n"
        left_table_html += row_html
    left_table_html += "</table>"

    # Construire le tableau principal avec des titres pour les colonnes
    table_html = f"""
<table style="width: 100%; border-collapse: collapse; border: 2px solid #000;">
  <tr>
    <th style="width: 70%; text-align: center; border: 2px solid #000;">Grille Saisonnière</th>
    <th style="width: 30%; text-align: center; border: 2px solid #000;">Œuvre d'Art</th>
  </tr>
  <tr>
    <td style="width: 70%; border: 2px solid #ccc;">{left_table_html}</td>
    <td style="width: 30%; text-align: center; border: 2px solid #ccc;">
      <h3>{artwork['title']}</h3>
      <p><em>{artwork['artist'] or 'Artiste inconnu'}</em>, {artwork['year'] or 'Date inconnue'}</p>
      <img src="{artwork['image']}" alt="{artwork['title']}" style="max-width: 80%; height: auto;">
    </td>
  </tr>
</table>
"""
    return table_html

def update_readme_with_table(season, commits):
    # Charger le fichier README.md
    try:
        with open("README.md", "r") as file:
            readme_content = file.read()
    except FileNotFoundError:
        raise Exception("README.md introuvable. Assurez-vous que le fichier existe.")

    # Générer le tableau
    table_content = generate_table(season, commits)

    # Définir les balises pour remplacer le contenu
    start_tag = "<!-- START_TABLE -->"
    end_tag = "<!-- END_TABLE -->"

    if start_tag not in readme_content or end_tag not in readme_content:
        raise Exception(f"Les balises {start_tag} et {end_tag} sont introuvables dans README.md.")

    # Remplacer le contenu entre les balises
    updated_readme = readme_content.split(start_tag)[0] + start_tag + "\n"
    updated_readme += table_content + "\n" + end_tag + readme_content.split(end_tag)[1]

    # Écrire le contenu mis à jour dans README.md
    with open("README.md", "w") as file:
        file.write(updated_readme)
    print("README.md mis à jour avec le tableau généré.")

# Exemple d'utilisation
if __name__ == "__main__":
    update_readme_with_table(season="winter", commits=15)
