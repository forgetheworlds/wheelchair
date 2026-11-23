"""Cruiser III V1.0 — Rock-Solid Multi-World Physics + Kinematic 3D CAD Exploded Showcase."""
from __future__ import annotations
import math
from dataclasses import dataclass
from pathlib import Path
import mujoco

MESH_DIR = Path(__file__).parent / "meshes"


@dataclass(frozen=True)
class WorldDef:
    key: str
    label: str
    ground_mu: float = 0.88
    crr: float = 0.017
    wet: bool = False
    grade_pct: float = 0.0
    camber_pct: float = 0.0
    proving_ground: bool = False


WORLDS: dict[str, WorldDef] = {
    "proving_ground": WorldDef("proving_ground", "Proving Ground (Ramps & Bumps)", proving_ground=True),
    "ada_8_3":        WorldDef("ada_8_3",        "8.3% Max ADA Ramp",              grade_pct=8.3),
    "steep_10":       WorldDef("steep_10",       "10% Steep Driveway",             grade_pct=10.0),
    "wet_5":          WorldDef("wet_5",          "Wet Tile 5% Ramp",               ground_mu=0.38, crr=0.015, wet=True, grade_pct=5.0),
    "downhill_regen": WorldDef("downhill_regen", "Downhill -8% Regen",             grade_pct=-8.0),
    "grass_camber":   WorldDef("grass_camber",   "Grass/Gravel + 4% Camber",       ground_mu=0.65, crr=0.052, camber_pct=4.0),
}

EXPLODE_OFFSETS: dict[str, tuple[float, float, float]] = {
    "wheel_left":   ( 0.00,  0.26,  0.00),
    "wheel_right":  ( 0.00, -0.26,  0.00),
    "roller_left":  (-0.22,  0.22,  0.18),
    "roller_right": (-0.22, -0.22,  0.18),
    "drive_left":   (-0.14,  0.15,  0.10),
    "drive_right":  (-0.14, -0.15,  0.10),
    "underseat":    ( 0.00,  0.00, -0.20),
    "joystick":     ( 0.00, -0.04,  0.10),
    "caster_left":  ( 0.04,  0.08, -0.10),
    "caster_right": ( 0.04, -0.08, -0.10),
}


def _setup_visuals_and_meshes(spec: mujoco.MjSpec, wet: bool = False, grass: bool = False):
    spec.visual.global_.offwidth = 1280
    spec.visual.global_.offheight = 720
    spec.visual.headlight.ambient = [0.12, 0.13, 0.15]
    spec.visual.headlight.diffuse = [0.44, 0.44, 0.46]
    spec.visual.quality.shadowsize = 4096

    def mat(name, rgba, rough=0.6, metal=0.0, spec_val=0.25):
        m = spec.add_material(name=name)
        m.rgba, m.roughness, m.metallic, m.specular = list(rgba), rough, metal, spec_val

    mat("mat_wheel",    [0.035, 0.038, 0.045, 1.0], rough=0.82, metal=0.05, spec_val=0.12)
    mat("mat_chassis",  [0.14,  0.16,  0.19,  1.0], rough=0.42, metal=0.55, spec_val=0.35)
    mat("mat_pacf",     [0.05,  0.06,  0.075, 1.0], rough=0.70, metal=0.12, spec_val=0.18)
    mat("mat_underseat",[0.07,  0.14,  0.22,  1.0], rough=0.55, metal=0.10, spec_val=0.22)
    mat("mat_hub_red",  [0.72,  0.035, 0.05,  1.0], rough=0.38, metal=0.05, spec_val=0.30)

    spec.add_texture(
        name="sky", type=mujoco.mjtTexture.mjTEXTURE_SKYBOX, builtin=mujoco.mjtBuiltin.mjBUILTIN_GRADIENT,
        width=512, height=512, rgb1=[0.32, 0.56, 0.82], rgb2=[0.78, 0.83, 0.88],
    )
    spec.add_texture(
        name="gtex", type=mujoco.mjtTexture.mjTEXTURE_2D, builtin=mujoco.mjtBuiltin.mjBUILTIN_CHECKER,
        width=512, height=512,
        rgb1=[0.42, 0.44, 0.46] if not grass else [0.18, 0.34, 0.14],
        rgb2=[0.48, 0.50, 0.52] if not grass else [0.22, 0.40, 0.17],
    )
    mg = spec.add_material(name="ground_mat")
    mg.textures[mujoco.mjtTextureRole.mjTEXROLE_RGB] = "gtex"
    mg.texrepeat = [60, 60]
    mg.reflectance = 0.22 if wet else 0.02
    mg.roughness = 0.25 if wet else 0.85

    spec.worldbody.add_light(pos=[6, -6, 10], dir=[-0.4, 0.4, -0.8], diffuse=[0.85, 0.84, 0.80], castshadow=True)
    spec.worldbody.add_light(pos=[-6, 6, 8], dir=[0.5, -0.5, -0.8], diffuse=[0.35, 0.38, 0.42], castshadow=False)

    for mname, fname in [
        ("m_chassis", "chassis_base.stl"), ("m_wl", "wheel_left.stl"), ("m_wr", "wheel_right.stl"),
        ("m_caster", "caster_wheel.stl"), ("m_hub", "hub_motor_roller.stl"),
        ("m_drv_l", "drive_mounts_left.stl"), ("m_drv_r", "drive_mounts_right.stl"),
        ("m_under", "underseat_bay.stl"), ("m_joy", "joystick_pod.stl"),
    ]:
        spec.add_mesh(name=mname, file=str(MESH_DIR / fname), scale=[0.001, 0.001, 0.001])


def build_world(world_key: str = "proving_ground") -> tuple[mujoco.MjModel, mujoco.MjData, WorldDef]:
    """Build a rock-solid driving physics world (zero extra explode joints -> crisp solid ground contact)."""
    w = WORLDS[world_key]
    spec = mujoco.MjSpec()
    spec.modelname = f"cruiser_iii_v10_{w.key}"
    spec.option.timestep = 0.002
    spec.option.integrator = mujoco.mjtIntegrator.mjINT_IMPLICITFAST
    spec.option.cone = mujoco.mjtCone.mjCONE_ELLIPTIC
    spec.option.iterations = 60

    pitch, roll = math.atan(w.grade_pct / 100.0), math.atan(w.camber_pct / 100.0)
    spec.option.gravity = [
        -9.81 * math.sin(pitch),
        -9.81 * math.sin(roll) * math.cos(pitch),
        -9.81 * math.cos(pitch) * math.cos(roll),
    ]

    _setup_visuals_and_meshes(spec, wet=w.wet, grass=(w.key == "grass_camber"))

    # Solid, stiff, non-sinking ground plane
    spec.worldbody.add_geom(
        name="ground", type=mujoco.mjtGeom.mjGEOM_PLANE, size=[150, 150, 0.1],
        material="ground_mat", friction=[w.ground_mu, 0.005, 0.001], solref=[0.008, 1.0],
    )

    if w.proving_ground:
        for idx, (bx, h, tw) in enumerate([(2.2, 0.015, 0.14), (4.2, 0.022, 0.18)]):
            spec.worldbody.add_geom(
                name=f"thresh_{idx}", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[bx, 0, h / 2],
                size=[tw * 0.25, 2.5, h / 2], rgba=[0.86, 0.68, 0.16, 1], friction=[w.ground_mu, 0.005, 0.001], solref=[0.008, 1.0],
            )
            ang = math.degrees(math.atan2(h, tw * 0.45))
            for s in (-1, 1):
                spec.worldbody.add_geom(
                    name=f"thresh_{idx}_{s:+d}", type=mujoco.mjtGeom.mjGEOM_BOX,
                    pos=[bx + s * tw * 0.36, 0, h * 0.35], euler=[0, s * ang, 0],
                    size=[tw * 0.28, 2.5, h * 0.25], rgba=[0.82, 0.64, 0.14, 1], friction=[w.ground_mu, 0.005, 0.001], solref=[0.008, 1.0],
                )
        rlen, rslope, thick = 5.0, 0.05, 0.04
        rang, rh = math.atan(rslope), rlen * rslope
        cx, cz = 6.0 + (rlen / 2) * math.cos(rang), (rh / 2) - (thick / 2) * math.cos(rang)
        spec.worldbody.add_geom(
            name="ada_ramp", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[cx, 0, cz], euler=[0, -math.degrees(rang), 0],
            size=[rlen / 2, 1.15, thick / 2], rgba=[0.65, 0.67, 0.70, 1], friction=[0.88, 0.005, 0.001], solref=[0.008, 1.0],
        )
        for sy in (-1.12, 1.12):
            spec.worldbody.add_geom(
                name=f"curb_{sy:+.1f}", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[cx, sy, cz + 0.05],
                euler=[0, -math.degrees(rang), 0], size=[rlen / 2, 0.04, 0.045], rgba=[0.95, 0.75, 0.10, 1],
            )
        spec.worldbody.add_geom(
            name="landing", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[6.0 + rlen + 2.0, 0, rh - thick / 2],
            size=[2.0, 1.25, thick / 2], rgba=[0.60, 0.63, 0.66, 1], friction=[0.88, 0.005, 0.001], solref=[0.008, 1.0],
        )
        spec.worldbody.add_geom(name="wet_lane", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[5.0, 3.2, 0.002], size=[6.0, 1.0, 0.002], rgba=[0.18, 0.42, 0.62, 0.85], friction=[0.35, 0.004, 0.001], contype=0, conaffinity=0)
        spec.worldbody.add_geom(name="grass_lane", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[5.0, -3.2, 0.002], size=[6.0, 1.0, 0.002], rgba=[0.24, 0.44, 0.20, 1], friction=[0.65, 0.015, 0.002], contype=0, conaffinity=0)
        for px, py in [(1.5, 1.25), (3.5, -1.25), (5.5, 1.25)]:
            spec.worldbody.add_geom(name=f"cone_{px}_{py}", type=mujoco.mjtGeom.mjGEOM_CYLINDER, pos=[px, py, 0.20], size=[0.07, 0.20, 0], rgba=[0.94, 0.36, 0.08, 1], contype=0, conaffinity=0)

    # Rigid chassis body (120 kg total loaded mass — zero extra slide joints!)
    chassis = spec.worldbody.add_body(name="chassis", pos=[0, 0, 0.003])
    chassis.add_freejoint(name="root")
    chassis.add_geom(name="inertia_core", type=mujoco.mjtGeom.mjGEOM_BOX, pos=[-0.05, 0, 0.45], size=[0.20, 0.20, 0.04], mass=13.5, rgba=[0, 0, 0, 0], contype=0, conaffinity=0)

    # Rigidly attached CAD visual sub-meshes
    chassis.add_geom(name="chassis_cad",     type=mujoco.mjtGeom.mjGEOM_MESH, meshname="m_chassis", material="mat_chassis",   contype=0, conaffinity=0, mass=0.01)
    chassis.add_geom(name="drive_left_cad",  type=mujoco.mjtGeom.mjGEOM_MESH, meshname="m_drv_l",   material="mat_pacf",      contype=0, conaffinity=0, mass=0.01)
    chassis.add_geom(name="drive_right_cad", type=mujoco.mjtGeom.mjGEOM_MESH, meshname="m_drv_r",   material="mat_pacf",      contype=0, conaffinity=0, mass=0.01)
    chassis.add_geom(name="underseat_cad",   type=mujoco.mjtGeom.mjGEOM_MESH, meshname="m_under",   material="mat_underseat", contype=0, conaffinity=0, mass=0.01)
    chassis.add_geom(name="joystick_cad",    type=mujoco.mjtGeom.mjGEOM_MESH, meshname="m_joy",     material="mat_pacf",      contype=0, conaffinity=0, mass=0.01)

    # Rear anti-tipper collision spheres (44 mm ADA ground clearance)
    for side, tag in ((1, "L"), (-1, "R")):
        chassis.add_geom(name=f"anti_tip_{tag}", type=mujoco.mjtGeom.mjGEOM_SPHERE, pos=[-0.360, side * 0.239, 0.074], size=[0.030, 0, 0], mass=0.25, rgba=[0, 0, 0, 0], friction=[0.2, 0.005, 0.001], solref=[0.008, 1.0])

    # Rigidly seated 100.5 kg occupant mannequin (directly on chassis -> rock-solid CG & stability!)
    occ_b, occ_s, occ_p = [0.22, 0.36, 0.56, 0.92], [0.76, 0.62, 0.52, 0.95], [0.16, 0.22, 0.32, 0.94]
    occ_parts = [
        ("occ_pelvis", mujoco.mjtGeom.mjGEOM_CAPSULE, dict(fromto=[-0.08, -0.10, 0.56, -0.08, 0.10, 0.56], size=[0.085, 0, 0], mass=22.0, rgba=occ_b)),
        ("occ_torso",  mujoco.mjtGeom.mjGEOM_CAPSULE, dict(fromto=[-0.10, 0, 0.62, -0.14, 0, 1.02], size=[0.115, 0, 0], mass=34.0, rgba=occ_b)),
        ("occ_head",   mujoco.mjtGeom.mjGEOM_SPHERE,  dict(pos=[-0.14, 0, 1.18], size=[0.092, 0, 0], mass=8.0, rgba=occ_s)),
        ("occ_ruarm",  mujoco.mjtGeom.mjGEOM_CAPSULE, dict(fromto=[-0.14, -0.19, 0.96, -0.11, -0.235, 0.74], size=[0.042, 0, 0], mass=3.0, rgba=occ_b)),
        ("occ_rfarm",  mujoco.mjtGeom.mjGEOM_CAPSULE, dict(fromto=[-0.11, -0.235, 0.74, 0.05, -0.239, 0.76], size=[0.036, 0, 0], mass=2.0, rgba=occ_s)),
        ("occ_luarm",  mujoco.mjtGeom.mjGEOM_CAPSULE, dict(fromto=[-0.14, 0.19, 0.96, -0.11, 0.235, 0.74], size=[0.042, 0, 0], mass=3.0, rgba=occ_b)),
        ("occ_lfarm",  mujoco.mjtGeom.mjGEOM_CAPSULE, dict(fromto=[-0.11, 0.235, 0.74, 0.04, 0.239, 0.73], size=[0.036, 0, 0], mass=2.0, rgba=occ_s)),
    ]
    for sy in (-0.11, 0.11):
        occ_parts.append((f"occ_th_{sy:+.2f}", mujoco.mjtGeom.mjGEOM_CAPSULE, dict(fromto=[-0.06, sy, 0.56, 0.24, sy, 0.53], size=[0.065, 0, 0], mass=10.5, rgba=occ_p)))
        occ_parts.append((f"occ_sh_{sy:+.2f}", mujoco.mjtGeom.mjGEOM_CAPSULE, dict(fromto=[0.24, sy, 0.53, 0.45, sy, 0.16], size=[0.050, 0, 0], mass=6.5, rgba=occ_p)))
    for nm, gtype, kw in occ_parts:
        chassis.add_geom(name=nm, type=gtype, contype=0, conaffinity=0, **kw)

    chassis.add_camera(name="chase_cam",     pos=[-1.85, -1.10, 1.30], xyaxes=[0.51, -0.86, 0, 0.30, 0.18, 0.94])
    chassis.add_camera(name="driver_pov",    pos=[-0.02,  0.00, 1.24], xyaxes=[0, -1, 0, 0.18, 0, 0.98])
    chassis.add_camera(name="hero_cam",      pos=[ 1.75, -1.65, 1.35], xyaxes=[0.69,  0.72, 0, -0.26, 0.25, 0.93])
    chassis.add_camera(name="drive_closeup", pos=[-0.72, -0.86, 0.78], xyaxes=[0.78, -0.62, 0,  0.24, 0.30, 0.92])
    chassis.add_camera(name="explode_cam",   pos=[-1.55, -1.70, 1.35], xyaxes=[0.74, -0.67, 0,  0.26, 0.29, 0.92])

    # 24" Rear drive wheels + spinning 70 mm BLDC hub motors at 130 deg
    ang = math.radians(130.0)
    rx, rz = -0.153 + (0.3048 + 0.035) * math.cos(ang), 0.3048 + (0.3048 + 0.035) * math.sin(ang)
    for side, tag, m_w in ((1, "left", "m_wl"), (-1, "right", "m_wr")):
        wb = chassis.add_body(name=f"{tag}_wheel", pos=[-0.153, side * 0.2975, 0.3048])
        wb.add_joint(name=f"{tag}_wheel_hinge", type=mujoco.mjtJoint.mjJNT_HINGE, axis=[0, 1, 0], damping=0.10, armature=0.04)
        wb.add_geom(name=f"{tag}_tire_col", type=mujoco.mjtGeom.mjGEOM_CYLINDER, euler=[90, 0, 0], size=[0.3048, 0.0165, 0], mass=2.2, rgba=[0, 0, 0, 0], friction=[w.ground_mu, 0.001, 0.0005], solref=[0.008, 1.0])
        wb.add_geom(name=f"wheel_{tag}_cad", type=mujoco.mjtGeom.mjGEOM_MESH, meshname=m_w, material="mat_wheel", contype=0, conaffinity=0, mass=0.01)

        rb = chassis.add_body(name=f"{tag}_roller", pos=[rx, side * 0.2975, rz])
        rb.add_joint(name=f"{tag}_roller_hinge", type=mujoco.mjtJoint.mjJNT_HINGE, axis=[0, 1, 0], damping=0.02)
        rb.add_geom(name=f"roller_{tag}_cad", type=mujoco.mjtGeom.mjGEOM_MESH, meshname="m_hub", material="mat_hub_red", contype=0, conaffinity=0, mass=0.615)

    # 8" Front swiveling casters (40 mm trail, low scrub for crisp natural turning)
    for side, tag in ((1, "left"), (-1, "right")):
        fork = chassis.add_body(name=f"{tag}_fork", pos=[0.279 + 0.04, side * 0.241, 0.22])
        fork.add_joint(name=f"{tag}_swivel", type=mujoco.mjtJoint.mjJNT_HINGE, axis=[0, 0, 1], damping=0.04)
        fork.add_geom(name=f"{tag}_stem", type=mujoco.mjtGeom.mjGEOM_CAPSULE, fromto=[0, 0, 0.02, -0.04, 0, -0.1184], size=[0.008, 0, 0], mass=0.35, rgba=[0, 0, 0, 0], contype=0, conaffinity=0)
        cw = fork.add_body(name=f"{tag}_caster", pos=[-0.04, 0, -0.1184])
        cw.add_joint(name=f"{tag}_caster_spin", type=mujoco.mjtJoint.mjJNT_HINGE, axis=[0, 1, 0], damping=0.02)
        cw.add_geom(name=f"{tag}_caster_col", type=mujoco.mjtGeom.mjGEOM_CYLINDER, euler=[90, 0, 0], size=[0.1016, 0.012, 0], mass=0.65, rgba=[0, 0, 0, 0], friction=[0.55, 0.0005, 0.0002], solref=[0.008, 1.0])
        cw.add_geom(name=f"caster_{tag}_cad", type=mujoco.mjtGeom.mjGEOM_MESH, meshname="m_caster", material="mat_wheel", contype=0, conaffinity=0, mass=0.01)

    model = spec.compile()
    data = mujoco.MjData(model)
    return model, data, w


def build_explode_showcase() -> tuple[mujoco.MjModel, mujoco.MjData]:
    """Pure kinematic 3D CAD Exploded Showcase (zero gravity, fixed anchor, smooth 0%->100% slider)."""
    spec = mujoco.MjSpec()
    spec.modelname = "cruiser_iii_v10_exploded_cad"
    spec.option.timestep = 0.005
    spec.option.gravity = [0.0, 0.0, 0.0]

    _setup_visuals_and_meshes(spec, wet=False, grass=False)
    spec.worldbody.add_geom(name="studio_floor", type=mujoco.mjtGeom.mjGEOM_PLANE, size=[40, 40, 0.1], material="ground_mat", contype=0, conaffinity=0)

    # Fixed floating anchor (no freejoint -> never flips, never clips!)
    anchor = spec.worldbody.add_body(name="chassis", pos=[0, 0, 0.24])
    anchor.add_geom(name="chassis_cad", type=mujoco.mjtGeom.mjGEOM_MESH, meshname="m_chassis", material="mat_chassis", contype=0, conaffinity=0, mass=1.0)

    anchor.add_camera(name="explode_cam",   pos=[-1.55, -1.70, 1.25], xyaxes=[0.74, -0.67, 0,  0.26, 0.29, 0.92])
    anchor.add_camera(name="hero_cam",      pos=[ 1.75, -1.65, 1.25], xyaxes=[0.69,  0.72, 0, -0.26, 0.25, 0.93])
    anchor.add_camera(name="drive_closeup", pos=[-0.85, -1.05, 0.85], xyaxes=[0.78, -0.62, 0,  0.24, 0.30, 0.92])
    anchor.add_camera(name="chase_cam",     pos=[-1.85, -1.10, 1.20], xyaxes=[0.51, -0.86, 0,  0.30, 0.18, 0.94])
    anchor.add_camera(name="driver_pov",    pos=[-0.02,  0.00, 1.24], xyaxes=[0, -1, 0, 0.18, 0, 0.98])

    def add_part(name, base_pos, mesh, mat_name):
        vec = EXPLODE_OFFSETS[name]
        dist = math.hypot(*vec)
        axis = [v / dist for v in vec]
        b = anchor.add_body(name=f"exp_{name}", pos=list(base_pos))
        b.add_joint(name=f"exp_{name}_jnt", type=mujoco.mjtJoint.mjJNT_SLIDE, axis=axis, range=[0.0, dist], limited=True, damping=20.0, armature=1.0)
        b.add_geom(name=f"{name}_cad", type=mujoco.mjtGeom.mjGEOM_MESH, meshname=mesh, material=mat_name, contype=0, conaffinity=0, mass=1.0)

    ang = math.radians(130.0)
    rx, rz = -0.153 + (0.3048 + 0.035) * math.cos(ang), 0.3048 + (0.3048 + 0.035) * math.sin(ang)
    add_part("drive_left",   (0, 0, 0),                   "m_drv_l",  "mat_pacf")
    add_part("drive_right",  (0, 0, 0),                   "m_drv_r",  "mat_pacf")
    add_part("underseat",    (0, 0, 0),                   "m_under",  "mat_underseat")
    add_part("joystick",     (0, 0, 0),                   "m_joy",    "mat_pacf")
    add_part("wheel_left",   (-0.153,  0.2975, 0.3048),   "m_wl",     "mat_wheel")
    add_part("wheel_right",  (-0.153, -0.2975, 0.3048),   "m_wr",     "mat_wheel")
    add_part("roller_left",  (rx,      0.2975, rz),       "m_hub",    "mat_hub_red")
    add_part("roller_right", (rx,     -0.2975, rz),       "m_hub",    "mat_hub_red")
    add_part("caster_left",  ( 0.279,  0.2410, 0.1016),   "m_caster", "mat_wheel")
    add_part("caster_right", ( 0.279, -0.2410, 0.1016),   "m_caster", "mat_wheel")

    model = spec.compile()
    data = mujoco.MjData(model)
    return model, data
