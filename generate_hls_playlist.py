import subprocess
import sys
from datetime import datetime

def run_yt_dlp(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"yt-dlp error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def get_video_info(video_id):
    cmd = [
        'yt-dlp',
        '--print', '%(channel)s - %(title)s',
        '--no-warnings',
        f'https://www.youtube.com/watch?v={video_id}'
    ]
    info = run_yt_dlp(cmd)
    return info if info else f"Unknown - {video_id}"

def get_hls_url(video_id):
    # Daha agresif format seçimi + user agent
    cmd = [
        'yt-dlp',
        '-f', 'best[protocol*=m3u8]/bestvideo+bestaudio/best',
        '--get-url',
        '--no-warnings',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        f'https://www.youtube.com/watch?v={video_id}'
    ]
    url = run_yt_dlp(cmd)
    return url if url and url.startswith('http') else f"# Hata: {video_id} için HLS linki alınamadı"

def main():
    output_file = "ytbred_hls.m3u"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-PLAYLIST-TYPE:VOD\n")
        f.write("# Playlist: ytbred_hls (GitHub Actions)\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write("# https://github.com/botechred/ytbred\n\n")
        
        try:
            with open("video_id.txt", "r", encoding="utf-8") as id_file:
                video_ids = [line.strip() for line in id_file if line.strip() and not line.strip().startswith("#")]
        except FileNotFoundError:
            f.write("# Hata: video_id.txt bulunamadı!\n")
            return

        print(f"Toplam {len(video_ids)} video işleniyor...")
        
        for idx, video_id in enumerate(video_ids, 1):
            print(f"[{idx}/{len(video_ids)}] {video_id}")
            title = get_video_info(video_id)
            hls_url = get_hls_url(video_id)
            
            f.write(f"#EXTINF:-1 tvg-id=\"{video_id}\" group-title=\"ytbred\",{title}\n")
            f.write(f"{hls_url}\n\n")
    
    print(f"✅ Playlist oluşturuldu: {output_file}")

if __name__ == "__main__":
    main()
