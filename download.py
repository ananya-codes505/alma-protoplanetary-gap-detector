import os
import sys
import requests

# Usage:  python download.py AS209
name = sys.argv[1] if len(sys.argv) > 1 else "AS209"
url = f"https://almascience.eso.org/almadata/lp/DSHARP/images/{name}_continuum.fits"
out = f"data/{name}_continuum.fits"

os.makedirs("data", exist_ok=True)
print("Downloading", url)
r = requests.get(url, timeout=120)
r.raise_for_status()
with open(out, "wb") as f:
    f.write(r.content)
print("Saved", out)
