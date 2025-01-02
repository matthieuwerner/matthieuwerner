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
repo_name = "matthieuwerner/matthieuwerner"

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
    for _ in range(10):
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

# Générer le contenu SVG
def generate_svg(season, commits):
    themes = {
        "spring": "🌸",
        "summer": "🌞",
        "autumn": "🍂",
        "winter": "❄️"
    }
    artwork = fetch_random_met_artwork()
    grid_size = 10
    cell_size = 40

    theme = themes[season]
    density = min(commits // 5, grid_size * grid_size)
    grid = ["⬜"] * (grid_size * grid_size)
    positions = random.sample(range(grid_size * grid_size), density)
    for pos in positions:
        grid[pos] = theme

    grid_elements = []
    for i in range(grid_size):
        for j in range(grid_size):
            content = grid[i * grid_size + j]
            x = j * cell_size
            y = i * cell_size
            grid_elements.append(
                f"<text x='{x + cell_size / 2}' y='{y + cell_size / 2}' text-anchor='middle' dominant-baseline='middle' font-size='20'>{content}</text>"
            )

    grid_svg = "\n".join(grid_elements)
    svg_width = grid_size * cell_size + 300
    svg_height = grid_size * cell_size

    svg_output = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" style="background-color: black; font-family: Arial, sans-serif;">
  <g fill="white" transform="translate(0, 0)">
    {grid_svg}
  </g>
  <g transform="translate({grid_size * cell_size + 20}, 20)" fill="white">
    <text x="0" y="20" font-size="16" fill="white">Découverte du jour 🖼️</text>
    <text x="0" y="50" font-size="14" fill="white"><tspan font-style="italic">{artwork['title']}</tspan></text>
    <text x="0" y="70" font-size="14" fill="white">{artwork['artist']}, {artwork['year']}</text>
    <image x="0" y="90" width="200" height="200" href="{artwork['image']}" />
  </g>
</svg>
"""
    return svg_output

# Mettre à jour le fichier README et créer le fichier SVG
def update_readme_with_svg(season, commits):
    repo = g.get_repo(repo_name)

    # Générer le contenu SVG
    svg_content = generate_svg(season, commits)
    svg_path = "output/generated-svg.svg"

    # Pousser le fichier SVG sur la branche output
    try:
        repo.create_file(
            path=svg_path,
            message="Update SVG",
            content=svg_content,
            branch="output",
        )
        print(f"SVG file pushed to branch 'output': {svg_path}")
    except Exception as e:
        print(f"Error pushing SVG file: {e}")

    # Mise à jour du README
    svg_url = f"https://raw.githubusercontent.com/{repo_name}/output/generated-svg.svg"
    try:
        with open("README.md.dist", "r") as file:
            readme_content = file.read()

        start_tag = "<!-- SVG_LINK -->"
        if start_tag not in readme_content:
            raise Exception(f"Balise {start_tag} introuvable dans README.md.dist.")
        updated_readme = readme_content.replace(start_tag, f"![Generated SVG]({svg_url})")

        with open("README.md", "w") as file:
            file.write(updated_readme)
        print("README.md mis à jour avec le lien SVG.")
    except Exception as e:
        print(f"Error updating README: {e}")

# Script principal
def main():
    print("Script started...")
    season = get_season()
    print(f"Current season: {season}")
    commits = get_commit_count(repo_name)
    update_readme_with_svg(season, commits)

if __name__ == "__main__":
    main()
