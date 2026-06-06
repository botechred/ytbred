import base64
import os
import re
import requests
import urllib3
import sys
from datetime import datetime

# SSL uyarılarını bastır
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Direk GitHub Secret'ten al
ENCRYPTED_URL = os.environ.get('ENCRYPTED_PLAYLIST_URL')
if not ENCRYPTED_URL:
    print("HATA: ENCRYPTED_PLAYLIST_URL GitHub Secret'ı bulunamadı!")
    sys.exit(1)

def create_redtube_folder():
    if not os.path.exists("redtube"):
        os.makedirs("redtube")

def decrypt_url():
    decrypted_bytes = base64.b64decode(ENCRYPTED_URL)
    return decrypted_bytes.decode("utf-8")

def fetch_playlist(url):
    response = requests.get(url, verify=False, timeout=30)
    response.raise_for_status()
    return response.text

def parse_playlist(content):
    lines = content.strip().split("\n")
    channels = []
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            match = re.search(r",(.+)$", lines[i])
            if match and i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                channel_name = match.group(1).strip()
                channel_url = lines[i + 1].strip()
                channels.append((channel_name, channel_url))
    return channels

def save_channel_as_m3u8(channel_name, stream_url):
    # Güvenli dosya adı
    safe_name = "".join(c for c in channel_name if c.isalnum() or c in ".-_").rstrip()
    safe_name = safe_name.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    safe_name = safe_name.replace('İ', 'I').replace('Ğ', 'G').replace('Ü', 'U').replace('Ş', 'S').replace('Ö', 'O').replace('Ç', 'C')
    
    filename = f"redtube/{safe_name}.m3u8"
    
    content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=1280000,RESOLUTION=1280x720
{stream_url}
"""

    # === DEĞİŞİKLİK KONTROLÜ ===
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"No change: {filename}")
                return
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {filename}")

def create_master_playlist(channels):
    master_content = ["#EXTM3U"]
    master_content.append("# Playlist: redtube")
    master_content.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    master_content.append(f"# Total channels: {len(channels)}")
    master_content.append("")

    for channel_name, stream_url in channels:
        master_content.append(f"#EXTINF:-1 tvg-logo=\"\" group-title=\"redtube\",{channel_name}")
        master_content.append(stream_url)
        master_content.append("")

    master_filename = "redtube/redtube.m3u"
    with open(master_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(master_content))
    print(f"✅ Master playlist saved: {master_filename}")

    # GitHub raw için
    github_filename = "redtube/redtube_github.m3u"
    github_content = ["#EXTM3U"]
    for channel_name, stream_url in channels:
        github_content.append(f"#EXTINF:-1,{channel_name}")
        github_content.append(stream_url)

    with open(github_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(github_content))
    print(f"✅ GitHub compatible playlist saved: {github_filename}")

def main():
    try:
        create_redtube_folder()
        playlist_url = decrypt_url()
        print(f"Fetching playlist from: {playlist_url[:50]}...")
        playlist_content = fetch_playlist(playlist_url)
        channels = parse_playlist(playlist_content)
        
        if not channels:
            print("No channels found in playlist.")
            return
        
        print(f"\n📺 Found {len(channels)} channels. Processing...\n")
        
        for name, url in channels:
            save_channel_as_m3u8(name, url)
        
        create_master_playlist(channels)
        
        print(f"\n✅ Successfully processed {len(channels)} channels")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
