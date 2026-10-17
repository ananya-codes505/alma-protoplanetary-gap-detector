import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
 
# A star (mass 1) at the centre, a planet on a circular orbit at radius 1,
# and thousands of dust grains feeling the gravity of both.
# Units: G = 1, star mass = 1, so the planet takes 2*pi time units per orbit.
rng = np.random.default_rng(1)
N = 6000            # number of dust grains
Q = 0.005           # planet mass / star mass (~5 Jupiter masses around a Sun-like star)
DT = 0.02           # time step
STEPS_PER_FRAME = 30     # smaller = slower, smoother motion
FRAMES = 330             # ~16 seconds at 20 frames per second
 
# Dust grains on circular orbits between radius 0.5 and 1.7
r = np.sqrt(rng.uniform(0.5**2, 1.7**2, N))
th = rng.uniform(0, 2 * np.pi, N)
pos = np.c_[r * np.cos(th), r * np.sin(th)]
vel = np.c_[-np.sin(th), np.cos(th)] / np.sqrt(r)[:, None]     # circular speed = 1/sqrt(r)
 
def planet_pos(t):
    return np.array([np.cos(t), np.sin(t)])                    # radius 1, period 2*pi
 
def accel(p, t):
    a = -p / np.linalg.norm(p, axis=1, keepdims=True) ** 3     # pull of the star
    d = p - planet_pos(t)
    a -= Q * d / (np.sum(d**2, axis=1, keepdims=True) + 1e-4) ** 1.5   # pull of the planet
    return a
 
fig, ax = plt.subplots(figsize=(6, 6), facecolor="black")
ax.set_facecolor("black"); ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-1.9, 1.9); ax.set_ylim(-1.9, 1.9)
dust = ax.scatter(pos[:, 0], pos[:, 1], s=3, c="#ff9a3c", alpha=0.7, linewidths=0)
ax.scatter([0], [0], s=120, c="gold")                          # star
planet = ax.scatter([1], [0], s=60, c="deepskyblue", edgecolors="white")   # planet
label = ax.text(0.02, 0.97, "", color="white", transform=ax.transAxes, va="top", fontsize=11)
ax.set_title("A young planet carving a gap in its dust disk", color="white", fontsize=12)
 
t = 0.0
acc = accel(pos, t)
 
def update(frame):
    global pos, vel, acc, t
    for _ in range(STEPS_PER_FRAME):                            # leapfrog integration
        vel += 0.5 * DT * acc
        pos += DT * vel
        t += DT
        acc = accel(pos, t)
        vel += 0.5 * DT * acc
    dust.set_offsets(pos)
    planet.set_offsets([planet_pos(t)])
    label.set_text(f"planet orbits: {t / (2 * np.pi):.0f}")
    return dust, planet, label
 
anim = FuncAnimation(fig, update, frames=FRAMES, blit=False)
anim.save("planet_gap.gif", writer=PillowWriter(fps=20), dpi=80, savefig_kwargs={"facecolor": "black"})
print("Saved planet_gap.gif")
 
