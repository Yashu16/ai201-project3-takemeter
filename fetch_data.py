import csv
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0.0.0 Safari/537.36"
}
TARGET = 500
LISTING_URL = "https://old.reddit.com/r/TrueFilm/top/?t=year"


def fetch(url: str) -> requests.Response | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 429:
            print(f"  429 rate-limited, waiting 30s then retrying...")
            time.sleep(30)
            r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"  {r.status_code} {url}")
            return None
        return r
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def get_post_links(listing_html: str) -> tuple[list[dict], str | None]:
    soup = BeautifulSoup(listing_html, "html.parser")
    items = []

    for thing in soup.select("div.thing.self"):  # self-posts only (have body text)
        title_tag = thing.select_one("a.title")
        score_tag = thing.select_one("div.score.unvoted, span.score.unvoted")
        permalink = thing.get("data-permalink", "")

        if not title_tag or not permalink:
            continue

        score_text = score_tag.get_text(strip=True) if score_tag else "0"
        try:
            score = int(score_text.replace(",", "").replace("•", "0"))
        except ValueError:
            score = 0

        items.append({
            "id": thing.get("data-fullname", "").replace("t3_", ""),
            "title": title_tag.get_text(strip=True),
            "score": score,
            "url": permalink,
        })

    next_tag = soup.select_one("span.next-button a")
    next_url = next_tag["href"] if next_tag else None
    return items, next_url


def get_post_body(post_html: str) -> str:
    soup = BeautifulSoup(post_html, "html.parser")
    expando = soup.select_one("div.expando div.md")
    if expando:
        return expando.get_text(" ", strip=True)
    # fallback: first div.md on the page (the OP text block)
    md = soup.select_one("div.md")
    return md.get_text(" ", strip=True) if md else ""


CSV_FILE = "truefilm_posts.csv"
FIELDNAMES = ["id", "title", "body", "score", "url", "label"]


def save(posts: list) -> None:
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(posts)


def load_existing() -> tuple[list, set]:
    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        seen_ids = {r["id"] for r in rows}
        print(f"Resuming — {len(rows)} posts already in CSV, skipping their IDs.")
        return rows, seen_ids
    except FileNotFoundError:
        return [], set()


posts, seen_ids = load_existing()
listing_url = LISTING_URL

while len(posts) < TARGET and listing_url:
    print(f"Fetching listing ({len(posts)} collected): {listing_url}")
    resp = fetch(listing_url)
    if resp is None:
        break

    items, listing_url = get_post_links(resp.text)
    if not items:
        print("No self-posts found on this page, stopping.")
        break

    for item in items:
        if len(posts) >= TARGET:
            break

        if item["id"] in seen_ids:
            print(f"  [skip] {item['title'][:60]}")
            continue

        post_url = f"https://old.reddit.com{item['url']}"
        post_resp = fetch(post_url)
        if post_resp is None:
            continue

        body = get_post_body(post_resp.text)
        if not body or len(body) < 100:
            continue

        posts.append({
            "id": item["id"],
            "title": item["title"],
            "body": body,
            "score": item["score"],
            "url": item["url"],
            "label": "",
        })
        seen_ids.add(item["id"])
        print(f"  [{len(posts)}] {item['title'][:60]}")
        time.sleep(4)

    save(posts)
    print(f"  (saved {len(posts)} so far)")

    time.sleep(6)

save(posts)

print(f"\nCollected {len(posts)} posts")