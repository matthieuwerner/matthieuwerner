import datetime
import os
import random
from github import Github

# Récupération du token GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN non défini. Vérifiez les secrets de votre workflow.")

# Connectez-vous avec PyGithub
g = Github(GITHUB_TOKEN)

# Détecter la saison actuelle
def get_season():
    today = datetime.date.today()
    if today >= datetime.date(today.year, 3, 21) and today < datetime.date(today.year, 6, 21):
        return "spring"
    elif today >= datetime.date(today.year, 6, 21) and today < datetime.date(today.year, 9, 21):
        return "summer"
    elif today >= datetime.date(today.year, 9, 21) and today < datetime.date(today.year, 12, 21):
        return "autumn"
    else:
        return "winter"

# Récupérer le nombre de commits récents
def get_commit_count(repo_name, days=30):
    try:
        print(f"Fetching commits for repository: {repo_name}")
        repo = g.get_repo(repo_name)
        since = datetime.datetime.now() - datetime.timedelta(days=days)
        commits = repo.get_commits(since=since)
        print(f"Number of commits in the last {days} days: {commits.totalCount}")
        return commits.totalCount
    except Exception as e:
        print(f"Erreur lors de la récupération des commits : {e}")
        return 0

import requests
import random

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

def generate_table(content, season, commits):
    import random

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
    # Ajouter le tableau et le contenu principal
    return f"{table_html}\n\n{content}"

# Script principal
def main():
    print("Script started...")
    season = get_season()
    print(f"Current season: {season}")

    repo_name = "matthieuwerner/matthieuwerner"
    commits = get_commit_count(repo_name)

    # Lecture du fichier README.md.dist
    try:
        with open("README.md.dist", "r") as file:
            content = file.read()
        print("README.md.dist loaded successfully.")
    except FileNotFoundError:
        print("README.md.dist not found. Please ensure the file exists.")
        return

    # Génération du contenu encadré
    framed_content = generate_table(content, season, commits)

    # Écriture dans le fichier README.md
    try:
        with open("README.md", "w") as file:
            file.write(framed_content)
        print("README.md generated successfully.")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier README.md : {e}")

if __name__ == "__main__":
    main()
