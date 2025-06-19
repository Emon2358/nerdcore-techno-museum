import os
import re
import argparse
import requests
from bs4 import BeautifulSoup


def scrape_posts(owner, keyword, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    base_url = f"https://vk.com/{owner}?w=wall"
    session = requests.Session()
    # Optional: set headers to mimic browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    })

    resp = session.get(base_url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    # posts have id like post{owner}_{postid}
    for post_div in soup.select('div.post'):  # VK's post container class may vary
        text_elem = post_div.select_one('.wall_post_text')
        if not text_elem:
            continue
        text = text_elem.get_text(strip=True)
        if keyword.lower() not in text.lower():
            continue

        # find attachments
        for doc_link in post_div.select('a.share_doc'):  # adjust selector
            href = doc_link.get('href')
            title = doc_link.get_text(strip=True)
            if href and title.endswith('.zip1'):
                # full URL
                file_url = href if href.startswith('http') else 'https://vk.com' + href
                print(f"Downloading {title} from {file_url}")
                download_file(session, file_url, out_dir, title)


def download_file(session, url, out_dir, filename):
    r = session.get(url, stream=True)
    r.raise_for_status()
    path = os.path.join(out_dir, filename)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print(f"Saved to {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword', required=True)
    parser.add_argument('--owner', default='doujinmusic')
    parser.add_argument('--out-dir', default='downloaded')
    args = parser.parse_args()

    scrape_posts(args.owner, args.keyword, args.out_dir)


if __name__ == '__main__':
    main()
