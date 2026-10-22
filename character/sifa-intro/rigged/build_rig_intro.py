"""Rigged Blender intro: Sifa (MakeHuman) walks in, turns, sits in a gaming chair and waves,
driven by CMU motion capture retargeted onto the MPFB cmu_mb rig.

Run: blender -b sifa_human.blend -P build_rig_intro.py -- <out_dir> [preview]
"""
import math
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
PREVIEW = len(argv) > 1 and argv[1] == "preview"

FPS = 24
DURATION = 27.0
END = int(DURATION * FPS)
SRC_FPS = 120

# timeline (output seconds)
T_WALK = 0.9            # walk starts
WALK_SRC = (0.55, 3.2)  # 113_25 source window
SIT_SRC0 = 0.5          # 113_15 source time where the walk hands over
SIT_SETTLE = 3.2        # 113_15 source time where she is seated and still
T_SIT0 = T_WALK + (WALK_SRC[1] - WALK_SRC[0])          # hand-over time
T_SEATED = T_SIT0 + (SIT_SETTLE - SIT_SRC0)            # seated
BLEND = 0.35
VOICE_START = T_SEATED + 0.2
WAVE_SRC = (2.9, 4.7)   # 143_25 window containing the wave
T_WAVE = VOICE_START - 0.2
WAVE_RAMP = 0.45
SEATED_YAW_TARGET = -90.0   # face the camera (camera looks along +Y)

scene = bpy.context.scene
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, END


def out_frame(t):
    return int(round(t * FPS)) + 1


# ---------------------------------------------------------------- character
rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
for pb in rig.pose.bones:
    pb.rotation_mode = "QUATERNION"


def tint(obj_key, color, value=1.0, sat=1.0):
    """Multiply an MPFB material's base colour by a tint (keeps fabric/hair texture)."""
    for o in bpy.data.objects:
        if o.type != "MESH" or obj_key not in o.name:
            continue
        for m in o.data.materials:
            nt = m.node_tree
            bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if not bsdf or not bsdf.inputs["Base Color"].is_linked:
                if bsdf:
                    bsdf.inputs["Base Color"].default_value = (*color, 1)
                continue
            link = bsdf.inputs["Base Color"].links[0]
            src = link.from_socket
            hsv = nt.nodes.new("ShaderNodeHueSaturation")
            hsv.inputs["Saturation"].default_value = sat
            hsv.inputs["Value"].default_value = value
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs[0].default_value = 1.0
            mix.inputs[7].default_value = (*color, 1)
            nt.links.new(src, hsv.inputs["Color"])
            nt.links.new(hsv.outputs["Color"], mix.inputs[6])
            nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])


tint("long01", (1.0, 0.86, 0.6), value=2.4, sat=0.35)          # blonde
tint("casualsuit", (0.16, 0.15, 0.2), value=0.55, sat=0.2)     # black top + dark joggers
tint("shoes", (0.95, 0.9, 1.0), value=1.6, sat=0.0)            # light sneakers

# ---------------------------------------------------------------- mocap sources
def load_bvh(name):
    bpy.ops.import_anim.bvh(filepath=f"/opt/mocap/{name}.bvh", global_scale=1.0, frame_start=1,
                            use_fps_scale=False, update_scene_fps=False, update_scene_duration=False,
                            rotate_mode="NATIVE", axis_forward="-Z", axis_up="Y")
    o = bpy.context.object
    o.name = "src_" + name
    o.hide_render = True
    return o


walk = load_bvh("113_25")
sit = load_bvh("113_15")
wave = load_bvh("143_25")
scene.frame_set(1)

tb = rig.data.bones
leg_t = (rig.matrix_world @ tb["LeftUpLeg"].head_local - rig.matrix_world @ tb["LeftFoot"].head_local).length
leg_s = (sit.data.bones["LeftUpLeg"].head_local - sit.data.bones["LeftFoot"].head_local).length
SCALE = leg_t / leg_s
print("SCALE", SCALE)


def sample(src, t):
    """World matrices of every source bone at source time t (seconds)."""
    f = 1 + t * SRC_FPS
    scene.frame_set(int(f), subframe=f - int(f))
    W = src.matrix_world
    return {pb.name: W @ pb.matrix for pb in src.pose.bones}


def hips_and_yaw(src, t):
    m = sample(src, t)
    L, R = m["LeftUpLeg"].translation, m["RightUpLeg"].translation
    fwd = Vector((0, 0, 1)).cross(R - L)
    return m["Hips"].translation.copy(), math.degrees(math.atan2(fwd.y, fwd.x))


# place the sit clip: seated pose faces the camera and sits on the chair at the origin
for o in (walk, sit, wave):
    o.scale = (SCALE,) * 3
bpy.context.view_layer.update()
_, seated_yaw = hips_and_yaw(sit, SIT_SETTLE + 0.4)
sit.rotation_euler[2] = math.radians(SEATED_YAW_TARGET - seated_yaw)
bpy.context.view_layer.update()
seated_hips, _ = hips_and_yaw(sit, SIT_SETTLE + 0.4)
sit.location = (-seated_hips.x, -seated_hips.y, 0)
bpy.context.view_layer.update()
seated_hips, _ = hips_and_yaw(sit, SIT_SETTLE + 0.4)
SEAT_Z = seated_hips.z
print("SEATED HIPS", seated_hips)

# place the walk clip so its last frame lines up with the start of the sit clip
hand_hips, hand_yaw = hips_and_yaw(sit, SIT_SRC0)
_, walk_yaw = hips_and_yaw(walk, WALK_SRC[1])
walk.rotation_euler[2] = math.radians(hand_yaw - walk_yaw)
bpy.context.view_layer.update()
walk_end_hips, _ = hips_and_yaw(walk, WALK_SRC[1])
walk.location = (hand_hips.x - walk_end_hips.x, hand_hips.y - walk_end_hips.y, 0)
bpy.context.view_layer.update()
print("WALK START", hips_and_yaw(walk, WALK_SRC[0]))

# ---------------------------------------------------------------- retarget calibration
SRC_NAME = {"LeftHandFinger1": "LeftHandIndex1", "RightHandFinger1": "RightHandIndex1"}
order = [b for b in tb]  # Blender stores bones parent-first


def rest_world(arm, bone):
    return arm.matrix_world @ bone.matrix_local


def calib(src):
    """Per-bone offset C so that target_world_rot = source_world_rot @ C."""
    C = {}
    for b in order:
        sb = src.data.bones.get(SRC_NAME.get(b.name, b.name))
        if sb is None:
            continue
        rt = rest_world(rig, b).to_quaternion()
        dt = (rest_world(rig, b).to_3x3() @ Vector((0, 1, 0))).normalized()
        rs = rest_world(src, sb).to_quaternion()
        ds = (rest_world(src, sb).to_3x3() @ Vector((0, 1, 0))).normalized()
        t_pose = dt.rotation_difference(ds) @ rt          # target bone aligned to the source T-pose
        C[b.name] = rs.inverted() @ t_pose
    return C


CAL = {s.name: calib(s) for s in (walk, sit, wave)}


def target_rots(src, t):
    m = sample(src, t)
    cal = CAL[src.name]
    rots = {}
    for b in order:
        sname = SRC_NAME.get(b.name, b.name)
        if b.name in cal and sname in m:
            rots[b.name] = m[sname].to_quaternion() @ cal[b.name]
    return rots, m["Hips"].translation.copy()


def blend(a, b, w):
    ra, pa = a
    rb, pb = b
    return {k: ra[k].slerp(rb[k], w) for k in ra}, pa.lerp(pb, w)


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


WAVE_BONES = ["RightShoulder", "RightArm", "RightForeArm", "RightHand", "RightFingerBase", "RightHandFinger1", "RThumb"]


def pose_at(t):
    """Target world rotations + hips position at output time t."""
    if t < T_SIT0:
        st = WALK_SRC[0] + max(0.0, t - T_WALK)
        pose = target_rots(walk, min(st, WALK_SRC[1]))
        if t > T_SIT0 - BLEND:
            w = smooth((t - (T_SIT0 - BLEND)) / BLEND)
            pose = blend(pose, target_rots(sit, SIT_SRC0), w)
        return pose
    if t < T_SEATED:
        return target_rots(sit, SIT_SRC0 + (t - T_SIT0))
    # seated idle: drift gently around the settled part of the sit clip
    st = SIT_SETTLE + 0.55 + 0.45 * math.sin((t - T_SEATED) * 2 * math.pi / 7.0 - math.pi / 2)
    rots, hips = target_rots(sit, st)
    # wave overlay on the right arm, relative to the chest
    if T_WAVE <= t <= T_WAVE + (WAVE_SRC[1] - WAVE_SRC[0]):
        local_t = t - T_WAVE
        dur = WAVE_SRC[1] - WAVE_SRC[0]
        w = smooth(local_t / WAVE_RAMP) * smooth((dur - local_t) / WAVE_RAMP)
        wr, _ = target_rots(wave, WAVE_SRC[0] + local_t)
        chest_t, chest_w = rots["Spine1"], wr["Spine1"]
        for name in WAVE_BONES:
            if name in wr:
                rel = chest_w.inverted() @ wr[name]
                rots[name] = rots[name].slerp(chest_t @ rel, w)
    return rots, hips


def apply(rots, hips_world, frame):
    inv = rig.matrix_world.inverted()
    inv_rot = inv.to_quaternion()
    pose_arm = {}
    for b in order:
        pb = rig.pose.bones[b.name]
        if b.parent:
            base = pose_arm[b.parent.name] @ (b.parent.matrix_local.inverted() @ b.matrix_local)
        else:
            base = b.matrix_local.copy()
        if b.name in rots:
            r = (inv_rot @ rots[b.name]).to_matrix().to_4x4()
            loc = (inv @ hips_world) if b.parent is None else base.translation
            desired = Matrix.Translation(loc) @ r
        else:
            desired = base.copy()
        basis = base.inverted() @ desired
        pb.rotation_quaternion = basis.to_quaternion()
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        if b.parent is None:
            pb.location = basis.translation
            pb.keyframe_insert("location", frame=frame)
        pose_arm[b.name] = desired


print("RETARGETING", END, "frames")
for fr in range(1, END + 1):
    t = (fr - 1) / FPS
    rots, hips = pose_at(max(t, T_WALK))
    apply(rots, hips, fr)
# hide the character until she walks in (she starts off-screen anyway)
for o in (walk, sit, wave):
    o.animation_data_clear()
    bpy.data.objects.remove(o)

# ---------------------------------------------------------------- render settings
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 8 if PREVIEW else 48
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = (960, 540) if PREVIEW else (1920, 1080)
scene.render.use_persistent_data = True
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = f"{OUT}/frame_"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Punchy"
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.004, 0.008, 1)


def mat(name, color, rough=0.6, emit=None, strength=0.0, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def box(name, loc, size, m, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m)
    if bevel:
        bpy.ops.object.transform_apply(scale=True)
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 4
        o.modifiers.new("smooth", "WEIGHTED_NORMAL")
        bpy.ops.object.shade_smooth()
    return o


def cyl(name, loc, r, h, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=32)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


# ---------------------------------------------------------------- room
wall = mat("Wall", (0.03, 0.03, 0.04), 0.85)
floor = mat("Floor", (0.025, 0.025, 0.03), 0.3)
box("Floor", (0, 0.5, -0.05), (16, 12, 0.1), floor)
box("BackWall", (0, 2.2, 2), (16, 0.1, 4.2), wall)
box("LeftWall", (-3.8, 0, 2), (0.1, 12, 4.2), wall)
# acoustic panels
panel = mat("Panel", (0.02, 0.02, 0.025), 0.95)
for i in range(4):
    for j in range(3):
        box(f"Panel{i}{j}", (1.6 + i * 0.5, 2.13, 1.1 + j * 0.5), (0.45, 0.06, 0.45), panel, 0.01)

led = mat("LED", (0, 0, 0), 1, (0.55, 0.15, 1.0), 25)
ledb = led.node_tree.nodes["Principled BSDF"]
box("LED_top", (0, 2.13, 3.3), (12, 0.04, 0.05), led)
box("LED_floor", (0, 2.13, 0.06), (12, 0.04, 0.04), led)
box("LED_side", (-3.73, 0.0, 3.3), (0.04, 8, 0.05), led)
palette = [(0.55, 0.15, 1.0), (0.1, 0.8, 1.0), (1.0, 0.15, 0.6)]
ledb.inputs["Emission Strength"].default_value = 0
ledb.inputs["Emission Strength"].keyframe_insert("default_value", frame=1)
for i, (t, v) in enumerate(((0.25, 25), (0.35, 3), (0.45, 25), (0.55, 6), (0.7, 25))):
    ledb.inputs["Emission Strength"].default_value = v
    ledb.inputs["Emission Strength"].keyframe_insert("default_value", frame=out_frame(t))
for i in range(int(DURATION // 6) + 2):
    ledb.inputs["Emission Color"].default_value = (*palette[i % 3], 1)
    ledb.inputs["Emission Color"].keyframe_insert("default_value", frame=out_frame(i * 6))


def neon(name, body, loc, size, color, peak, t0):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, 0))
    t = bpy.context.object
    t.name = name
    t.data.body = body
    t.data.size = size
    t.data.extrude = 0.015
    t.data.bevel_depth = 0.006
    t.data.align_x = "CENTER"
    m = mat(name + "M", color, 0.3, color, 0)
    t.data.materials.append(m)
    s = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for tt, v in ((t0 - 0.05, 0), (t0, peak), (t0 + 0.08, 3), (t0 + 0.16, peak), (t0 + 0.24, 6), (t0 + 0.35, peak)):
        s.default_value = v
        s.keyframe_insert("default_value", frame=max(1, out_frame(tt)))


neon("NeonSIFA", "SIFA", (0, 2.1, 2.25), 0.75, (0.75, 0.3, 1.0), 28, 0.8)
neon("NeonSub", "THE FIRST SI AGENT", (0, 2.1, 1.98), 0.17, (0.1, 0.85, 1.0), 18, 1.3)

# desk with monitor + keyboard on the left
wood = mat("Desk", (0.18, 0.1, 0.05), 0.45)
dark = mat("DarkPlastic", (0.01, 0.01, 0.012), 0.35)
box("DeskTop", (-2.2, 0.6, 0.74), (1.6, 0.75, 0.05), wood, 0.01)
box("DeskLegL", (-2.95, 0.6, 0.37), (0.05, 0.7, 0.72), dark)
box("DeskLegR", (-1.45, 0.6, 0.37), (0.05, 0.7, 0.72), dark)
screen = mat("Screen", (0, 0, 0), 0.2, (0.05, 0.06, 0.12), 1.0)
mon = box("Monitor", (-2.25, 0.85, 1.12), (1.0, 0.05, 0.56), dark, 0.01, rot=(0, 0, math.radians(25)))
scr = box("MonitorScreen", (-2.24, 0.82, 1.12), (0.94, 0.01, 0.5), screen, rot=(0, 0, math.radians(25)))
bpy.ops.object.text_add(location=(-2.22, 0.80, 1.12), rotation=(math.radians(90), 0, math.radians(25)))
gt = bpy.context.object
gt.data.body = "GEARS OF WAR\nE-DAY"
gt.data.size = 0.085
gt.data.align_x = "CENTER"
gt.data.align_y = "CENTER"
gt.data.materials.append(mat("GearsTitle", (0.8, 0.05, 0.03), 0.4, (1.0, 0.08, 0.04), 6))
box("Keyboard", (-2.1, 0.45, 0.78), (0.5, 0.16, 0.025), mat("KB", (0.02, 0.02, 0.02), 0.4, (0.6, 0.2, 1.0), 1.5), 0.005)

# shelves with glowing collectibles
shelf = mat("Shelf", (0.05, 0.05, 0.06), 0.5)
for x in (-1.9, 2.0):
    box(f"Shelf{x}", (x, 2.02, 2.0), (1.2, 0.26, 0.04), shelf, 0.005)
    for j, c in enumerate(palette):
        cyl(f"Prop{x}{j}", (x - 0.35 + j * 0.35, 2.02, 2.14), 0.06, 0.22, mat(f"P{x}{j}", (0.02, 0.02, 0.02), 0.3, c, 5))

# ---------------------------------------------------------------- gaming chair (seat under her seated hips)
SEAT_H = SEAT_Z - 0.12
blk = mat("ChairBlack", (0.012, 0.012, 0.015), 0.4)
pur = mat("ChairPurple", (0.22, 0.04, 0.5), 0.45)
chrome = mat("Chrome", (0.6, 0.6, 0.65), 0.2, metal=1.0)
cy = 0.08
box("Seat", (0, cy, SEAT_H - 0.05), (0.56, 0.54, 0.12), blk, 0.04)
box("SeatSideL", (-0.26, cy, SEAT_H), (0.08, 0.52, 0.12), pur, 0.03)
box("SeatSideR", (0.26, cy, SEAT_H), (0.08, 0.52, 0.12), pur, 0.03)
box("Back", (0, cy + 0.32, SEAT_H + 0.45), (0.54, 0.12, 0.85), blk, 0.05, rot=(math.radians(-8), 0, 0))
box("BackWingL", (-0.25, cy + 0.3, SEAT_H + 0.45), (0.08, 0.13, 0.8), pur, 0.03, rot=(math.radians(-8), 0, 0))
box("BackWingR", (0.25, cy + 0.3, SEAT_H + 0.45), (0.08, 0.13, 0.8), pur, 0.03, rot=(math.radians(-8), 0, 0))
box("Headrest", (0, cy + 0.36, SEAT_H + 0.82), (0.26, 0.06, 0.12), pur, 0.03, rot=(math.radians(-8), 0, 0))
for sx in (-1, 1):
    box(f"Arm{sx}", (sx * 0.33, cy - 0.02, SEAT_H + 0.2), (0.07, 0.3, 0.04), blk, 0.015)
    cyl(f"ArmPost{sx}", (sx * 0.33, cy + 0.04, SEAT_H + 0.08), 0.02, 0.22, blk)
cyl("GasLift", (0, cy, (SEAT_H - 0.1) / 2 + 0.06), 0.03, SEAT_H - 0.12, chrome)
for a in range(5):
    ang = a * 2 * math.pi / 5 + math.pi / 2
    leg = box(f"Base{a}", (0.17 * math.cos(ang), cy + 0.17 * math.sin(ang), 0.07), (0.34, 0.05, 0.04), blk, 0.01)
    leg.rotation_euler[2] = ang
    cyl(f"Wheel{a}", (0.33 * math.cos(ang), cy + 0.33 * math.sin(ang), 0.03), 0.03, 0.03, blk, rot=(0, math.radians(90), 0))

# ---------------------------------------------------------------- lights
def area(name, loc, target, color, energy, size):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.name = name
    l.data.color = color
    l.data.energy = energy
    l.data.size = size
    c = l.constraints.new("TRACK_TO")
    e = bpy.data.objects.new(name + "_t", None)
    scene.collection.objects.link(e)
    e.location = target
    c.target = e
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    return l


area("Key", (1.4, -2.6, 2.4), (0, 0, 1.0), (1.0, 0.94, 0.9), 260, 1.6)
area("Fill", (-2.0, -2.2, 1.6), (0, 0, 1.0), (0.55, 0.45, 1.0), 90, 2.0)
area("RimL", (-1.6, 1.6, 2.4), (0, 0, 1.2), (0.6, 0.2, 1.0), 220, 0.8)
area("RimR", (1.8, 1.6, 2.4), (0, 0, 1.2), (0.1, 0.8, 1.0), 220, 0.8)

# ---------------------------------------------------------------- camera
bpy.ops.object.camera_add()
cam = bpy.context.object
scene.camera = cam
cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 2.8
tgt = bpy.data.objects.new("CamTarget", None)
scene.collection.objects.link(tgt)
cam.data.dof.focus_object = tgt
tc = cam.constraints.new("TRACK_TO")
tc.target = tgt
tc.track_axis = "TRACK_NEGATIVE_Z"
tc.up_axis = "UP_Y"
for t, loc, aim, lens in ((0, (-0.4, -5.6, 1.45), (-0.6, 0.4, 1.2), 50),
                          (T_SIT0, (0.4, -5.0, 1.4), (0.2, 0.3, 1.05), 34),
                          (T_SEATED, (0.3, -4.4, 1.35), (0.0, 0.2, 0.95), 30),
                          (DURATION, (0.05, -3.4, 1.2), (0.0, 0.1, 0.95), 36)):
    cam.location = loc
    tgt.location = aim
    cam.data.lens = lens
    cam.keyframe_insert("location", frame=out_frame(t))
    tgt.keyframe_insert("location", frame=out_frame(t))
    cam.data.keyframe_insert("lens", frame=out_frame(t))

# ---------------------------------------------------------------- titles (camera-attached)
def cam_text(name, body, loc, size, color, t_in, t_out=None):
    bpy.ops.object.text_add()
    t = bpy.context.object
    t.name = name
    t.data.body = body
    t.data.size = size
    t.parent = cam
    t.location = loc
    t.data.materials.append(mat(name + "M", color, 0.5, color, 4))
    for tt, hidden in ((0, True), (t_in, False)) + (((t_out, True),) if t_out else ()):
        t.hide_render = hidden
        t.keyframe_insert("hide_render", frame=max(1, out_frame(tt)))


cam_text("LT1", "SIFA  |  The First SI Agent", (-0.48, -0.3, -1.0), 0.032, (1, 1, 1), VOICE_START + 0.4, VOICE_START + 7)
cam_text("LT2", "TODAY: GEARS OF WAR: E-DAY  -  Honest Walkthrough", (-0.48, -0.3, -1.0), 0.026, (0.2, 0.9, 1.0), VOICE_START + 7.2)

with open(f"{OUT}/timing.txt", "w") as fh:
    fh.write(f"voice_start={VOICE_START:.3f}\nseated={T_SEATED:.3f}\n")
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/sifa_rig_intro.blend")
print("BUILT", END, "frames; voice starts at", VOICE_START)
