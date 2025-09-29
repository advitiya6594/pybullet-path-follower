import argparse, json, csv, os, math, time
from pathlib import Path
import numpy as np
import pybullet as p
import pybullet_data as pd

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def norm(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v

def simple_repulsion(pos, obstacles, influence=0.35, gain=0.6):
    repulse = np.zeros(3)
    for obs in obstacles:
        c = np.array(obs["center"], dtype=float)
        R = float(obs["radius"])
        dvec = pos - c
        dist = np.linalg.norm(dvec)
        if dist < max(influence, R + 1e-6):
            away = norm(dvec)
            closeness = max(0.0, (influence - dist) / influence)
            repulse += gain * closeness * away
    return repulse

def main():
    parser = argparse.ArgumentParser(description="PyBullet drone path follower")
    parser.add_argument("--gui", action="store_true", help="show GUI (default headless)")
    parser.add_argument("--speed", type=float, default=0.6, help="constant speed (m/s)")
    parser.add_argument("--dt", type=float, default=1.0/240.0, help="physics time step")
    parser.add_argument("--eps", type=float, default=0.05, help="arrival threshold (m)")
    parser.add_argument("--max-steps", type=int, default=12_000, help="safety cap")
    parser.add_argument("--waypoints", type=str, default="waypoints.json")
    parser.add_argument("--obstacles", type=str, default="obstacles.json")
    parser.add_argument("--traj-out", type=str, default="trajectory.csv")
    parser.add_argument("--record", action="store_true", help="save demo.mp4 via TinyRenderer")
    parser.add_argument("--video", type=str, default="assets/demo.mp4")
    args = parser.parse_args()

    if args.gui:
        cid = p.connect(p.GUI)
    else:
        cid = p.connect(p.DIRECT)

    p.setAdditionalSearchPath(pd.getDataPath())
    p.resetSimulation()
    p.setGravity(0, 0, -9.8)
    p.setTimeStep(args.dt)
    os.makedirs("assets", exist_ok=True)

    plane = p.loadURDF("plane.urdf")

    radius = 0.06
    mass = 0.25
    col = p.createCollisionShape(p.GEOM_SPHERE, radius=radius)
    vis = p.createVisualShape(p.GEOM_SPHERE, radius=radius, rgbaColor=[0.1, 0.5, 0.9, 1.0])
    start_pos = [0.0, 0.0, 0.3]
    drone = p.createMultiBody(mass, col, vis, basePosition=start_pos)

    waypoints = load_json(args.waypoints, [[1,0,0.3],[1,1,0.3],[0,1,0.3],[0,0,0.3]])
    obstacles = load_json(args.obstacles, [])
    wp_i = 0

    traj_rows = [["t", "x", "y", "z", "wp_i", "dist"]]
    t = 0.0

    writer = None
    if args.record:
        import imageio
        writer = imageio.get_writer(args.video, fps=max(1, int(1.0/args.dt)))

    for step in range(args.max_steps):
        pos, orn = p.getBasePositionAndOrientation(drone)
        pos = np.array(pos)
        target = np.array(waypoints[wp_i], dtype=float)
        dvec = target - pos
        dist = float(np.linalg.norm(dvec))

        if dist < args.eps:
            wp_i += 1
            if wp_i >= len(waypoints):
                print(f"Reached final waypoint at step {step}.")
                break
            target = np.array(waypoints[wp_i], dtype=float)
            dvec = target - pos
            dist = float(np.linalg.norm(dvec))

        desired_dir = norm(dvec)
        if obstacles:
            desired_dir = norm(desired_dir + simple_repulsion(pos, obstacles))

        v = desired_dir * args.speed
        p.resetBaseVelocity(drone, linearVelocity=v.tolist())

        traj_rows.append([f"{t:.4f}", f"{pos[0]:.5f}", f"{pos[1]:.5f}", f"{pos[2]:.5f}", wp_i, f"{dist:.5f}"])
        if args.gui:
            time.sleep(args.dt)
        p.stepSimulation()
        t += args.dt

        if writer is not None:
            w, h = 640, 480
            view = p.computeViewMatrixFromYawPitchRoll(
                cameraTargetPosition=pos.tolist(),
                distance=1.2, yaw=45, pitch=-30, roll=0, upAxisIndex=2
            )
            proj = p.computeProjectionMatrixFOV(fov=60, aspect=float(w)/h, nearVal=0.01, farVal=10)
            _, _, px, _, _ = p.getCameraImage(w, h, view, proj, renderer=p.ER_TINY_RENDERER)
            frame = np.reshape(px, (h, w, 4))[:, :, :3]
            writer.append_data(frame)

        if (step % max(1, int(0.25/args.dt))) == 0:
            print(f"t={t:6.2f}s  pos={pos}  -> wp[{wp_i}]={target}  dist={dist:.3f}")

    with open(args.traj_out, "w", newline="") as f:
        csv.writer(f).writerows(traj_rows)

    if writer is not None:
        writer.close()
        print(f"Saved video to {args.video}")

    p.disconnect(cid)
    print(f"Saved trajectory to {args.traj_out}")

if __name__ == "__main__":
    main()
