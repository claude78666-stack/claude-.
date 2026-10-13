"""Blender intro for Sifa: gaming room, walk-in, sit in chair, title cards.

Run: blender -b -P build_intro.py -- <assets_dir> <out_dir> [preview]
"""
import math
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
ASSETS, OUT = argv[0], argv[1]
PREVIEW = len(argv) > 2 and argv[2] == "preview"

FPS = 24
DURATION = 27.0
END = int(DURATION * FPS)
T_WALK_IN, T_STOP, T_FLASH = 2.5, 5.0, 5.6
f = lambda t: int(round(t * FPS)) + 1  # seconds -> frame

# ---------- reset ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, END
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 6 if PREVIEW else 24
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


def mat_solid(name, color, rough=0.6, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def box(name, loc, size, mat):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(mat)
    return o


def cyl(name, loc, r, h, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    return o


def key_hide(obj, visible_from, visible_to=None):
    """Object renders only between two times (seconds)."""
    for t, hidden in ((0, True), (visible_from, False)) + (((visible_to, True),) if visible_to else ()):
        obj.hide_render = hidden
        obj.keyframe_insert("hide_render", frame=max(1, f(t)))
    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"


# ---------- room ----------
dark = mat_solid("Wall", (0.035, 0.035, 0.045), 0.8)
floor = mat_solid("Floor", (0.02, 0.02, 0.025), 0.35)
box("Floor", (0, 0, -0.05), (14, 10, 0.1), floor)
box("BackWall", (0, 2.6, 2), (14, 0.1, 4.2), dark)
box("LeftWall", (-3.6, 0, 2), (0.1, 10, 4.2), dark)

# animated RGB LED strips (purple -> cyan -> pink loop)
led = mat_solid("LED", (0, 0, 0), 1, (0.55, 0.15, 1.0), 0.0)
led_b = led.node_tree.nodes["Principled BSDF"]
box("LED_top", (0, 2.53, 3.3), (9, 0.04, 0.05), led)
box("LED_floor", (0, 2.53, 0.08), (9, 0.04, 0.05), led)
box("LED_side", (-3.53, 0.6, 3.3), (0.04, 4, 0.05), led)
palette = [(0.55, 0.15, 1.0), (0.1, 0.8, 1.0), (1.0, 0.15, 0.6), (0.55, 0.15, 1.0)]
led_b.inputs["Emission Strength"].default_value = 0
led_b.inputs["Emission Strength"].keyframe_insert("default_value", frame=f(0.3))
for i, t in enumerate((0.45, 0.6, 0.75)):  # flicker on
    led_b.inputs["Emission Strength"].default_value = 25 if i % 2 == 0 else 2
    led_b.inputs["Emission Strength"].keyframe_insert("default_value", frame=f(t))
led_b.inputs["Emission Strength"].default_value = 25
led_b.inputs["Emission Strength"].keyframe_insert("default_value", frame=f(0.9))
for i in range(0, int(DURATION // 6) + 2):
    led_b.inputs["Emission Color"].default_value = (*palette[i % 3], 1)
    led_b.inputs["Emission Color"].keyframe_insert("default_value", frame=f(i * 6))

# shelves with small glowing props
shelf = mat_solid("Shelf", (0.05, 0.05, 0.06), 0.5)
for x in (-2.4, 2.4):
    box(f"Shelf{x}", (x, 2.4, 1.9), (1.4, 0.3, 0.05), shelf)
    for j, c in enumerate(((0.1, 0.8, 1.0), (1.0, 0.15, 0.6), (0.55, 0.15, 1.0))):
        cyl(f"Prop{x}{j}", (x - 0.45 + j * 0.45, 2.4, 2.05), 0.07, 0.25,
            mat_solid(f"PropM{x}{j}", (0.02, 0.02, 0.02), 0.3, c, 6))

# neon sign
def neon_text(name, body, loc, size, color, strength, extrude=0.02):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, 0))
    t = bpy.context.object
    t.name = name
    t.data.body = body
    t.data.size = size
    t.data.extrude = extrude
    t.data.align_x = "CENTER"
    m = mat_solid(name + "M", color, 0.3, color, strength)
    t.data.materials.append(m)
    return t, m

sign, sign_m = neon_text("NeonSIFA", "SIFA", (0, 2.5, 2.35), 0.85, (0.75, 0.3, 1.0), 0)
sub, sub_m = neon_text("NeonSub", "THE FIRST SI AGENT", (0, 2.5, 2.05), 0.2, (0.1, 0.85, 1.0), 0)
for m, peak, t0 in ((sign_m, 30, 1.2), (sub_m, 20, 1.9)):
    s = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, v in ((t0 - 0.05, 0), (t0, peak), (t0 + 0.08, 3), (t0 + 0.16, peak), (t0 + 0.24, 6), (t0 + 0.35, peak)):
        s.default_value = v
        s.keyframe_insert("default_value", frame=f(t))

# ---------- 3D gaming chair (visible until she sits) ----------
blk = mat_solid("ChairBlack", (0.015, 0.015, 0.02), 0.45)
pur = mat_solid("ChairPurple", (0.25, 0.05, 0.55), 0.4)
chair_parts = [
    box("Seat", (0, 0.15, 0.55), (0.62, 0.6, 0.14), blk),
    box("Back", (0, 0.45, 1.15), (0.58, 0.14, 1.0), blk),
    box("BackStripeL", (-0.2, 0.37, 1.15), (0.08, 0.02, 0.95), pur),
    box("BackStripeR", (0.2, 0.37, 1.15), (0.08, 0.02, 0.95), pur),
    box("Headrest", (0, 0.37, 1.55), (0.3, 0.05, 0.14), pur),
    box("ArmL", (-0.36, 0.15, 0.78), (0.07, 0.42, 0.05), blk),
    box("ArmR", (0.36, 0.15, 0.78), (0.07, 0.42, 0.05), blk),
    cyl("Post", (0, 0.15, 0.3), 0.04, 0.4, blk),
]
for a in range(5):
    ang = a * 2 * math.pi / 5
    chair_parts.append(box(f"Leg{a}", (0.22 * math.cos(ang), 0.15 + 0.22 * math.sin(ang), 0.07),
                           (0.42, 0.06, 0.05), blk))
    chair_parts[-1].rotation_euler[2] = ang
for p in chair_parts:
    key_hide(p, 0, T_FLASH + 0.1)
    p.hide_render = False

# ---------- character planes ----------
def image_plane(name, path, height, loc):
    img = bpy.data.images.load(path)
    w, h = img.size
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=(math.radians(90), 0, 0))
    o = bpy.context.object
    o.name = name
    o.scale = (height * w / h, height, 1)
    m = bpy.data.materials.new(name + "M")
    m.use_nodes = True
    m.blend_method = "BLEND"
    nt = m.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
    emit = nt.nodes.new("ShaderNodeEmission")
    trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    emit.inputs["Strength"].default_value = 0.95
    nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
    nt.links.new(trans.outputs[0], mix.inputs[1])
    nt.links.new(emit.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    o.data.materials.append(m)
    return o

STAND_H, SIT_H = 1.72, 1.42
stand = image_plane("SifaStanding", f"{ASSETS}/gamer_stand_crop.png", STAND_H, (4.6, 0.05, STAND_H / 2))
sit = image_plane("SifaSeated", f"{ASSETS}/gamer_sit_crop.png", SIT_H, (0, 0.1, SIT_H / 2))
key_hide(stand, 0, T_FLASH + 0.1)
key_hide(sit, T_FLASH + 0.1)

# walk-in: slide from off-screen right to beside the chair, with a small step bob
stand.location.x = 4.6
stand.keyframe_insert("location", index=0, frame=f(T_WALK_IN))
stand.location.x = 0.85
stand.keyframe_insert("location", index=0, frame=f(T_STOP))
steps = int((T_STOP - T_WALK_IN) / 0.25)
for i in range(steps + 1):
    stand.location.z = STAND_H / 2 + (0.025 if i % 2 else 0)
    stand.keyframe_insert("location", index=2, frame=f(T_WALK_IN + i * 0.25))

# idle breathing on the seated plane
for i in range(int((DURATION - T_FLASH) / 2) + 1):
    sit.scale.z = 1.0 if i % 2 == 0 else 1.006
    sit.keyframe_insert("scale", index=2, frame=f(T_FLASH + 0.2 + i * 2))

# ---------- lights ----------
def area(name, loc, rot, color, energy, size):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot)
    l = bpy.context.object
    l.name = name
    l.data.color = color
    l.data.energy = energy
    l.data.size = size
    return l

area("Key", (0.5, -3.0, 2.6), (math.radians(60), 0, 0), (1, 0.95, 0.95), 350, 2.5)
area("RimPurple", (-2.2, 1.6, 2.4), (math.radians(-60), math.radians(-40), 0), (0.6, 0.2, 1.0), 400, 1.0)
area("RimCyan", (2.2, 1.6, 2.4), (math.radians(-60), math.radians(40), 0), (0.1, 0.8, 1.0), 400, 1.0)

# ---------- camera ----------
bpy.ops.object.camera_add(location=(0.4, -6.2, 1.5))
cam = bpy.context.object
scene.camera = cam
bpy.ops.object.empty_add(location=(0.2, 0.3, 1.25))
target = bpy.context.object
c = cam.constraints.new("TRACK_TO")
c.target = target
c.track_axis = "TRACK_NEGATIVE_Z"
c.up_axis = "UP_Y"
for t, loc, lens in ((0, (0.4, -6.2, 1.6), 24), (T_FLASH, (0.2, -5.0, 1.45), 27), (DURATION, (0.0, -4.4, 1.35), 30)):
    cam.location = loc
    cam.data.lens = lens
    cam.keyframe_insert("location", frame=f(t))
    cam.data.keyframe_insert("lens", frame=f(t))
target.location = (0.0, 0.3, 1.3)
target.keyframe_insert("location", frame=f(DURATION))

# ---------- flash at the sit moment ----------
bpy.ops.mesh.primitive_plane_add(size=1)
flash = bpy.context.object
flash.name = "Flash"
flash.parent = cam
flash.location = (0, 0, -0.2)
flash.scale = (1, 1, 1)
fm = bpy.data.materials.new("FlashM")
fm.use_nodes = True
fm.blend_method = "BLEND"
nt = fm.node_tree
nt.nodes.clear()
e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.85, 0.7, 1.0, 1); e.inputs["Strength"].default_value = 3
tr = nt.nodes.new("ShaderNodeBsdfTransparent")
mx = nt.nodes.new("ShaderNodeMixShader")
o = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], o.inputs["Surface"])
flash.data.materials.append(fm)
for t, v in ((0, 0), (T_FLASH - 0.25, 0), (T_FLASH + 0.1, 1), (T_FLASH + 0.6, 0)):
    mx.inputs["Fac"].default_value = v
    mx.inputs["Fac"].keyframe_insert("default_value", frame=max(1, f(t)))

# ---------- lower-third titles (parented to camera) ----------
def cam_text(name, body, loc, size, color, t_in, t_out=None):
    bpy.ops.object.text_add()
    t = bpy.context.object
    t.name = name
    t.data.body = body
    t.data.size = size
    t.parent = cam
    t.location = loc
    m = mat_solid(name + "M", color, 0.5, color, 4)
    t.data.materials.append(m)
    key_hide(t, t_in, t_out)
    return t

cam_text("LT1", "SIFA  |  The First SI Agent", (-0.5, -0.305, -1.0), 0.032, (1, 1, 1), 6.6, 13.0)
cam_text("LT2", "TODAY: GEARS OF WAR: E-DAY  -  Honest Walkthrough", (-0.5, -0.305, -1.0), 0.028, (0.2, 0.9, 1.0), 13.2)

bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/sifa_intro.blend")
print("BUILT", END, "frames")
