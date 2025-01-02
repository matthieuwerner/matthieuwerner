import os
import random
import datetime
from github import Github

# Récupération du token GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN non défini. Vérifiez les secrets de votre workflow.")

# Connectez-vous avec PyGithub
g = Github(GITHUB_TOKEN)
repo_name = "matthieuwerner/matthieuwerner"  # Remplacez par votre dépôt

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

# Récupérer une œuvre d'art aléatoire
def fetch_random_met_artwork():
    import requests
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
                "year": artwork.get("objectDate", "Date inconnue"),
            }
    return {
        "title": "Œuvre inconnue",
        "image": "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg",
        "artist": "Artiste inconnu",
        "year": "Date inconnue",
    }

# Générer le contenu SVG
def generate_svg(season, commits):
    themes = {
        "spring": "🌸",
        "summer": "🌞",
        "autumn": "🍂",
        "winter": "❄️",
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

# Script principal
def main():
    print("Script started...")
    season = get_season()
    print(f"Current season: {season}")

    repo = g.get_repo(repo_name)
    commits = 50  # Exemple fixe, remplacez par une fonction de récupération réelle

    svg_content = generate_svg(season, commits)

    # Écrire le fichier SVG dans la branche output
    try:
        repo.create_file(
            path="output/generated-svg.svg",
            message="Update SVG",
            content=svg_content,
            branch="output",
        )
        print("SVG file successfully created in the output branch.")
    except Exception as e:
        print(f"Error creating SVG file: {e}")

    # Ajouter un lien vers le fichier SVG dans le README
    try:
        readme = repo.get_contents("README.md", ref="main")
        updated_readme = readme.decoded_content.decode("utf-8")
        svg_url = f"https://raw.githubusercontent.com/{repo_name}/output/generated-svg.svg"

        if "<!-- SVG_LINK -->" in updated_readme:
            updated_readme = updated_readme.replace(
                "<!-- SVG_LINK -->",
                f"[![SVG Contributions](https://raw.githubusercontent.com/{repo_name}/output/generated-svg.svg)]({svg_url})",
            )
            repo.update_file(
                path=readme.path,
                message="Update README with SVG link",
                content=updated_readme,
                sha=readme.sha,
                branch="main",
            )
            print("README file successfully updated.")
    except Exception as e:
        print(f"Error updating README: {e}")

if __name__ == "__main__":
    main()
