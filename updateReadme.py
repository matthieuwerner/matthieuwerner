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
        repo = g.get_repo(repo_name)  # Nom complet du repo ex: "utilisateur/nom_du_repo"
        since = datetime.datetime.now() - datetime.timedelta(days=days)
        commits = repo.get_commits(since=since)
        print(f"Number of commits in the last {days} days: {commits.totalCount}")
        return commits.totalCount
    except Exception as e:
        print(f"Erreur lors de la récupération des commits : {e}")
        return 0

# Générer le cadre ASCII en Markdown
def generate_ascii_frame(content, season, commits):
    themes = {
        "spring": "🌸 🌳",
        "summer": "🌞 🌴",
        "autumn": "🍂 🍁",
        "winter": "❄️ 🌲"
    }
    theme = themes[season]
    density = min(commits // 5, 10)  # Ajuste la densité en fonction des commits

    # Générer le cadre
    frame_top = f"╔{'═' * 70}╗"
    frame_bottom = f"╚{'═' * 70}╝"
    theme_line = f"║ {theme * density} ║"

    # Ajouter le cadre autour du contenu
    framed_content = f"```\n{frame_top}\n{theme_line}\n{content}\n{theme_line}\n{frame_bottom}\n```"
    return framed_content

# Script principal
def main():
    print("Script started...")
    season = get_season()
    print(f"Current season: {season}")

    repo_name = "matthieuwerner/matthieuwerner"  # Remplacez par votre dépôt
    commits = get_commit_count(repo_name)

    # Lecture du fichier README
    try:
        with open("README.md", "r") as file:
            content = file.read()
        print("README.md loaded successfully.")
    except FileNotFoundError:
        print("README.md not found. Please ensure the file exists.")
        return

    # Génération du contenu encadré
    framed_content = generate_ascii_frame(content, season, commits)

    # Écriture dans le README
    try:
        with open("README.md", "w") as file:
            file.write(framed_content)
        print("README.md updated successfully.")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier README.md : {e}")

if __name__ == "__main__":
    main()
