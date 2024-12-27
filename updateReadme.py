
import datetime
import os
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

def generate_ascii_frame(content, season, commits):
    themes = {
        "spring": "🌸🌳",
        "summer": "🌞🌴",
        "autumn": "🍂🍁",
        "winter": "❄️🌲"
    }
    theme = themes[season]
    density = min(commits // 5, 10)  # Ajuste la densité en fonction des commits

    # Configuration de la largeur du cadre
    frame_width = 70  # Largeur fixe du cadre (modifiable)
    content_lines = content.split("\n")

    # Générer la ligne des thèmes centrée
    theme_line_content = (theme * density).strip()  # Créer le thème répété
    theme_line_length = len(theme_line_content)
    padding_left = (frame_width - theme_line_length) // 2
    padding_right = frame_width - theme_line_length - padding_left
    theme_line = f"║{' ' * padding_left}{theme_line_content}{' ' * padding_right}║"

    # Générer les lignes du cadre
    frame_top = f"╔{'═' * frame_width}╗"
    frame_bottom = f"╚{'═' * frame_width}╝"

    # Ajouter chaque ligne du contenu avec un alignement propre
    framed_content = f"{frame_top}\n{theme_line}\n"
    for line in content_lines:
        truncated_line = line[:frame_width]  # Tronquer les lignes trop longues
        padded_line = truncated_line.ljust(frame_width)
        framed_content += f"║{padded_line}║\n"
    framed_content += f"{theme_line}\n{frame_bottom}"

    return framed_content

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
    framed_content = generate_ascii_frame(content, season, commits)

    # Écriture dans le fichier README.md
    try:
        with open("README.md", "w") as file:
            file.write(framed_content)
        print("README.md generated successfully.")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier README.md : {e}")

if __name__ == "__main__":
    main()
