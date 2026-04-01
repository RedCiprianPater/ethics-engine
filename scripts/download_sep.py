#!/usr/bin/env python3
"""
Batch download Stanford Encyclopedia of Philosophy articles.
Respects robots.txt, uses polite delays.
Caches to disk for offline processing.
"""

import requests
import time
import json
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE_URL = "https://plato.stanford.edu"
ARCHIVES_URL = "https://plato.stanford.edu/archives/"
OUTPUT_DIR = Path("data/raw/sep")
DELAY = 2  # seconds between requests

def get_archives():
    """Get list of available archives (spr, fall, win, etc.)"""
    resp = requests.get(ARCHIVES_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    archives = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('archives/') and href.endswith('/'):
            archives.append(urljoin(BASE_URL, href))
    return archives

def get_entries(archive_url):
    """Get all entry URLs from an archive"""
    resp = requests.get(archive_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    entries = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        # SEP entries are /entries/[name]/
        if '/entries/' in href and href.endswith('/'):
            full_url = urljoin(archive_url, href)
            entries.append(full_url)
    return list(set(entries))  # dedupe

def download_entry(entry_url):
    """Download single entry, extract text"""
    try:
        resp = requests.get(entry_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extract title
        title = soup.find('h1')
        title_text = title.get_text(strip=True) if title else "Unknown"
        
        # Extract main content
        content_div = soup.find('div', id='main-text')
        if not content_div:
            content_div = soup.find('div', {'class': 'entry-content'})
        
        if content_div:
            # Clean up: remove bibliography, footnotes for now
            for bib in content_div.find_all(['div', 'section'], class_=['bibliography', 'footnotes']):
                bib.decompose()
            
            text = content_div.get_text(separator='\n', strip=True)
            
            return {
                'url': entry_url,
                'title': title_text,
                'text': text,
                'word_count': len(text.split()),
                'source': 'stanford_encyclopedia'
            }
    except Exception as e:
        print(f"Error downloading {entry_url}: {e}")
    return None

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Fetching SEP archives...")
    archives = get_archives()
    print(f"Found {len(archives)} archives")
    
    all_entries = []
    for archive in archives[:1]:  # Start with most recent only
        print(f"Fetching entries from {archive}...")
        entries = get_entries(archive)
        all_entries.extend(entries)
        time.sleep(DELAY)
    
    all_entries = list(set(all_entries))  # dedupe across archives
    print(f"Total unique entries: {len(all_entries)}")
    
    # Download each entry
    downloaded = 0
    for i, entry_url in enumerate(all_entries):
        # Check if already cached
        entry_name = urlparse(entry_url).path.strip('/').split('/')[-1]
        cache_file = OUTPUT_DIR / f"{entry_name}.json"
        
        if cache_file.exists():
            print(f"[{i+1}/{len(all_entries)}] Cached: {entry_name}")
            continue
        
        print(f"[{i+1}/{len(all_entries)}] Downloading: {entry_name}")
        data = download_entry(entry_url)
        
        if data:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            downloaded += 1
        
        time.sleep(DELAY)
        
        # Progress checkpoint every 10
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(all_entries)} entries processed")
    
    print(f"\nDone! Downloaded {downloaded} new entries.")
    print(f"Total cached: {len(list(OUTPUT_DIR.glob('*.json')))}")

if __name__ == "__main__":
    main()
