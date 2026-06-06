import requests
import re
import time
import os
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9"
}

def is_live_stream_active(video_id):
    """YouTube videosunun canlı yayın yapıp yapmadığını kontrol eder"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            return False, "HTTP Error"
        
        html = r.text
        
        # HLS manifest varsa ve canlıysa
        if '"hlsManifestUrl"' in html or 'liveStreamable":true' in html:
            m = re.search(r'"hlsManifestUrl":"([^"]+\.m3u8[^"]*)"', html)
            if m:
                return True, m.group(1).replace("\\/", "/")
        
        # Alternatif kontroller
        if any(x in html for x in ['"isLive":true', '"liveBroadcastDetails"']):
            return True, "LIVE"
            
        return False, "Ended or Not Live"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


# ===================== ANA İŞLEM =====================
with open("video_id.txt", "r", encoding="utf-8") as f:
    video_ids = [line.strip() for line in f if line.strip()]

working = []
not_working = []

print(f"🔍 Toplam {len(video_ids)} video ID kontrol ediliyor...\n")

for idx, vid in enumerate(video_ids, 1):
    print(f"[{idx:3}/{len(video_ids)}] Kontrol: {vid}")
    is_active, info = is_live_stream_active(vid)
    
    if is_active:
        working.append(vid)
        print(f"   ✅ ÇALIŞIYOR")
    else:
        not_working.append(vid)
        print(f"   ❌ BİTTİ / GEÇERSİZ - {info}")
    
    time.sleep(2.5)  # YouTube rate limit'e takılmamak için

# Dosyaları güncelle
with open("video_id.txt", "w", encoding="utf-8") as f:
    for vid in working:
        f.write(vid + "\n")

with open("video_id_no.txt", "a", encoding="utf-8") as f:  # append ile eski kayıtlar kalsın
    f.write(f"\n# === {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    for vid in not_working:
        f.write(vid + "\n")

print("\n" + "="*50)
print(f"✅ İşlem tamamlandı!")
print(f"   Çalışan ID:     {len(working)}")
print(f"   Çalışmayan ID:  {len(not_working)}")
print(f"   video_id.txt          → Güncellendi")
print(f"   video_id_no.txt       → Güncellendi (append)")
