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

def generate_table(content, season, commits):
    import random

    themes = {
        "spring": "🌸",
        "summer": "🌞",
        "autumn": "🍂",
        "winter": "❄️"
    }
    artworks = [
        "🎨 Mona Lisa",
        "🖼️ Starry Night",
        "🎭 The Scream",
        "🗿 Easter Island Moai",
        "🖌️ The Persistence of Memory"
    ]
    # Sélection aléatoire d'une œuvre d'art
    selected_artwork = random.choice(artworks)

    # Dimensions de la grille
    grid_height = 50  # Nombre de lignes
    grid_width = 10   # Nombre de colonnes
    total_cells = grid_height * grid_width

    # Calcul de la densité des éléments saisonniers
    theme = themes[season]
    density = min(commits // 5, total_cells)  # Ajuste la densité pour ne pas dépasser la taille de la grille

    # Générer une grille remplie de cases neutres
    grid = ["⬜"] * total_cells

    # Placer les éléments saisonniers à des positions aléatoires
    positions = random.sample(range(total_cells), density)
    for pos in positions:
        grid[pos] = theme

    # Construire le tableau HTML ligne par ligne
    table_html = "<table>\n"
    for row in range(grid_height):
        start = row * grid_width
        end = start + grid_width
        row_html = "<tr>" + "".join(f"<td>{cell}</td>" for cell in grid[start:end]) + "</tr>\n"
        table_html += row_html
    table_html += "</table>"

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
