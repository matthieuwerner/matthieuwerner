import datetime
import os
import random
import re
import requests
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
repo_name = "matthieuwerner/matthieuwerner"
g = Github(GITHUB_TOKEN)

def get_season():
    month = datetime.date.today().month
    if 3 <= month <= 5: return "spring"
    if 6 <= month <= 8: return "summer"
    if 9 <= month <= 11: return "autumn"
    return "winter"

def fetch_random_met_artwork():
    api_base_url = "https://collectionapi.metmuseum.org/public/collection/v1"
    try:
        r = requests.get(f"{api_base_url}/objects")
        object_ids = r.json().get("objectIDs", [])
        for _ in range(10):
            obj_id = random.choice(object_ids)
            artwork = requests.get(f"{api_base_url}/objects/{obj_id}").json()
            if artwork.get("primaryImage"):
                return {
                    "title": artwork.get("title", "Unknown"),
                    "image": artwork.get("primaryImage"),
                    "artist": artwork.get("artistDisplayName", "Unknown Artist"),
                    "year": artwork.get("objectDate", "n/a")
                }
    except: pass
    return {"title": "Art Piece", "artist": "Unknown", "year": "n/a", "image": ""}

def generate_svg(season):
    themes = {"spring": "🌸", "summer": "🌞", "autumn": "🍂", "winter": "❄️"}
    artwork = fetch_random_met_artwork()
    theme = themes[season]
    
    # Grille 10x10 simplifiée
    grid_elements = []
    for i in range(10):
        for j in range(10):
            content = theme if random.random() > 0.8 else "⬜"
            grid_elements.append(f"<text x='{j*40+20}' y='{i*40+20}' text-anchor='middle' dominant-baseline='middle' font-size='20'>{content}</text>")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="700" height="400" style="background-color: black; font-family: Arial;">
  <g fill="white">{"".join(grid_elements)}</g>
  <g transform="translate(420, 20)" fill="white">
    <text x="0" y="20" font-size="16">Daily Discovery 🖼️</text>
    <text x="0" y="50" font-size="14" font-style="italic">{artwork['title']}</text>
    <text x="0" y="70" font-size="12">{artwork['artist']}, {artwork['year']}</text>
    <image x="0" y="90" width="250" height="250" href="{artwork['image']}" />
  </g>
</svg>"""

def main():
    repo = g.get_repo(repo_name)
    svg_content = generate_svg(get_season())
    
    # 1. Push SVG to output branch (via API for speed)
    try:
        contents = repo.get_contents("generated-svg.svg", ref="output")
        repo.update_file(contents.path, "Update SVG", svg_content, contents.sha, branch="output")
    except:
        repo.create_file("generated-svg.svg", "Initial SVG", svg_content, branch="output")

    # 2. Update README.md from .dist
    with open("README.md.dist", "r") as f: content = f.read()
    svg_url = f"https://raw.githubusercontent.com/{repo_name}/output/generated-svg.svg"
    tag = ""
    end_tag = ""
    replacement = f"{tag}\n<p align='center'><img src='{svg_url}' alt='Daily Art'></p>\n{end_tag}"
    new_readme = re.sub(f"{tag}.*?{end_tag}", replacement, content, flags=re.DOTALL)
    
    with open("README.md", "w") as f: f.write(new_readme)

if __name__ == "__main__":
    main()
