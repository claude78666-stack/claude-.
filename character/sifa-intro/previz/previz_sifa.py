"""Blender previz of the new Sifa format: a stand-in Sifa in her gaming room who waves, does the
"yes" hand pump on her key line, talks with her hands, then swivels her chair to the monitor and
looks at the screen.

Run: blender -b -P previz_sifa.py -- <out_dir> <shot> [preview]
  shot = wide  (960x540, 13 s: wave, talk, yes-pump, swivel and look at the monitor)
         face  (540x540, 10 s loop for the bottom-left facecam: talking gestures)
A preview of staging, gestures and timing only; the final Sifa is the photoreal one.
"""
import math
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, SHOT = argv[0], argv[1]
PREVIEW = len(argv) > 2 and argv[2] == "preview"
SCREEN_IMG = argv[3] if len(argv) > 3 else None
FPS = 24
DUR = 13.0 if SHOT == "wide" else 10.0
f = lambda t: int(round(t * FPS)) + 1
D = math.radians

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, int(DUR * FPS)
scene.frame_step = 2 if PREVIEW else 1  # preview: 12 fps, doubled to 24 in the edit
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 6 if PREVIEW else 20
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = (960, 540) if SHOT == "wide" else (540, 540)
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = f"{OUT}/{SHOT}_"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Punchy"
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.008, 0.02, 1)


def mat(name, color, rough=0.6, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def box(name, loc, size, m, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name, o.scale = name, (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def blob(name, loc, scale, m, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc)
    o = bpy.context.object
    o.name, o.scale = name, scale
    o.data.materials.append(m)
    smooth(o)
    if parent:
        o.parent = parent
    return o


def joint(name, loc, parent=None):
    """An empty at a joint; meshes hang off it, and its rotation is what gets animated."""
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.03
    scene.collection.objects.link(e)
    e.location = loc
    e.rotation_mode = "XYZ"
    if parent:
        e.parent = parent
    return e


def limb(name, parent_joint, length, radius, m):
    """Capsule hanging down (-Z) from a joint."""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=(0, 0, -length / 2), vertices=20)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    smooth(o)
    o.parent = parent_joint
    for z in (0, -length):
        blob(name + "_cap", (0, 0, z), (radius,) * 3, m, parent_joint)
    return o


# ---------------------------------------------------------------- materials
hoodie = mat("Hoodie", (0.02, 0.02, 0.025), 0.8)
trim = mat("Trim", (0.5, 0.35, 0.8), 0.5)
skin = mat("Skin", (0.8, 0.6, 0.5), 0.45)
hair = mat("Hair", (0.72, 0.52, 0.24), 0.45)
dark = mat("Dark", (0.02, 0.02, 0.03), 0.4)
chair_m = mat("Chair", (0.05, 0.04, 0.07), 0.35)
chair_acc = mat("ChairAccent", (0.35, 0.15, 0.6), 0.4)
wall = mat("Wall", (0.05, 0.03, 0.08), 0.9)
floor_m = mat("Floor", (0.08, 0.08, 0.1), 0.6)
desk_m = mat("Desk", (0.25, 0.15, 0.1), 0.5)
neon_p = mat("NeonP", (0.6, 0.2, 1), 0.3, (0.75, 0.3, 1), 18)
neon_c = mat("NeonC", (0.1, 0.8, 1), 0.3, (0.1, 0.85, 1), 12)

# ---------------------------------------------------------------- room
box("Floor", (0, 0, -0.01), (8, 8, 0.02), floor_m)
box("BackWall", (0, 1.4, 1.6), (8, 0.05, 3.2), wall)
box("SideWall", (2.4, 0, 1.6), (0.05, 8, 3.2), wall)
bpy.ops.object.text_add(location=(-0.5, 1.36, 1.6), rotation=(D(90), 0, 0))
sign = bpy.context.object
sign.data.body = "SIFA"
sign.data.size = 0.4
sign.data.extrude = 0.01
sign.data.materials.append(neon_p)
box("StripTop", (0, 1.37, 3.1), (6, 0.02, 0.03), neon_c)
box("StripFloor", (0, 1.37, 0.03), (6, 0.02, 0.03), neon_c)
for i, (x, z) in enumerate(((-1.6, 1.0), (-1.6, 1.4), (-1.6, 1.8))):
    box(f"Shelf{i}", (x, 1.25, z), (0.7, 0.25, 0.03), desk_m)
    box(f"Box{i}", (x + 0.1 * (i - 1), 1.25, z + 0.1), (0.12, 0.12, 0.17), neon_p if i == 1 else trim)

# desk, monitor and laptop to Sifa's left (+X), facing her
box("Desk", (1.25, -0.05, 0.74), (0.7, 1.5, 0.05), desk_m)
for y in (-0.7, 0.6):
    box(f"DeskLeg{y}", (1.25, y, 0.37), (0.05, 0.05, 0.74), dark)
box("Monitor", (1.45, 0.0, 1.15), (0.04, 0.95, 0.55), dark)
screen = mat("Screen", (0.1, 0.1, 0.1), 0.3, (0.6, 0.3, 0.2), 4)
if SCREEN_IMG:
    nt = screen.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(SCREEN_IMG)
    b = nt.nodes["Principled BSDF"]
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
bpy.ops.mesh.primitive_plane_add(size=1, location=(1.425, 0.0, 1.15), rotation=(D(90), 0, D(-90)))
scr = bpy.context.object
scr.scale = (0.9, 0.5, 1)
scr.data.materials.append(screen)
box("Laptop", (1.12, 0.05, 0.78), (0.3, 0.38, 0.02), dark)
box("LaptopLid", (1.27, 0.05, 0.9), (0.02, 0.38, 0.24), dark, rot=(0, D(-12), 0))
box("Keyboard", (1.1, -0.45, 0.78), (0.18, 0.45, 0.02), neon_p)

# ---------------------------------------------------------------- chair (swivels) and Sifa
pivot = joint("ChairPivot", (0, 0, 0))
box("ChairBase", (0, 0, 0.05), (0.6, 0.6, 0.04), chair_m)
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.42, location=(0, 0, 0.28))
bpy.context.object.data.materials.append(dark)
box("Seat", (0, 0, 0.5), (0.55, 0.55, 0.1), chair_m, pivot)
box("Back", (0, 0.27, 1.0), (0.52, 0.09, 0.9), chair_m, pivot, rot=(D(-8), 0, 0))
box("BackStripe", (0, 0.22, 1.05), (0.12, 0.01, 0.8), chair_acc, pivot, rot=(D(-8), 0, 0))
for x in (-0.3, 0.3):
    box(f"Arm{x}", (x, -0.05, 0.72), (0.06, 0.42, 0.05), chair_m, pivot)

pelvis = joint("Pelvis", (0, 0.02, 0.6), pivot)
spine = joint("Spine", (0, 0, 0.02), pelvis)
blob("Hips", (0, 0, 0), (0.18, 0.13, 0.1), hoodie, pelvis)
blob("Torso", (0, 0, 0.27), (0.2, 0.13, 0.28), hoodie, spine)
box("HoodieStripe", (0.06, -0.125, 0.25), (0.012, 0.01, 0.35), trim, spine)
box("HoodieStripe2", (-0.06, -0.125, 0.25), (0.012, 0.01, 0.35), trim, spine)
neck = joint("Neck", (0, 0, 0.52), spine)
blob("NeckMesh", (0, 0, 0.04), (0.05, 0.05, 0.06), skin, neck)
head = joint("Head", (0, 0, 0.1), neck)
blob("HeadMesh", (0, 0, 0.1), (0.095, 0.105, 0.125), skin, head)
blob("HairBack", (0, 0.03, 0.12), (0.115, 0.1, 0.14), hair, head)
blob("HairFall", (0, 0.04, -0.13), (0.15, 0.07, 0.22), hair, head)
for x in (-0.035, 0.035):
    blob(f"Eye{x}", (x, -0.088, 0.12), (0.013, 0.008, 0.01), dark, head)
mouth = blob("Mouth", (0, -0.09, 0.045), (0.022, 0.006, 0.006), mat("Lips", (0.5, 0.2, 0.2), 0.4), head)
blob("Headphones", (0, 0.0, -0.06), (0.11, 0.09, 0.03), dark, neck)

arms = {}
for side, sx in (("R", -1), ("L", 1)):
    sh = joint(f"Shoulder{side}", (0.2 * sx, 0, 0.45), spine)
    limb(f"UpperArm{side}", sh, 0.27, 0.045, hoodie)
    el = joint(f"Elbow{side}", (0, 0, -0.27), sh)
    limb(f"Forearm{side}", el, 0.24, 0.038, hoodie)
    wr = joint(f"Wrist{side}", (0, 0, -0.25), el)
    blob(f"Hand{side}", (0, 0, -0.05), (0.035, 0.018, 0.05), skin, wr)
    fingers = joint(f"Fingers{side}", (0, 0, -0.09), wr)
    blob(f"FingerMesh{side}", (0, 0, -0.03), (0.032, 0.016, 0.035), skin, fingers)
    arms[side] = (sh, el, wr, fingers)
for side, sx in (("R", -1), ("L", 1)):
    hip = joint(f"Hip{side}", (0.09 * sx, 0, 0), pelvis)
    hip.rotation_euler = (D(90), 0, 0)  # thighs forward, toward the camera
    limb(f"Thigh{side}", hip, 0.42, 0.065, hoodie)
    knee = joint(f"Knee{side}", (0, 0, -0.42), hip)
    knee.rotation_euler = (D(-90), 0, 0)
    limb(f"Shin{side}", knee, 0.45, 0.055, hoodie)
    blob(f"Shoe{side}", (0, -0.05, -0.47), (0.05, 0.11, 0.04), dark, knee)


# ---------------------------------------------------------------- animation helpers
def key(obj, t, rot=None, loc=None):
    if rot is not None:
        obj.rotation_euler = tuple(D(a) for a in rot)
        obj.keyframe_insert("rotation_euler", frame=f(t))
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=f(t))


REST_UPPER = {"R": (-25, 8, -6), "L": (-25, -8, 6)}   # forearms resting on the armrests
REST_ELBOW = (-70, 0, 0)


def rest(side, t):
    sh, el, wr, fi = arms[side]
    key(sh, t, REST_UPPER[side])
    key(el, t, REST_ELBOW)
    key(wr, t, (10, 0, 0))
    key(fi, t, (0, 0, 0))


def talk_gesture(side, t, kind):
    """Short, natural hand moves while talking (about 1.6 s each)."""
    sh, el, wr, fi = arms[side]
    s = -1 if side == "R" else 1
    if kind == "open":       # open palm out to the side, explaining
        key(sh, t + 0.3, (-45, 20 * -s, -10 * s)); key(el, t + 0.3, (-85, 0, 0)); key(wr, t + 0.3, (30, 0, 40 * s))
        key(sh, t + 1.0, (-40, 26 * -s, -10 * s)); key(wr, t + 1.0, (25, 0, 55 * s))
    elif kind == "point":    # points toward the monitor
        key(sh, t + 0.35, (-70, -5, 15)); key(el, t + 0.35, (-20, 0, 0)); key(fi, t + 0.35, (-10, 0, 0))
        key(sh, t + 1.1, (-72, -5, 18))
    elif kind == "count":    # counting on fingers
        key(sh, t + 0.3, (-55, 10 * -s, 0)); key(el, t + 0.3, (-100, 0, 0)); key(fi, t + 0.3, (-60, 0, 0))
        key(fi, t + 0.7, (0, 0, 0)); key(fi, t + 1.1, (-60, 0, 0))
    elif kind == "both":     # both hands out, "here's the thing"
        for sd, ss in (("R", -1), ("L", 1)):
            a = arms[sd]
            key(a[0], t + 0.35, (-50, 25 * -ss, -15 * ss)); key(a[1], t + 0.35, (-80, 0, 0)); key(a[2], t + 0.35, (35, 0, 45 * ss))
            key(a[0], t + 1.1, (-48, 30 * -ss, -15 * ss))


def yes_pump(t, dur=2.0):
    """The reference 'nodding yes' hand: right hand raised to chest height, fingers loosely curled,
    pumped up and down about 3 times a second while she lands her point."""
    sh, el, wr, fi = arms["R"]
    key(sh, t, REST_UPPER["R"]); key(el, t, REST_ELBOW)
    key(sh, t + 0.3, (-62, 12, -4)); key(el, t + 0.3, (-95, 0, 0)); key(fi, t + 0.3, (-55, 0, 0)); key(wr, t + 0.3, (5, 0, 0))
    n = int(dur * 3)
    for i in range(n):
        tt = t + 0.35 + i / 3
        key(el, tt, (-82, 0, 0)); key(el, tt + 1 / 6, (-104, 0, 0))
        key(head, tt, (6, 0, 0)); key(head, tt + 1 / 6, (-2, 0, 0))   # head nods with the hand
    key(head, t + 0.35 + n / 3, (0, 0, 0))


def wave(t, dur=1.8):
    sh, el, wr, fi = arms["R"]
    key(sh, t + 0.3, (-15, 75, 10)); key(el, t + 0.3, (0, -105, 0)); key(fi, t + 0.3, (0, 0, 0))
    for i in range(4):
        key(el, t + 0.4 + i * 0.3, (0, -88, 0)); key(el, t + 0.55 + i * 0.3, (0, -118, 0))


def talk_head(t0, t1):
    """Small nods and tilts plus a moving mouth while she talks."""
    t, i = t0, 0
    while t < t1:
        key(head, t, (3 * math.sin(i * 1.7), 4 * math.sin(i * 0.9), 5 * math.sin(i * 1.3)))
        mouth.scale = (0.022, 0.006, 0.006 + 0.012 * (i % 2))
        mouth.keyframe_insert("scale", frame=f(t))
        t += 0.17
        i += 1
    mouth.scale = (0.022, 0.006, 0.006)
    mouth.keyframe_insert("scale", frame=f(t1))


# ---------------------------------------------------------------- performance
key(pivot, 0, (0, 0, 0))
key(spine, 0, (0, 0, 0))
key(head, 0, (0, 0, 0))
for side in "RL":
    rest(side, 0)

if SHOT == "wide":
    # 0-2.4 "Hi, I'm Sifa" + wave
    talk_head(0.3, 2.4); wave(0.3); rest("R", 2.5)
    # 2.6-4.4 "...the first S-I agent!" with the yes-pump
    talk_head(2.6, 4.6); yes_pump(2.5, 2.0); rest("R", 4.9)
    # 4.9-8.2 explaining with her hands, not continuous
    talk_head(5.0, 8.2); talk_gesture("L", 5.2, "open"); rest("L", 6.6)
    talk_gesture("R", 6.8, "count"); rest("R", 8.2)
    # 8.4-10.4 swivel the chair to the desk and look at the screen
    key(pivot, 8.4, (0, 0, 0)); key(pivot, 10.0, (0, 0, 72))
    key(head, 8.6, (0, 0, 0)); key(head, 10.2, (-4, 0, 14))
    key(spine, 8.6, (0, 0, 0)); key(spine, 10.2, (8, 0, 0))   # leans in toward the screen
    for side in "RL":
        sh, el, wr, fi = arms[side]
        key(sh, 9.2, REST_UPPER[side]); key(el, 9.2, REST_ELBOW)
        key(sh, 10.4, (-58, 4 if side == "R" else -4, 0)); key(el, 10.4, (-55, 0, 0)); key(wr, 10.4, (-15, 0, 0))
    key(pivot, DUR, (0, 0, 72)); key(head, DUR, (-6, 0, 16))
    cam_loc, cam_target, lens = (0.45, -2.9, 1.2), (0.35, 0.0, 0.95), 38
else:
    # facecam loop: talking with varied, occasional gestures
    talk_head(0.2, 9.6)
    talk_gesture("L", 0.6, "open"); rest("L", 2.2)
    talk_gesture("R", 2.8, "point"); rest("R", 4.3)
    yes_pump(4.8, 1.4); rest("R", 6.7)
    talk_gesture("R", 7.0, "both"); rest("R", 8.6); rest("L", 8.6)
    cam_loc, cam_target, lens = (0.0, -1.5, 1.2), (0.0, 0.0, 1.12), 40

for o in bpy.data.objects:
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "EASE_IN_OUT"

# ---------------------------------------------------------------- camera and lights
bpy.ops.object.camera_add(location=cam_loc)
cam = bpy.context.object
cam.data.lens = lens
target = joint("CamTarget", cam_target)
c = cam.constraints.new("TRACK_TO")
c.target, c.track_axis, c.up_axis = target, "TRACK_NEGATIVE_Z", "UP_Y"
scene.camera = cam
if SHOT == "wide":  # slow push-in, then drift toward the monitor as she turns
    cam.keyframe_insert("location", frame=1)
    cam.location = (0.6, -2.5, 1.18)
    cam.keyframe_insert("location", frame=f(8.4))
    cam.location = (0.95, -2.2, 1.16)
    cam.keyframe_insert("location", frame=f(DUR))
    target.keyframe_insert("location", frame=f(8.4))
    target.location = (0.9, 0.0, 1.05)
    target.keyframe_insert("location", frame=f(DUR))


def area(name, loc, rot, color, energy, size):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot)
    l = bpy.context.object
    l.name = name
    l.data.color, l.data.energy, l.data.size = color, energy, size
    return l


area("Key", (-0.9, -1.8, 1.9), (D(55), 0, D(-25)), (1, 0.92, 0.88), 140, 1.2)
area("RimPurple", (-1.2, 1.0, 2.2), (D(-50), D(-30), 0), (0.7, 0.3, 1), 220, 1.0)
area("FillCyan", (1.6, -0.6, 1.4), (D(70), 0, D(80)), (0.2, 0.8, 1), 90, 1.0)
if SHOT == "face":  # cut-out: only Sifa, no room, transparent background, for overlaying on gameplay
    keep = set()
    def mark(o):
        keep.add(o.name)
        for c in o.children:
            mark(c)
    mark(pelvis)
    for o in bpy.data.objects:
        if o.type in ("MESH", "CURVE", "FONT") and o.name not in keep:
            o.hide_render = True
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_x, scene.render.resolution_y = 720, 720

import os
if os.environ.get("FRAMES"):  # test stills only, e.g. FRAMES=1,60,120
    for fr in map(int, os.environ["FRAMES"].split(",")):
        scene.frame_set(fr)
        scene.render.filepath = f"{OUT}/{SHOT}_test_{fr:04d}.png"
        bpy.ops.render.render(write_still=True)
else:
    print("rendering", SHOT, scene.frame_end, "frames")
    bpy.ops.render.render(animation=True)
