import sys
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.signal import find_peaks
 
# Disk table: name -> (distance in pc, inclination in deg, position angle in deg, star mass in solar masses)
# Values from the DSHARP papers (Andrews et al. 2018; Huang et al. 2018)
DISKS = {
    "AS209":    (121, 34.97, 85.76, 0.83),
    "DoAr25":   (138, 67.4, 110.6, 0.95),
    "Elias24":  (136, 29.0, 45.7, 0.78),
    "GWLup":    (155, 38.7, 37.6, 0.46),
    "HD143006": (165, 18.6, 169.0, 1.78),
    "HD163296": (101, 46.7, 133.33, 2.04),
    "RULup":    (159, 18.8, 121.0, 0.63),
    "SR4":      (134, 22.0, 18.0, 0.68),
}
 
# Usage:  python find_gaps.py AS209
NAME = sys.argv[1] if len(sys.argv) > 1 else "AS209"
DIST, INCL, PA, MSTAR = DISKS[NAME]
 
# 1. Load the image
with fits.open(f"data/{NAME}_continuum.fits") as f:
    img = np.nan_to_num(np.squeeze(f[0].data))
    pix = abs(f[0].header["CDELT1"]) * 3600              # arcsec per pixel
 
# 2. Distance of every pixel from the star, undoing the disk's tilt
yc, xc = np.unravel_index(np.argmax(img), img.shape)    # brightest pixel = star
y, x = np.indices(img.shape)
dx, dy = (xc - x) * pix, (y - yc) * pix                 # arcsec east, north
pa, inc = np.radians(PA), np.radians(INCL)
a = dx * np.sin(pa) + dy * np.cos(pa)                   # along the long axis
b = (-dx * np.cos(pa) + dy * np.sin(pa)) / np.cos(inc)  # short axis, stretched back
r_au = np.hypot(a, b) * DIST
 
# 3. Average brightness in 2-au-wide rings
radii = np.arange(0, 160, 2)
profile = np.array([img[(r_au >= r) & (r_au < r + 2)].mean() for r in radii])
 
# 4. Gaps = dips in the profile (width=0 also measures each dip's width)
gaps, props = find_peaks(-np.log10(np.clip(profile, 1e-9, None)), prominence=0.05, width=0)
widths = props["widths"] * 2                            # widths come in bins; each bin is 2 au
 
# 5. Ignore dips beyond the disk's edge (there the curve is just noise)
light = np.cumsum(profile * radii)                      # light inside each radius
edge = radii[np.argmax(light > 0.99 * light[-1])]       # radius holding 99% of the light
inside = radii[gaps] < edge
gaps, widths = gaps[inside], widths[inside]
 
# 6. What planet could carve each gap? (Kanagawa et al. 2016)
H = 0.07        # assumed disk thickness h/r
ALPHA = 1e-3    # assumed gas turbulence
 
def planet_size(m_jup):
    if m_jup < 0.03: return "smaller than Neptune"
    if m_jup < 0.15: return "Neptune-like"
    if m_jup < 0.6:  return "Saturn-like"
    return "Jupiter-like or bigger"
 
print(f"\n{NAME}  (disk edge ~{edge} au)")
for r_gap, w in zip(radii[gaps], widths):
    q = (w / (0.41 * r_gap)) ** 2 * H ** 1.5 * ALPHA ** 0.5   # planet mass / star mass
    m_jup = q * MSTAR * 1047.6                                # 1 solar mass = 1047.6 Jupiter masses
    print(f"  gap at {r_gap:3d} au, width {w:4.1f} au  ->  planet ~{m_jup:.2g} Jupiter masses ({planet_size(m_jup)})")
 
# 7. Plot image and profile side by side, save as PNG
c = int(1.2 / pix)                                      # show +/- 1.2 arcsec
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
ax1.imshow(np.arcsinh(img[yc-c:yc+c, xc-c:xc+c] / (0.05 * img.max())),
           origin="lower", cmap="inferno")
ax1.set_title(NAME); ax1.axis("off")
ax2.semilogy(radii, profile)
for g in gaps:
    ax2.axvline(radii[g], ls="--", color="k")
ax2.axvline(edge, color="r", lw=1)                      # red line = disk edge
ax2.set_xlabel("radius [au]"); ax2.set_ylabel("brightness [Jy/beam]")
plt.tight_layout()
plt.savefig(f"{NAME}_gaps.png", dpi=120)
plt.close()
 
