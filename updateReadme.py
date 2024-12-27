import datetime
from github import Github

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
    # Connectez-vous avec votre token GitHub
    g = Github("YOUR_GITHUB_TOKEN")  # Remplacez YOUR_GITHUB_TOKEN par un secret GitHub Action
    repo = g.get_repo(repo_name)  # Remplacez "repo_name" par votre dépôt (exemple: "user/repo")
    since = datetime.datetime.now() - datetime.timedelta(days=days)
    commits = repo.get_commits(since=since)
    return commits.totalCount

# Générer le cadre ASCII en Markdown
def generate_ascii_frame(content, season, commits):
    themes = {
        "spring": "🌸 🌳",
        "summer": "🌞 🌴",
        "autumn": "🍂 🍁",
        "winter": "❄️ 🌲"
    }
    theme = themes[season]
    density = min(commits // 5, 10)  # Ajuste la densité en fonction des commits (5 commits = 1 densité)

    # Générer le cadre
    frame_top = f"╔{'═' * 70}╗"
    frame_bottom = f"╚{'═' * 70}╝"
    theme_line = f"║ {theme * density} ║"

    # Ajouter le cadre autour du contenu
    framed_content = f"```\n{frame_top}\n{theme_line}\n{content}\n{theme_line}\n{frame_bottom}\n```"
    return framed_content

# Script principal
def main():
    season = get_season()
    repo_name = "user/repo"  # Remplacez "user/repo" par votre dépôt
    commits = get_commit_count(repo_name)

    with open("README.md", "r") as file:
        content = file.read()

    framed_content = generate_ascii_frame(content, season, commits)

    # Écrire dans le README
    with open("README.md", "w") as file:
        file.write(framed_content)

if __name__ == "__main__":
    main()
