import subprocess
import sys
from datetime import datetime

def get_video_info(video_id):
    try:
        # Kanal + Başlık al
        info_cmd = [
            'yt-dlp',
            '--print', '%(channel)s - %(title)s',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        info = subprocess.check_output(info_cmd, text=True, stderr=subprocess.DEVNULL).strip()
        return info
    except:
        return f"Unknown Channel - {video_id}"

def get_hls_url(video_id):
    try:
        # En iyi HLS (m3u8) linkini al
        cmd = [
            'yt-dlp',
            '-f', 'best[protocol*=m3u8]/best',
            '--get-url',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        url = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
        return url
    except:
        return f"# Hata: {video_id} için HLS linki alınamadı"

def main():
    output_file = "ytbred_hls.m3u"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-PLAYLIST-TYPE:VOD\n")
        f.write(f"# Playlist: ytbred_hls\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write("# https://github.com/botechred/ytbred\n\n")
        
        with open("video_id.txt", "r", encoding="utf-8") as id_file:
            video_ids = [line.strip() for line in id_file if line.strip() and not line.strip().startswith("#")]
        
        print(f"Toplam {len(video_ids)} video işleniyor...")
        
        for idx, video_id in enumerate(video_ids, 1):
            print(f"[{idx}/{len(video_ids)}] İşleniyor: {video_id}")
            title = get_video_info(video_id)
            hls_url = get_hls_url(video_id)
            
            f.write(f"#EXTINF:-1 tvg-id=\"{video_id}\" group-title=\"ytbred\",{title}\n")
            f.write(f"{hls_url}\n\n")
    
    print(f"✅ Playlist oluşturuldu: {output_file}")

if __name__ == "__main__":
    main()
