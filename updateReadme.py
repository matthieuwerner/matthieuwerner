import datetime
import os
import random
import requests
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

# Récupérer une œuvre d'art du Met
def fetch_random_met_artwork():
    api_base_url = "https://collectionapi.metmuseum.org/public/collection/v1"
    response = requests.get(f"{api_base_url}/objects")
    if response.status_code != 200:
        raise Exception("Erreur lors de la récupération des œuvres du Met")
    object_ids = response.json().get("objectIDs", [])
    for _ in range(10):  # Limite à 10 essais
        random_id = random.choice(object_ids)
        response = requests.get(f"{api_base_url}/objects/{random_id}")
        if response.status_code != 200:
            continue
        artwork = response.json()
        if artwork.get("primaryImage"):
            return {
                "title": artwork.get("title", "Œuvre inconnue"),
                "image": artwork.get("primaryImage"),
                "artist": artwork.get("artistDisplayName", "Artiste inconnu"),
                "year": artwork.get("objectDate", "Date inconnue")
            }
    return {
        "title": "Œuvre inconnue",
        "image": "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg",
        "artist": "Artiste inconnu",
        "year": "Date inconnue"
    }

def fetch_computer_related_artworks():
    """
    Récupère une œuvre liée à l'informatique à partir de l'API du Met.
    :return: Dictionnaire contenant les informations sur l'œuvre.
    """
    api_base_url = "https://collectionapi.metmuseum.org/public/collection/v1"
    keywords = ["computer", "technology", "digital", "machine"]

    # Rechercher des œuvres pour chaque mot-clé
    for keyword in keywords:
        print(f"Recherche d'œuvres avec le mot-clé : {keyword}")
        response = requests.get(f"{api_base_url}/search", params={"q": keyword})
        if response.status_code != 200:
            raise Exception(f"Erreur lors de la recherche pour le mot-clé : {keyword}")

        object_ids = response.json().get("objectIDs", [])
        if not object_ids:
            print(f"Aucune œuvre trouvée pour le mot-clé : {keyword}")
            continue

        # Filtrer jusqu'à obtenir une œuvre avec une image
        for _ in range(10):  # Limite à 10 essais pour éviter les boucles infinies
            random_id = random.choice(object_ids)
            response = requests.get(f"{api_base_url}/objects/{random_id}")
            if response.status_code != 200:
                continue
            artwork = response.json()
            if artwork.get("primaryImage"):
                return {
                    "title": artwork.get("title", "Œuvre inconnue"),
                    "image": artwork.get("primaryImage"),
                    "artist": artwork.get("artistDisplayName", "Artiste inconnu"),
                    "year": artwork.get("objectDate", "Date inconnue")
                }

    # Si aucune œuvre n'est trouvée
    return {
        "title": "Aucune œuvre liée à l'informatique trouvée",
        "image": "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg",
        "artist": "Artiste inconnu",
        "year": "Date inconnue"
    }

# Générer le tableau
def generate_table(season, commits):
    themes = {
        "spring": "🌸",
        "summer": "🌞",
        "autumn": "🍂",
        "winter": "❄️"
    }
    artwork = fetch_random_met_artwork()
    grid_size = 10  # Taille de la grille (10x10)
    total_cells = grid_size * grid_size

    theme = themes[season]
    density = min(commits // 5, total_cells)  # Ajuste la densité

    # Générer une liste de cellules avec des cases neutres
    grid = ["⬜"] * total_cells

    # Placer des éléments saisonniers à des positions aléatoires
    positions = random.sample(range(total_cells), density)
    for pos in positions:
        grid[pos] = theme

    # Construire la grille HTML
    grid_html = "<table style='border-collapse: collapse; width: 100%; font-family: monospace;'>\n"
    for row in range(grid_size):
        start = row * grid_size
        end = start + grid_size
        row_html = "<tr>" + "".join(f"<td style='padding: 5px; text-align: center;'>{cell}</td>" for cell in grid[start:end]) + "</tr>\n"
        grid_html += row_html
    grid_html += "</table>"

    # Construire le tableau principal avec les deux colonnes
    output_html = f"""
<table style="width: 100%; border-collapse: collapse;">
  <tr>
    <td style="width: 70%; vertical-align: top; padding-right: 10px;">
      <h3 style="margin-bottom: 10px;">Densité de contributions</h3>
      {grid_html}
    </td>
    <td style="width: 30%; vertical-align: top; text-align: center; padding-left: 10px;">
      <h3>Découverte du jour 🖼️</h3>
      <p><em>{artwork['title']}</em></p>
      <p>{artwork['artist'] or "Artiste inconnu"}, {artwork['year'] or "Date inconnue"}</p>
      <img src="{artwork['image']}" alt="{artwork['title']}" style="max-width: 80%; height: auto; margin-top: 10px;">
    </td>
  </tr>
</table>
"""
    return output_html

# Mettre à jour le README avec des balises dédiées
def update_readme_with_table(season, commits):
    try:
        with open("README.md.dist", "r") as file:
            readme_content = file.read()
    except FileNotFoundError:
        raise Exception("README.md.dist introuvable.")
    start_tag = "<!-- START_TABLE -->"
    end_tag = "<!-- END_TABLE -->"
    if start_tag not in readme_content or end_tag not in readme_content:
        raise Exception(f"Les balises {start_tag} et {end_tag} sont introuvables dans README.md.dist.")
    table_content = generate_table(season, commits)
    updated_readme = readme_content.split(start_tag)[0] + start_tag + "\n"
    updated_readme += table_content + "\n" + end_tag + readme_content.split(end_tag)[1]
    with open("README.md", "w") as file:
        file.write(updated_readme)
    print("README.md mis à jour avec le tableau généré.")

# Script principal
def main():
    print("Script started...")
    season = get_season()
    print(f"Current season: {season}")
    repo_name = "matthieuwerner/matthieuwerner"
    commits = get_commit_count(repo_name)
    update_readme_with_table(season, commits)

if __name__ == "__main__":
    main()
