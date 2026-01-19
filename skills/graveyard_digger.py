import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import json
from datetime import datetime

# --- Configuration ---
# You might need to set your API Key in environment variables or hardcode for testing
# os.environ["GOOGLE_API_KEY"] = "YOUR_KEY"

SCENE_SETTING = """
You are the "Graveyard Digger" (守墓人). 
Your job is to dig through the "fresh graves" of GitHub (Trending Repos).
You don't care about corporate polish. You care about SOUL, CHAOS, and LAZY GENIUS.
You are looking for:
1. "Shovel Sellers" (Tools that make money off the AI hype).
2. "Lazy Workflows" (Tools that automate the mundane).
3. "Wrapper Crap" (Thin wrappers around APIs - Roast them gently but firmly).
4. "Hidden Gems" (True innovation).

Output Style: Spicy, Cynical but hopeful, Cyberpunk-Noir. 
Use emojis like 💀, ⚰️, 💎, 🕯️.
"""

def fetch_github_trends(language=None):
    """
    Scrapes GitHub Trending page.
    Note: GitHub doesn't have a public API for trending, so we scrape.
    """
    url = "https://github.com/trending"
    if language:
        url += f"/{language}"
    
    print(f"🕯️ Approaching the graveyard gates: {url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"💀 Failed to enter the graveyard: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    repos = []
    
    repo_list = soup.select('article.Box-row')
    
    for item in repo_list:
        try:
            # Title (User/Repo)
            title_tag = item.select_one('h2 a')
            relative_url = title_tag['href']
            full_name = relative_url.strip('/') # user/repo
            
            # Description
            desc_tag = item.select_one('p')
            description = desc_tag.text.strip() if desc_tag else "No epitaph found."
            
            # Stats
            stars_tag = item.select_one('a[href$="/stargazers"]')
            stars = stars_tag.text.strip() if stars_tag else "0"
            
            # Metadata
            language_tag = item.select_one('span[itemprop="programmingLanguage"]')
            lang = language_tag.text.strip() if language_tag else "Unknown"
            
            repos.append({
                "name": full_name,
                "url": f"https://github.com{relative_url}",
                "description": description,
                "stars": stars,
                "language": lang
            })
        except Exception as e:
            continue
            
    return repos

def dig_and_review(repos):
    """
    Sends the repo list to Gemini for a spicy review.
    """
    if not repos:
        print("⚰️ The graveyard is empty.")
        return

    print(f"💀 Dug up {len(repos)} bodies. Summoning the Spirit (Gemini)...")
    
    # Construct the prompt
    repo_text = ""
    for i, repo in enumerate(repos[:10]): # Limit to top 10
        repo_text += f"{i+1}. **{repo['name']}** ({repo['stars']} stars, {repo['language']})\n"
        repo_text += f"   Desc: {repo['description']}\n\n"
        
    prompt = f"""
    {SCENE_SETTING}
    
    Here are the bodies I found today:
    
    {repo_text}
    
    TASK:
    Pick the top 3 most interesting ones.
    Label them:
    - 💎 [The Diamond]: The most valuable/useful.
    - 🧱 [The Shovel]: The best tool/infrastructure.
    - 🤡Or👻 [The Meme/Ghost]: The weirdest or most overhyped.
    
    Provide a "Spicy Commentary" for each.
    """
    
    # TODO: Connect to Gemini API here
    # model = genai.GenerativeModel('gemini-pro')
    # response = model.generate_content(prompt)
    # print(response.text)
    
    print("--- DEBUG: Prompt Prepared ---")
    print(prompt)

if __name__ == "__main__":
    trend_repos = fetch_github_trends()
    dig_and_review(trend_repos)
