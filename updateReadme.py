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

# Générer le tableau
def generate_table(season, commits):
    themes = {
        "spring": "🌸",
        "summer": "🌞",
        "autumn": "🍂",
        "winter": "❄️"
    }
    artwork = fetch_random_met_artwork()
    grid_size = 10
    total_cells = grid_size * grid_size
    theme = themes[season]
    density = min(commits // 5, total_cells)
    grid = ["⬜"] * total_cells
    positions = random.sample(range(total_cells), density)
    for pos in positions:
        grid[pos] = theme
    left_table_html = "<table style='border-collapse: collapse; width: 100%;'>\n"
    for row in range(grid_size):
        start = row * grid_size
        end = start + grid_size
        row_html = "<tr>" + "".join(f"<td style='border: 1px solid #ccc; text-align: center;'>{cell}</td>" for cell in grid[start:end]) + "</tr>\n"
        left_table_html += row_html
    left_table_html += "</table>"
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
