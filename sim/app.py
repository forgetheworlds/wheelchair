"""Cruiser III V1.0 — Simplified Browser Simulator (Natural Joystick, Worlds & Interactive CAD Explode).

Run:
  python sim/app.py
  python sim/app.py --world ada_8_3 --port 8085
"""
from __future__ import annotations
import argparse
import dataclasses
import math
import numpy as np
import mujoco
from mujoco.studio import app as studio_app
from mujoco.studio import launch_web
from mujoco.studio import messages
from mujoco.studio import plugin
from mujoco.studio import viewer_protocol
from mujoco.studio.dear_imgui import dear_imgui as imgui

from worlds import WORLDS, EXPLODE_OFFSETS, WorldDef, build_world, build_explode_showcase

SPEED_MODES = {1: 3.2 / 3.6, 2: 6.0 / 3.6, 3: 9.0 / 3.6}
CAMERAS = ["chase_cam", "driver_pov", "hero_cam", "drive_closeup", "explode_cam", "free"]
CAM_LABELS = ["Chase", "Driver POV", "Hero 3/4", "Drive Detail", "Explode View", "Free Orbit"]


@dataclasses.dataclass
class ControlCmd(messages.Snapshot):
    throttle: float = 0.0
    steer: float = 0.0
    speed_mode: int = 2
    power_on: bool = True
    engaged: bool = True
    explode: float = 0.0


@dataclasses.dataclass
class ModeSwitchEvent(messages.Event):
    world_key: str = "proving_ground"
    explode_mode: bool = False


@dataclasses.dataclass
class Telemetry(messages.Snapshot):
    speed_kmh: float = 0.0
    current_a: float = 0.0
    soc_pct: float = 100.0
    regen_mwh: float = 0.0
    pos_z: float = 0.0
    slip: bool = False


class FOCDriveController:
    """Natural human mobility-joystick + 36V 70mm 60KV Dual-FOC motor & regen physics."""

    def __init__(self, world: WorldDef):
        self.world = world
        self.reset()

    def reset(self):
        self.soc, self.spent_wh, self.regen_wh = 1.0, 0.0, 0.0
        self.current_a, self.slip = 0.0, False
        self.roller_wl = self.roller_wr = 0.0
        self._v = self._w = self._il = self._ir = 0.0

    def step(self, cmd: ControlCmd, wl: float, wr: float, dt: float) -> tuple[float, float]:
        r_wheel, r_roller, track_half = 0.3048, 0.035, 0.2975
        G = r_wheel / r_roller
        w_noload = 60.0 * 36.0 * 2.0 * math.pi / 60.0
        max_tau = (0.45 if self.world.wet else 0.85) * 145.0 * r_wheel
        rr = 0.5 * self.world.crr * 120.0 * 9.81 * r_wheel
        rr_l, rr_r = -rr * math.tanh(wl / 0.08), -rr * math.tanh(wr / 0.08)

        if not cmd.engaged:
            self.slip, self.current_a, self.roller_wl, self.roller_wr = False, 0.0, 0.0, 0.0
            self._il = self._ir = 0.0
            return rr_l, rr_r

        v_max = SPEED_MODES[cmd.speed_mode]
        v_curr = 0.5 * (wl + wr) * r_wheel
        hi_frac = float(np.clip((abs(v_curr) - 1.65) / 1.0, 0.0, 1.0))
        w_max = 2.85 if abs(cmd.throttle) < 0.05 else (2.35 - 0.95 * hi_frac)

        vt, wt = cmd.throttle * v_max, cmd.steer * w_max
        va = 1.65 if abs(vt) > abs(self._v) else 2.80
        wa = 5.50 if abs(wt) > abs(self._w) else 7.50
        self._v += float(np.clip(vt - self._v, -va * dt, va * dt))
        self._w += float(np.clip(wt - self._w, -wa * dt, wa * dt))

        vl, vr = self._v - self._w * track_half, self._v + self._w * track_half
        cap = max(v_max * 1.15, 1.2)
        pk = max(abs(vl), abs(vr))
        if pk > cap:
            vl, vr = vl * (cap / pk), vr * (cap / pk)

        taus, slips, roms, ints, p_elec_tot = [], [], [], [self._il, self._ir], 0.0
        for i, (w_w, w_c) in enumerate(((wl, vl / r_wheel), (wr, vr / r_wheel))):
            w_r = w_w * G
            if cmd.power_on:
                err = w_c - w_w
                ints[i] = float(np.clip(ints[i] + err * dt, -0.35, 0.35))
                if abs(w_c) < 0.02 and abs(w_w) < 0.05:
                    ints[i] *= 0.85
                tr = float(np.clip(5.8 * err + 14.0 * ints[i], -4.8, 4.8))
                pos_lim = 4.8 * max(0.0, 1.0 - abs(w_r) / w_noload)
                if tr * w_r > 0:
                    tr = float(np.clip(tr, -pos_lim, pos_lim))
                tw_cmd = tr * G
            else:
                ints[i] = 0.0
                tw_cmd = float(np.clip(-w_w * 320.0, -max_tau, max_tau))

            sl = abs(tw_cmd) > max_tau
            tw = float(np.clip(tw_cmd, -max_tau, max_tau))
            if sl:
                ints[i] *= 0.90
            pm = tw * w_w
            if pm >= 0:
                pe = pm / 0.85 + 2.5
                self.spent_wh += pe * dt / 3600.0
            else:
                pr = min(abs(pm) * 0.65, 144.0) if cmd.power_on else 0.0
                pe = -pr
                self.regen_wh += pr * dt / 3600.0
            p_elec_tot += pe
            taus.append(tw); slips.append(sl); roms.append(-w_r * (1.35 if sl else 1.0))

        self._il, self._ir = ints
        self.slip = any(slips)
        self.roller_wl, self.roller_wr = roms
        self.current_a = p_elec_tot / 36.0
        self.soc = float(np.clip(1.0 - (self.spent_wh - self.regen_wh) / 360.0, 0.0, 1.0))
        return taus[0] + rr_l, taus[1] + rr_r


class BrowserHUD(plugin.ViewerPlugin):
    """Browser HUD: 2D Virtual Joystick + WASD, World Switcher, and Interactive CAD Exploded View."""

    def __init__(self, initial_world: str):
        super().__init__()
        self.world_key = initial_world
        self.explode_mode = False
        self.explode_pct = 0.0
        self.mode, self.power_on, self.engaged = 2, True, True
        self.cam_idx, self._cam_ready = 0, False
        self.tel = Telemetry()
        self._last_cmd = ControlCmd()

    @messages.handler
    def on_telemetry(self, t: Telemetry) -> bool:
        self.tel = t
        return False

    @messages.handler
    def on_post_model(self, event: messages.PostModelEvent) -> bool:
        self._cam_ready = False
        return False

    def _set_cam(self, idx: int):
        self.cam_idx = idx % len(CAMERAS)
        if self.viewer is None or self.viewer.model is None:
            return
        name = CAMERAS[self.cam_idx]
        if name == "free":
            self.viewer.camera.type = mujoco.mjtCamera.mjCAMERA_FREE
            self.viewer.camera_index = -1
        else:
            cid = mujoco.mj_name2id(self.viewer.model, mujoco.mjtObj.mjOBJ_CAMERA, name)
            if cid >= 0:
                self.viewer.camera.type = mujoco.mjtCamera.mjCAMERA_FIXED
                self.viewer.camera.fixedcamid = cid
                self.viewer.camera_index = cid

    def _enter_explode(self, pct: float):
        self.explode_pct = pct
        if not self.explode_mode:
            self.explode_mode = True
            self.cam_idx = 4  # explode_cam
            if self.viewer is not None:
                self.viewer.send_to_sim(ModeSwitchEvent(world_key=self.world_key, explode_mode=True))

    def _enter_drive(self, world_key: str):
        self.world_key = world_key
        self.explode_mode = False
        self.explode_pct = 0.0
        self.cam_idx = 0  # chase_cam
        if self.viewer is not None:
            self.viewer.send_to_sim(ModeSwitchEvent(world_key=world_key, explode_mode=False))

    @messages.handler
    def on_build_gui(self, event: messages.BuildGuiEvent) -> bool:
        if not self._cam_ready and self.viewer is not None and self.viewer.model is not None:
            self._cam_ready = True
            self._set_cam(self.cam_idx)

        io = imgui.GetIO()
        mod = bool(io.KeyCtrl or io.KeySuper or io.KeyAlt)
        w = (not mod) and (imgui.IsKeyDown(imgui.Key.W) or imgui.IsKeyDown(imgui.Key.UpArrow))
        s = (not mod) and (imgui.IsKeyDown(imgui.Key.S) or imgui.IsKeyDown(imgui.Key.DownArrow))
        a = (not mod) and (imgui.IsKeyDown(imgui.Key.A) or imgui.IsKeyDown(imgui.Key.LeftArrow))
        d = (not mod) and (imgui.IsKeyDown(imgui.Key.D) or imgui.IsKeyDown(imgui.Key.RightArrow))

        if not mod:
            if imgui.IsKeyPressed(imgui.Key.M, False): self.mode = (self.mode % 3) + 1
            if imgui.IsKeyPressed(imgui.Key.E, False): self.power_on = not self.power_on
            if imgui.IsKeyPressed(imgui.Key.R, False): self.engaged = not self.engaged
            if imgui.IsKeyPressed(imgui.Key.V, False): self._set_cam(self.cam_idx + 1)

        thr_kb, str_kb = (1.0 if w else 0.0) - (1.0 if s else 0.0), (1.0 if a else 0.0) - (1.0 if d else 0.0)
        thr_joy = str_joy = 0.0
        joy_on = False

        imgui.SetNextWindowPos(imgui.Vec2(14, 14), imgui.Cond.FirstUseEver)
        imgui.SetNextWindowSize(imgui.Vec2(335, 540), imgui.Cond.FirstUseEver)
        opened, _ = imgui.Begin("Cruiser III V1.0 — Controls, Worlds & CAD Explode", True)
        if opened:
            t = self.tel
            if self.explode_mode:
                imgui.Text("VIEWING: 3D CAD Exploded Showcase")
            else:
                imgui.Text(f"Speed: {t.speed_kmh:+5.2f} km/h | Elev: {t.pos_z:4.2f} m")
                imgui.Text(f"Batt:  {t.soc_pct:5.1f}% ({t.current_a:+5.1f} A) | Regen: +{t.regen_mwh:5.1f} mWh")
            imgui.Text(f"Cam:   {CAM_LABELS[self.cam_idx]} | Grip: {'SLIP!' if t.slip else 'LOCKED'}")
            imgui.Separator()

            # --- 2D Spring-Return Thumb Joystick ---
            imgui.Text("Drag Thumbstick or Hold WASD / Arrows:")
            pad, rad = 148.0, 64.0
            pos = imgui.GetCursorScreenPos()
            cx, cy = pos.x + pad * 0.5, pos.y + pad * 0.5
            imgui.InvisibleButton("##joy", imgui.Vec2(pad, pad))
            if imgui.IsItemActive() and not self.explode_mode:
                mp = imgui.GetMousePos()
                dx, dy = (mp.x - cx) / rad, (cy - mp.y) / rad
                mag = math.hypot(dx, dy)
                if mag > 1.0:
                    dx, dy = dx / mag, dy / mag
                expo = lambda v: 0.0 if abs(v) < 0.07 else math.copysign(0.55 * ((abs(v) - 0.07) / 0.93) + 0.45 * (((abs(v) - 0.07) / 0.93) ** 2), v)
                thr_joy, str_joy, joy_on = expo(dy), expo(-dx), True

            dt_v, ds_v = (thr_joy if joy_on else thr_kb), (str_joy if joy_on else str_kb)
            if self.explode_mode:
                dt_v = ds_v = 0.0
            kx, ky = cx - ds_v * rad, cy - dt_v * rad
            dl = imgui.GetWindowDrawList()
            c_bg = imgui.ColorConvertFloat4ToU32(imgui.Vec4(0.11, 0.13, 0.16, 0.95))
            c_ln = imgui.ColorConvertFloat4ToU32(imgui.Vec4(0.42, 0.48, 0.56, 0.85))
            c_ax = imgui.ColorConvertFloat4ToU32(imgui.Vec4(0.30, 0.34, 0.40, 0.65))
            c_kb = imgui.ColorConvertFloat4ToU32(imgui.Vec4(0.92, 0.20, 0.16, 1.0))
            dl.AddCircleFilled(imgui.Vec2(cx, cy), rad + 5, c_bg, 48)
            dl.AddCircle(imgui.Vec2(cx, cy), rad + 5, c_ln, 48, 2.0)
            dl.AddLine(imgui.Vec2(cx - rad, cy), imgui.Vec2(cx + rad, cy), c_ax, 1.0)
            dl.AddLine(imgui.Vec2(cx, cy - rad), imgui.Vec2(cx, cy + rad), c_ax, 1.0)
            dl.AddLine(imgui.Vec2(cx, cy), imgui.Vec2(kx, ky), c_ln, 4.0)
            dl.AddCircleFilled(imgui.Vec2(kx, ky), 15.0, c_kb, 32)

            imgui.SameLine()
            imgui.Text(f"\nFWD: {dt_v:+.2f}\nTRN: {ds_v:+.2f}\n\n[W/S] Drive\n[A/D] Turn\n[V] Camera")

            for m_id, lbl in ((1, "3 km/h"), (2, "6 km/h"), (3, "9 km/h")):
                if imgui.Button(f"{'*' if self.mode == m_id else ''}{lbl}##m{m_id}"):
                    self.mode = m_id
                imgui.SameLine()
            if imgui.Button("Cam [V]##c"):
                self._set_cam(self.cam_idx + 1)

            if imgui.Button(("E-STOP: ARMED [E]" if self.power_on else "E-STOP: HELD [E]") + "##e"):
                self.power_on = not self.power_on
            imgui.SameLine()
            if imgui.Button(("Rollers: ON [R]" if self.engaged else "Rollers: FREE [R]") + "##r"):
                self.engaged = not self.engaged

            # --- Interactive 3D CAD Exploded View ---
            imgui.Separator()
            imgui.Text("Interactive 3D CAD Exploded View:")
            changed, val = imgui.SliderFloat("Explode##exp", self.explode_pct, 0.0, 100.0, "%.0f%%")
            if changed:
                if val > 1.0:
                    self._enter_explode(val)
                elif self.explode_mode:
                    self.explode_pct = val
            if imgui.Button("Explode CAD (100%)##e1"):
                self._enter_explode(100.0)
            imgui.SameLine()
            if imgui.Button("Back to Drive##e0"):
                self._enter_drive(self.world_key)

            # --- World Switcher ---
            imgui.Separator()
            imgui.Text("Switch World:")
            for wk, wdef in WORLDS.items():
                mark = "> " if (wk == self.world_key and not self.explode_mode) else "  "
                if imgui.Button(f"{mark}{wdef.label}##w_{wk}"):
                    self._enter_drive(wk)
        imgui.End()

        cmd = ControlCmd(
            throttle=0.0 if self.explode_mode else (thr_joy if joy_on else thr_kb),
            steer=0.0 if self.explode_mode else (str_joy if joy_on else str_kb),
            speed_mode=self.mode, power_on=self.power_on, engaged=self.engaged,
            explode=self.explode_pct / 100.0,
        )
        if cmd != self._last_cmd and self.viewer is not None:
            self._last_cmd = cmd
            self.viewer.send_to_sim(cmd)
        return False


class SimRunner(plugin.SimPlugin):
    """Runs either rock-solid driving physics OR pure kinematic 60 FPS CAD Explode Showcase."""

    def __init__(self, world: WorldDef):
        super().__init__()
        self.world = world
        self.explode_mode = False
        self.ctrl = FOCDriveController(world)
        self.cmd = ControlCmd()
        self._drive_dofs = None
        self._exp_joints: list[tuple[int, int, float]] = []
        self._n = 0

    def _bind(self, m: mujoco.MjModel):
        if self.explode_mode:
            self._exp_joints = []
            for part, vec in EXPLODE_OFFSETS.items():
                jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"exp_{part}_jnt")
                if jid >= 0:
                    self._exp_joints.append((m.jnt_qposadr[jid], m.jnt_dofadr[jid], math.hypot(*vec)))
            self._drive_dofs = None
        else:
            self._drive_dofs = tuple(
                m.jnt_dofadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j)]
                for j in ("left_wheel_hinge", "right_wheel_hinge", "left_roller_hinge", "right_roller_hinge")
            )
            self._exp_joints = []

    @messages.handler
    def on_cmd(self, c: ControlCmd) -> bool:
        self.cmd = c
        return False

    @messages.handler
    def on_mode_switch(self, ev: ModeSwitchEvent) -> bool:
        if self.handle is None:
            return False
        self.explode_mode = ev.explode_mode
        self._drive_dofs = None
        self._exp_joints = []
        if ev.explode_mode:
            m, d = build_explode_showcase()
            self.handle.set_model(m, d)
        elif ev.world_key in WORLDS:
            m, d, w = build_world(ev.world_key)
            self.world, self.ctrl = w, FOCDriveController(w)
            self.handle.set_model(m, d)
        return False

    @messages.handler
    def on_reset(self, ev: messages.ResetEvent) -> bool:
        self.ctrl.reset()
        return False

    @messages.handler
    def on_pre_step(self, ev: messages.PreStepEvent) -> bool:
        m, d = self.handle.model, self.handle.data
        if m is None or d is None:
            return False
        if self.explode_mode:
            if not self._exp_joints:
                self._bind(m)
            exp = float(np.clip(self.cmd.explode, 0.0, 1.0))
            for qadr, dadr, dist in self._exp_joints:
                d.qpos[qadr] = exp * dist
                d.qvel[dadr] = 0.0
            mujoco.mj_forward(m, d)
            return False

        if self._drive_dofs is None:
            self._bind(m)
        ql, qr, rl, rr = self._drive_dofs
        tl, tr = self.ctrl.step(self.cmd, float(d.qvel[ql]), float(d.qvel[qr]), m.opt.timestep)
        d.qfrc_applied[:] = 0.0
        d.qfrc_applied[ql], d.qfrc_applied[qr] = tl, tr
        d.qfrc_applied[rl] = 0.25 * (self.ctrl.roller_wl - float(d.qvel[rl]))
        d.qfrc_applied[rr] = 0.25 * (self.ctrl.roller_wr - float(d.qvel[rr]))

        self._n += 1
        if self._n % 25 == 0:
            v_kmh = 0.5 * (float(d.qvel[ql]) + float(d.qvel[qr])) * 0.3048 * 3.6
            self.handle.send_to_viewer(Telemetry(
                speed_kmh=v_kmh, current_a=self.ctrl.current_a, soc_pct=self.ctrl.soc * 100.0,
                regen_mwh=self.ctrl.regen_wh * 1000.0, pos_z=float(d.qpos[2]), slip=self.ctrl.slip,
            ))
        return False


def main():
    p = argparse.ArgumentParser(description="Cruiser III V1.0 Browser Simulator")
    p.add_argument("--world", default="proving_ground", choices=list(WORLDS.keys()))
    p.add_argument("--port", type=int, default=8085)
    p.add_argument("--no-browser", action="store_true")
    args = p.parse_args()

    model, data, world = build_world(args.world)
    vcfg = viewer_protocol.ViewerConfig(
        title="Cruiser III V1.0 — Direct-Drive BLDC FOC Simulator",
        http_port=args.port,
        open_browser=not args.no_browser,
    )
    launch_web.run(
        vcfg, model=model, data=data,
        plugins=[studio_app.App(), *studio_app.SIM_PLUGINS, BrowserHUD(world.key), SimRunner(world)],
    )


if __name__ == "__main__":
    main()
