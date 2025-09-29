import csv, json
import numpy as np
import matplotlib.pyplot as plt

def load_csv(path):
    rows = []
    with open(path, "r") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    xs = np.array([float(r["x"]) for r in rows])
    ys = np.array([float(r["y"]) for r in rows])
    zs = np.array([float(r["z"]) for r in rows])
    return xs, ys, zs

def main():
    xs, ys, zs = load_csv("trajectory.csv")
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.plot(xs, ys, zs, linewidth=2)
    ax.scatter(xs[0], ys[0], zs[0], s=40, label="start")
    ax.scatter(xs[-1], ys[-1], zs[-1], s=40, label="end")
    try:
        wps = json.load(open("waypoints.json", "r"))
        wps = np.array(wps, dtype=float)
        ax.scatter(wps[:,0], wps[:,1], wps[:,2], marker="x", s=60, label="waypoints")
    except Exception:
        pass
    try:
        obs = json.load(open("obstacles.json", "r"))
        for o in obs:
            c = np.array(o["center"], dtype=float)
            ax.scatter(c[0], c[1], c[2], s=50, label="obstacle")
    except Exception:
        pass
    ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)"); ax.set_zlabel("Z (m)")
    ax.set_title("Drone Trajectory"); ax.legend()
    plt.show()

if __name__ == "__main__":
    main()