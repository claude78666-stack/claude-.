"""Blender previz (animatic) for "Prophet Nuh and the Great Ark".

Run:  blender -b -P build_previz.py -- [--render] [--frames A-B]
Builds every set in one .blend, binds one camera per shot to timeline markers,
and (with --render) writes PNG frames to frames/. Shot lengths follow the
narration in durations.json so picture and voice line up.

Prophet Nuh is never shown as a person: only as a soft, faceless figure of
white light. Allah is never depicted.
"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector

random.seed(7)
D = os.path.dirname(os.path.abspath(__file__))
FPS = 8
LEAD, TAIL = 1.0, 1.5                       # seconds before / after each narration
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 6
sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"
sc.cycles.max_bounces = 2
sc.cycles.use_adaptive_sampling = True
sc.render.resolution_x, sc.render.resolution_y = 512, 288
sc.render.use_persistent_data = True
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = os.path.join(D, "frames", "f_")

# ---------------------------------------------------------------- timeline
durs = json.load(open(os.path.join(D, "durations.json")))
SHOT = {}
f = 1
for sid, d in durs:
    n = round((LEAD + d + TAIL + (1.5 if sid == "s11" else 0)) * FPS)
    SHOT[sid] = (f, f + n - 1)
    f += n
sc.frame_start, sc.frame_end = 1, f - 1
json.dump({k: v for k, v in SHOT.items()}, open(os.path.join(D, "shots.json"), "w"))


def at(sid, frac):
    a, b = SHOT[sid]
    return round(a + (b - a) * frac)


# ---------------------------------------------------------------- materials
def mat(name, col, rough=0.6, emit=None, estr=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = estr
    return m


def wood_mat(name, c1, c2):
    m = mat(name, c1, 0.8)
    nt = m.node_tree
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 6
    wave.inputs["Distortion"].default_value = 1.5
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c2, 1)
    ramp.color_ramp.elements[1].color = (*c1, 1)
    ramp.color_ramp.elements[0].position = 0.45
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def glow_mat(name, strength):
    """Soft halo: bright where it faces the camera, fading to clear at the rim."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1, 0.97, 0.88, 1)
    em.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], mix.inputs["Fac"])
    nt.links.new(em.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


GRASS = mat("grass", (0.16, 0.36, 0.09), 0.9)
EARTH = mat("dry_earth", (0.55, 0.42, 0.26), 0.95)
STONE = mat("stone", (0.42, 0.40, 0.38), 0.85)
ROCK = mat("rock", (0.30, 0.27, 0.24), 0.9)
MUD = mat("mudbrick", (0.62, 0.48, 0.33), 0.9)
WOOD = wood_mat("planks", (0.42, 0.26, 0.13), (0.27, 0.16, 0.08))
DARK = mat("dark", (0.04, 0.03, 0.02), 0.9)
SKIN = mat("skin", (0.55, 0.38, 0.27), 0.7)
WATER = mat("water", (0.03, 0.17, 0.24), 0.08)
STORM = mat("storm_water", (0.02, 0.07, 0.09), 0.12)
RIVER = mat("river", (0.08, 0.30, 0.42), 0.1)
LEAF = mat("leaves", (0.10, 0.30, 0.07), 0.8)
TRUNK = mat("trunk", (0.25, 0.16, 0.08), 0.9)
CLOTH = [mat(f"cloth{i}", c, 0.9) for i, c in enumerate(
    [(0.55, 0.47, 0.35), (0.38, 0.30, 0.22), (0.62, 0.58, 0.50), (0.30, 0.33, 0.30), (0.50, 0.36, 0.26)])]
RICH = [mat("rich_purple", (0.30, 0.08, 0.36), 0.5), mat("rich_red", (0.55, 0.08, 0.06), 0.5)]
GOLD = mat("gold", (0.85, 0.62, 0.15), 0.3)
LIGHT_CORE = mat("nuh_core", (1, 1, 1), 0.5, (1, 0.98, 0.92), 18)
HALO = glow_mat("nuh_halo", 3.0)
MOON = mat("moon", (0.9, 0.9, 0.85), 0.9, (0.85, 0.88, 1.0), 6)
SUNDISC = mat("sun_disc", (1, 0.8, 0.3), 0.9, (1, 0.75, 0.3), 30)
DROP = mat("raindrop", (0.7, 0.75, 0.8), 0.2, (0.5, 0.55, 0.6), 0.6)
ANIMAL_COL = {
    "elephant": mat("elephant", (0.36, 0.35, 0.34)), "giraffe": mat("giraffe", (0.78, 0.55, 0.22)),
    "sheep": mat("sheep", (0.88, 0.86, 0.80)), "lion": mat("lion", (0.72, 0.50, 0.22)),
    "camel": mat("camel", (0.70, 0.55, 0.36)), "horse": mat("horse", (0.35, 0.22, 0.13)),
}


# ---------------------------------------------------------------- helpers
def prim(kind, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), m=None, name=None, smooth=False, **kw):
    getattr(bpy.ops.mesh, f"primitive_{kind}_add")(location=loc, rotation=rot, **kw)
    o = bpy.context.active_object
    o.scale = scale
    if m:
        o.data.materials.append(m)
    if name:
        o.name = name
    if smooth:
        bpy.ops.object.shade_smooth()
    return o


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.location = loc
    return e


def group(name, loc, parts):
    e = empty(name)
    for p in parts:
        p.parent = e
    e.location = loc
    return e


def key(obj, path, frame, value=None, index=-1):
    if value is not None:
        attr = obj
        *head, last = path.split(".")
        for h in head:
            attr = getattr(attr, h)
        setattr(attr, last, value)
    obj.keyframe_insert(data_path=path, frame=frame, index=index)


def linear(obj):
    ad = obj.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def wobble(obj, path, index, strength, scale):
    if not (obj.animation_data and obj.animation_data.action):
        obj.keyframe_insert(data_path=path, frame=1, index=index)
    fc = obj.animation_data.action.fcurves.find(path, index=index)
    if fc is None:
        obj.keyframe_insert(data_path=path, frame=1, index=index)
        fc = obj.animation_data.action.fcurves.find(path, index=index)
    n = fc.modifiers.new("NOISE")
    n.strength, n.scale, n.phase = strength, scale, random.uniform(0, 100)


def show_between(obj, f0, f1):
    """Hide an object (scale 0) outside [f0, f1]."""
    s = obj.scale.copy()
    for fr, v in ((1, 0), (f0 - 1, 0), (f0, 1), (f1, 1), (f1 + 1, 0)):
        if fr >= 1:
            obj.scale = s * v if v else (0, 0, 0)
            obj.keyframe_insert("scale", frame=fr)
    for fc in obj.animation_data.action.fcurves:
        if fc.data_path == "scale":
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def ground(name, loc, size, m, hills=1.5, noise=18):
    o = prim("grid", loc, (size, size, 1), m=m, name=name, x_subdivisions=120, y_subdivisions=120, size=2)
    tex = bpy.data.textures.new(name + "_n", "CLOUDS")
    tex.noise_scale = noise
    d = o.modifiers.new("hills", "DISPLACE")
    d.texture, d.strength, d.mid_level = tex, hills, 0.5
    bpy.ops.object.shade_smooth()
    return o


def tree(loc, s=1.0):
    t = prim("cylinder", (0, 0, 1.2 * s), (0.18 * s, 0.18 * s, 1.2 * s), m=TRUNK, vertices=8)
    c = prim("ico_sphere", (0, 0, 3.0 * s), (1.3 * s, 1.3 * s, 1.5 * s), m=LEAF, subdivisions=2)
    return group("tree", loc, [t, c])


def person(loc, cloth, h=1.0, name="person", yaw=0.0, hat=False):
    parts = [
        prim("cylinder", (0, 0, 0.6 * h), (0.24 * h, 0.24 * h, 0.6 * h), m=cloth, vertices=14, smooth=True),
        prim("uv_sphere", (0, 0, 1.38 * h), (0.19 * h,) * 3, m=SKIN, segments=14, ring_count=8, smooth=True),
    ]
    if hat:
        parts.append(prim("cylinder", (0, 0, 1.62 * h), (0.17 * h, 0.17 * h, 0.1 * h), m=GOLD, vertices=12))
    e = group(name, loc, parts)
    e.rotation_euler.z = yaw
    return e


def cloth_cover(person_e, f_on, h=1.0):
    """A cloth that drops over the head: 'they covered themselves with their clothes'."""
    c = prim("cone", (0, 0, 1.45 * h), (0.32 * h, 0.32 * h, 0.42 * h), m=CLOTH[3], vertices=14)
    c.parent = person_e
    c.location = (0, 0, 1.45 * h)
    show_between(c, f_on, 10 ** 6)
    return c


def nuh_light(name, loc):
    core = prim("uv_sphere", (0, 0, 1.0), (0.30, 0.30, 0.95), m=LIGHT_CORE, segments=24, ring_count=12, smooth=True)
    halo = prim("uv_sphere", (0, 0, 1.0), (1.1, 1.1, 1.7), m=HALO, segments=24, ring_count=12, smooth=True)
    ld = bpy.data.lights.new(name + "_l", "POINT")
    ld.energy, ld.color, ld.shadow_soft_size = 1500, (1, 0.96, 0.85), 1.0
    lo = bpy.data.objects.new(name + "_l", ld)
    sc.collection.objects.link(lo)
    lo.location = (0, 0, 1.2)
    return group(name, loc, [core, halo, lo])


def animal(kind, loc, yaw=0.0):
    m = ANIMAL_COL[kind]
    spec = {  # body (x,y,z radii), leg height, leg radius, head radius, neck height
        "elephant": ((1.5, 0.85, 0.85), 1.0, 0.24, 0.55, 0.0),
        "giraffe": ((0.9, 0.42, 0.45), 1.6, 0.08, 0.22, 1.9),
        "sheep": ((0.55, 0.32, 0.32), 0.35, 0.06, 0.18, 0.0),
        "lion": ((0.85, 0.36, 0.40), 0.55, 0.09, 0.30, 0.0),
        "camel": ((0.95, 0.40, 0.45), 1.2, 0.09, 0.22, 0.8),
        "horse": ((0.9, 0.35, 0.42), 1.0, 0.08, 0.22, 0.55),
    }[kind]
    (bx, by, bz), lh, lr, hr, nh = spec
    zc = lh + bz * 0.8
    parts = [prim("uv_sphere", (0, 0, zc), (bx, by, bz), m=m, segments=18, ring_count=10, smooth=True)]
    for sx in (-0.6, 0.6):
        for sy in (-0.55, 0.55):
            parts.append(prim("cylinder", (sx * bx, sy * by, lh / 2), (lr, lr, lh / 2), m=m, vertices=8))
    hx = bx * 0.95
    hz = zc + bz * 0.4 + nh
    if nh:
        parts.append(prim("cylinder", (hx * 0.9, 0, zc + nh / 2 + bz * 0.3), (0.1 + lr, 0.1 + lr, nh / 2),
                          rot=(0, 0.25, 0), m=m, vertices=10))
    parts.append(prim("uv_sphere", (hx + hr * 0.6, 0, hz), (hr * 1.2, hr, hr), m=m, segments=14, ring_count=8, smooth=True))
    if kind == "lion":
        parts.append(prim("uv_sphere", (hx + hr * 0.2, 0, hz), (hr * 1.2, hr * 1.6, hr * 1.6), m=ANIMAL_COL["horse"], segments=14, ring_count=8))
    if kind == "elephant":
        parts.append(prim("cylinder", (hx + hr * 1.5, 0, hz - 0.6), (0.12, 0.12, 0.6), rot=(0, 0.3, 0), m=m, vertices=8))
    if kind == "camel":
        parts.append(prim("uv_sphere", (0, 0, zc + bz * 0.9), (0.35, 0.3, 0.35), m=m, segments=12, ring_count=8, smooth=True))
    e = group(kind, loc, parts)
    e.rotation_euler.z = yaw
    return e


def ark(name, loc, L=40, W=10, H=6, build=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    xedges = [e for e in bm.edges if abs(e.verts[0].co.x - e.verts[1].co.x) > 0.5]
    bmesh.ops.subdivide_edges(bm, edges=xedges, cuts=14, use_grid_fill=True)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    for v in bm.verts:
        x, y, z = v.co
        t = abs(x) * 2
        v.co.x, v.co.y, v.co.z = x * L, y * W, z * H
        if z < 0:
            v.co.y *= 0.55
        v.co.y *= max(0.08, 1 - t ** 3) ** 0.5
        if z > 0:
            v.co.z += 1.6 * t ** 2
        else:
            v.co.z += 1.2 * t ** 3
    bm.to_mesh(me)
    bm.free()
    hull = bpy.data.objects.new(name + "_hull", me)
    sc.collection.objects.link(hull)
    hull.data.materials.append(WOOD)
    bev = hull.modifiers.new("bevel", "BEVEL")
    bev.width, bev.segments = 0.15, 2
    parts = [hull]
    cab = prim("cube", (0, 0, H / 2 + 1.6), (L * 0.27, W * 0.3, 1.6), m=WOOD)
    roof = prim("cube", (0, 0, H / 2 + 3.4), (L * 0.29, W * 0.34, 0.25), m=WOOD)
    door = prim("cube", (0, -W * 0.5 + 0.2, 0.2), (1.4, 0.2, 1.6), m=DARK)
    parts += [cab, roof, door]
    if build:
        f0, f1 = build
        b = hull.modifiers.new("build", "BUILD")
        b.frame_start, b.frame_duration, b.use_random_order, b.seed = f0, f1 - f0, True, 3
        for p in (cab, roof):
            s = p.scale.copy()
            p.scale = (s.x, s.y, 0.001)
            p.keyframe_insert("scale", frame=f1 - 12)
            p.scale = s
            p.keyframe_insert("scale", frame=f1 + 6)
    e = group(name, loc, parts)
    return e


def ocean(name, loc, spatial, scale, chop, f0, f1, m, res=12, seed=1, speed=1.0):
    o = prim("plane", loc, m=m, name=name)
    mod = o.modifiers.new("Ocean", "OCEAN")
    mod.geometry_mode = "GENERATE"
    mod.resolution, mod.viewport_resolution = res, 4
    mod.spatial_size, mod.wave_scale, mod.choppiness = spatial, scale, chop
    mod.repeat_x = mod.repeat_y = 2
    mod.random_seed = seed
    mod.time = 1
    o.keyframe_insert('modifiers["Ocean"].time', frame=f0)
    mod.time = 1 + (f1 - f0) / FPS * speed
    o.keyframe_insert('modifiers["Ocean"].time', frame=f1)
    linear(o)
    bpy.ops.object.shade_smooth()
    # Cheap flat water out to the horizon so the edge of the wave patch never shows.
    far = prim("plane", loc, (1400, 1400, 1), m=m, name=name + "_far")
    far.parent = o
    far.location = (0, 0, -0.12)
    return o


DROP_OBJ = prim("cylinder", (0, 0, -500), (0.4, 0.012, 0.012), rot=(0, math.pi / 2, 0), m=DROP, name="drop", vertices=6)
DROP_OBJ.rotation_euler = (0, 0, 0)
DROP_OBJ.scale = (0.4, 0.012, 0.012)  # long along X; particles align X to velocity


def rain(name, loc, size, f0, f1, count):
    em = prim("plane", loc, (size, size, 1), name=name)
    em.modifiers.new("rain", "PARTICLE_SYSTEM")
    ps = em.particle_systems[0].settings
    ps.count, ps.frame_start, ps.frame_end, ps.lifetime = count, f0 - 30, f1, 30
    ps.emit_from, ps.physics_type = "FACE", "NEWTON"
    ps.normal_factor = 0
    ps.object_align_factor = (2, 0, -40)
    ps.render_type, ps.instance_object, ps.particle_size = "OBJECT", DROP_OBJ, 1.0
    ps.use_rotations, ps.rotation_mode = True, "VEL"
    em.show_instancer_for_render = False
    return em


# ---------------------------------------------------------------- world + sun
world = bpy.data.worlds.new("sky")
sc.world = world
world.use_nodes = True
BG = world.node_tree.nodes["Background"]
sun_d = bpy.data.lights.new("sun", "SUN")
sun_d.angle = math.radians(3)
SUN = bpy.data.objects.new("sun", sun_d)
sc.collection.objects.link(SUN)


def sky(frame, col, strength, sun_energy, sun_rot, sun_col=(1, 0.95, 0.85)):
    BG.inputs["Color"].default_value = (*col, 1)
    BG.inputs["Color"].keyframe_insert("default_value", frame=frame)
    BG.inputs["Strength"].default_value = strength
    BG.inputs["Strength"].keyframe_insert("default_value", frame=frame)
    sun_d.energy = sun_energy
    sun_d.keyframe_insert("energy", frame=frame)
    sun_d.color = sun_col
    sun_d.keyframe_insert("color", frame=frame)
    SUN.rotation_euler = [math.radians(a) for a in sun_rot]
    SUN.keyframe_insert("rotation_euler", frame=frame)


def hold_sky(sid, *args, **kw):
    a, b = SHOT[sid]
    sky(a, *args, **kw)
    sky(b, *args, **kw)


# ---------------------------------------------------------------- cameras
def camera(sid, keys, lens=32):
    """keys: list of (frac, cam_pos, target_pos)."""
    cd = bpy.data.cameras.new(sid)
    cd.lens = lens
    cd.clip_end = 1500
    c = bpy.data.objects.new("cam_" + sid, cd)
    sc.collection.objects.link(c)
    t = empty("tgt_" + sid)
    con = c.constraints.new("TRACK_TO")
    con.target, con.track_axis, con.up_axis = t, "TRACK_NEGATIVE_Z", "UP_Y"
    for frac, p, q in keys:
        fr = at(sid, frac)
        c.location = p
        c.keyframe_insert("location", frame=fr)
        t.location = q
        t.keyframe_insert("location", frame=fr)
    m = sc.timeline_markers.new(sid, frame=SHOT[sid][0])
    m.camera = c
    return c


def walk(obj, f0, f1, p0, p1, bob=0.05):
    obj.location = p0
    obj.keyframe_insert("location", frame=f0)
    obj.location = p1
    obj.keyframe_insert("location", frame=f1)
    linear(obj)
    if bob:
        wobble(obj, "location", 2, bob, 1.5)


# ================================================================= SETS
# --- S1 hook: calm sea at sunrise, ark on the water ----------------------
X = 0
ocean("sea1", (X, 0, 0), 320, 0.35, 0.6, *SHOT["s01"], WATER, seed=4)
a1 = ark("ark1", (X, 0, 1.2))
wobble(a1, "rotation_euler", 1, 0.03, 12)
wobble(a1, "location", 2, 0.25, 10)
hold_sky("s01", (0.95, 0.55, 0.30), 0.9, 4.0, (82, 0, 160), (1, 0.6, 0.35))
camera("s01", [(0, (X - 95, -70, 9), (X, 0, 3)), (1, (X - 52, -38, 5), (X, 0, 4))], lens=35)

# --- S2 village of statues ------------------------------------------------
X = 4000
ground("land2", (X, 0, -0.3), 120, GRASS, 0.8)
prim("plane", (X + 10, -20, -0.05), (120, 5, 1), rot=(0, 0, 0.15), m=RIVER, name="river2")
for i in range(40):
    tx, ty = X + random.uniform(-90, 90), random.uniform(-80, 60)
    if abs(tx - X) < 50 and ty < 22:
        continue  # keep the camera path clear
    tree((tx, ty, 0), random.uniform(0.8, 1.4))
prim("cube", (X, 25, 0.25), (14, 3, 0.5), m=STONE, name="platform")
for i in range(5):
    sx = X - 10 + i * 5
    prim("cylinder", (sx, 25, 1.2), (0.9, 0.9, 0.5), m=STONE, vertices=10)
    prim("cube", (sx, 25, 3.0), (0.7, 0.55, 1.4 + 0.2 * (i % 2)), m=STONE)
    prim("uv_sphere", (sx, 25, 4.9 + 0.3 * (i % 2)), (0.6,) * 3, m=STONE, segments=12, ring_count=8)
for r in range(3):
    for i in range(6):
        p = person((X - 8 + i * 3.2 + r, 14 - r * 3, 0), random.choice(CLOTH), random.uniform(0.9, 1.05),
                   yaw=0)
        a, b = SHOT["s02"]
        for k, fr in enumerate(range(a + 10, b, 30)):
            key(p, "rotation_euler", fr, (0, 0, 0), -1)
            key(p, "rotation_euler", fr + 12, (math.radians(-35), 0, 0), -1)
            p.rotation_euler = (0, 0, 0)
hold_sky("s02", (0.45, 0.65, 0.95), 1.0, 4.5, (50, 10, 30))
camera("s02", [(0, (X - 40, -70, 25), (X, 10, 2)), (0.6, (X - 12, -18, 7), (X, 22, 3)),
               (1, (X - 4, -2, 4), (X, 25, 3.5))], lens=30)

# --- S3 Nuh calls his people; moon, sun, earth like a carpet ---------------
X = 8000
hill = prim("cone", (X, 30, 0), (18, 18, 7), m=GRASS, vertices=48, name="hill3")
ground("land3", (X, 0, -0.3), 160, GRASS, 0.8)
nuh_light("nuh3", (X, 30, 7))
for i in range(28):
    ang = math.radians(200 + i * 5.2)
    rr = 22 + (i % 3) * 2.2
    person((X + rr * math.cos(ang), 30 + rr * math.sin(ang), 0), random.choice(CLOTH),
           random.uniform(0.85, 1.05), yaw=ang + math.pi)
prim("uv_sphere", (X - 70, 260, 120), (9,) * 3, m=MOON, segments=32, ring_count=16, smooth=True)
prim("uv_sphere", (X + 90, 280, 90), (14,) * 3, m=SUNDISC, segments=32, ring_count=16, smooth=True)
for i in range(40):
    tree((X + random.uniform(-150, 150), random.uniform(-150, -40), 0), random.uniform(0.8, 1.6))
a, b = SHOT["s03"]
sky(a, (0.45, 0.65, 0.95), 1.0, 4.5, (55, 0, 200))
sky(at("s03", 0.55), (0.45, 0.65, 0.95), 1.0, 4.5, (55, 0, 200))
sky(at("s03", 0.62), (0.75, 0.45, 0.45), 0.6, 1.5, (85, 0, 200), (1, 0.6, 0.4))
sky(at("s03", 0.80), (0.75, 0.45, 0.45), 0.6, 1.5, (85, 0, 200), (1, 0.6, 0.4))
sky(at("s03", 0.86), (0.50, 0.68, 0.95), 1.0, 4.5, (50, 0, 200))
sky(b, (0.50, 0.68, 0.95), 1.0, 4.5, (50, 0, 200))
camera("s03", [(0, (X, -12, 2.2), (X, 30, 7)), (0.5, (X + 6, 6, 3), (X, 30, 8)),
               (0.6, (X + 2, 10, 4), (X, 200, 90)), (0.8, (X + 2, 10, 4), (X + 10, 260, 100)),
               (0.86, (X + 2, 40, 60), (X, -60, 0)), (1, (X + 2, 60, 80), (X, -100, 0))], lens=28)

# --- S4 night and day, they cover their ears / heads ----------------------
X = 12000
ground("land4", (X, 0, -0.3), 120, GRASS, 0.6)
houses = []
for i in range(9):
    hx, hy = X + (i % 3) * 14 - 14, (i // 3) * 14 - 14
    prim("cube", (hx, hy, 1.5), (2.5, 2.5, 1.5), m=MUD)
    prim("cube", (hx, hy, 3.1), (2.8, 2.8, 0.15), m=TRUNK)
    houses.append((hx, hy))
people4 = []
for i, (hx, hy) in enumerate(houses):
    p = person((hx + 4, hy - 3.5, 0), random.choice(CLOTH), random.uniform(0.9, 1.05), yaw=random.uniform(0, 6.28))
    cloth_cover(p, at("s04", 0.30 + 0.02 * i))
    people4.append(p)
n4 = nuh_light("nuh4", (X - 20, -20, 0))
a, b = SHOT["s04"]
path = [(hx + 6, hy - 6, 0) for hx, hy in houses]
for k, p in enumerate(path):
    key(n4, "location", a + round((b - a) * k / len(path)), Vector(p))
cyc = 7 * FPS
for k, fr in enumerate(range(a, b + 1, cyc // 2)):
    if k % 2 == 0:
        sky(fr, (0.45, 0.65, 0.95), 1.0, 4.0, (45, 0, 30))
    else:
        sky(fr, (0.02, 0.03, 0.08), 0.25, 0.05, (120, 0, 30), (0.6, 0.7, 1.0))
camera("s04", [(0, (X - 50, -50, 30), (X, 0, 0)), (0.5, (X + 40, -55, 26), (X, 0, 0)),
               (1, (X + 55, 30, 30), (X, 0, 0))], lens=30)

# --- S5 the poor believers and the proud chiefs ---------------------------
X = 16000
ground("land5", (X, 0, -0.3), 100, GRASS, 0.6)
nuh_light("nuh5", (X, 6, 0))
for i in range(5):
    person((X - 3 + i * 1.4, 2 - (i % 2) * 1.2, 0), CLOTH[i % 2], random.uniform(0.85, 1.0), yaw=math.pi / 2)
chiefs = []
for i in range(4):
    c = person((X + 10 + i * 1.8, 3 + (i % 2), 0), RICH[i % 2], 1.15, yaw=math.pi, hat=True)
    a, b = SHOT["s05"]
    for fr in range(a, at("s05", 0.5), 6):
        key(c, "location", fr, Vector((X + 10 + i * 1.8, 3 + (i % 2), 0)))
        key(c, "location", fr + 3, Vector((X + 10 + i * 1.8, 3 + (i % 2), 0.25)))
    chiefs.append(c)
for i in range(10):
    tree((X + random.uniform(-40, 40), random.uniform(20, 60), 0))
hold_sky("s05", (0.95, 0.70, 0.45), 0.8, 3.0, (72, 0, 120), (1, 0.75, 0.5))
camera("s05", [(0, (X + 13, -8, 2), (X + 13, 3, 1.6)), (0.45, (X + 11, -9, 2), (X + 12, 3, 1.6)),
               (0.6, (X + 2, -9, 2.2), (X, 3, 1.2)), (1, (X, -5, 1.8), (X - 0.5, 3, 1.1))], lens=35)

# --- S6/S7 building the ark on dry land, then boarding --------------------
X = 20000
ground("land6", (X, 0, -0.3), 160, EARTH, 1.2, 25)
a6, b6 = SHOT["s06"]
a7, b7 = SHOT["s07"]
ark("ark6", (X, 0, 3.0), build=(a6 + 12, at("s06", 0.85)))
for i in range(10):
    for side in (-1, 1):
        prim("cylinder", (X - 18 + i * 4, side * 6.5, 4), (0.12, 0.12, 4.2), m=TRUNK, vertices=6)
for i in range(4):
    prim("cube", (X - 10 + i * 6, -14, 0.4), (2.5, 0.8, 0.4), m=WOOD)
n6 = nuh_light("nuh6", (X - 14, -9, 0))
walk(n6, a6, b6, (X - 14, -9, 0), (X + 12, -9, 0), bob=0)
for i in range(3):
    c = person((X - 40, -22 - i * 1.5, 0), RICH[i % 2], 1.15, yaw=0, hat=True)
    walk(c, at("s06", 0.55), at("s06", 1.0), (X - 40 - i * 2, -22 - i * 1.2, 0), (X + 30 - i * 2, -22 - i * 1.2, 0), bob=0.12)
ramp = prim("cube", (X, -10.5, 1.4), (1.6, 6.5, 0.12), rot=(math.radians(-26), 0, 0), m=WOOD, name="ramp")
show_between(ramp, a7, b7)
flood7 = ocean("rise7", (X, 0, -3.0), 140, 0.4, 0.4, a7, b7, WATER, seed=7)
key(flood7, "location", a7, Vector((X, 0, -3.0)))
key(flood7, "location", b7, Vector((X, 0, 0.6)))
kinds = ["elephant", "giraffe", "camel", "lion", "horse", "sheep"]
for i, kd in enumerate(kinds):
    for j in range(2):
        an = animal(kd, (X - 60, -40, 0), yaw=math.radians(90))
        f0 = a7 + round(i * 1.6 * FPS) + j * 8
        f1 = f0 + round(7 * FPS)
        an.location = (X - 3 + j * 3 - 30, -34, 0)
        walk(an, f0, f1, (X - 2 + j * 3 - 6, -34, 0), (X - 0.5 + j * 1.2, -12, 0.4), bob=0.08)
        show_between(an, f0, f1)
for i in range(5):
    p = person((X - 5, -34, 0), CLOTH[i % 5], 1.0, yaw=math.radians(90))
    f0 = a7 + round((10 + i * 0.8) * FPS)
    walk(p, f0, f0 + 6 * FPS, (X - 2 + i, -30, 0), (X, -12, 0.4), bob=0.05)
    show_between(p, f0, f0 + 6 * FPS)
rain("rain7", (X, -10, 40), 60, at("s07", 0.4), b7, 4000)
sky(a6, (0.55, 0.70, 0.92), 1.0, 5.0, (40, 0, 60))
sky(b6, (0.55, 0.70, 0.92), 1.0, 5.0, (40, 0, 60))
sky(a7, (0.30, 0.33, 0.38), 0.6, 1.2, (55, 0, 60), (0.8, 0.85, 0.9))
sky(b7, (0.16, 0.18, 0.22), 0.6, 0.6, (60, 0, 60), (0.7, 0.75, 0.85))
camera("s06", [(0, (X - 55, -45, 14), (X, 0, 3)), (0.5, (X - 10, -60, 10), (X, 0, 4)),
               (1, (X + 50, -45, 12), (X, 0, 4))], lens=30)
camera("s07", [(0, (X - 30, -50, 6), (X - 4, -20, 2)), (0.6, (X - 22, -40, 5), (X, -12, 3)),
               (1, (X - 35, -60, 14), (X, 0, 5))], lens=30)

# --- S8 the flood, the son on the rock ------------------------------------
X = 24000
a8, b8 = SHOT["s08"]
sea8 = ocean("storm8", (X, 0, 0), 320, 4.5, 1.6, a8, b8, STORM, res=14, seed=11, speed=1.4)
key(sea8, "location", at("s08", 0.35), Vector((X, 0, 0)))
key(sea8, "location", at("s08", 0.75), Vector((X, 0, 3.0)))
a8k = ark("ark8", (X, 0, 2.0))
walk(a8k, a8, b8, (X - 10, 0, 2.0), (X + 20, 0, 2.0), bob=0)
wobble(a8k, "location", 2, 1.8, 8)
wobble(a8k, "rotation_euler", 1, 0.12, 6)
wobble(a8k, "rotation_euler", 0, 0.06, 9)
rock = prim("cone", (X - 60, 80, -2), (9, 9, 11), m=ROCK, vertices=12, name="rock8")
son = person((X - 60, 80, 9.0), CLOTH[1], 0.95, yaw=math.radians(220), name="son")
rain("rain8", (X + 20, 20, 50), 120, a8, b8, 9000)
sky(a8, (0.16, 0.18, 0.22), 0.7, 0.6, (60, 0, 60), (0.7, 0.75, 0.85))
for k in range(5):  # lightning flashes
    fr = a8 + round((b8 - a8) * (0.1 + 0.19 * k))
    sky(fr - 1, (0.16, 0.18, 0.22), 0.7, 0.6, (60, 0, 60), (0.7, 0.75, 0.85))
    sky(fr, (0.7, 0.75, 0.9), 2.5, 4.0, (60, 0, 60), (0.8, 0.85, 1.0))
    sky(fr + 2, (0.16, 0.18, 0.22), 0.7, 0.6, (60, 0, 60), (0.7, 0.75, 0.85))
sky(b8, (0.16, 0.18, 0.22), 0.7, 0.6, (60, 0, 60), (0.7, 0.75, 0.85))
camera("s08", [(0, (X - 70, -60, 12), (X, 0, 3)), (0.3, (X - 25, -45, 10), (X + 5, 0, 4)),
               (0.38, (X - 35, 25, 10), (X - 60, 80, 9)), (0.66, (X - 40, 35, 11), (X - 60, 80, 9)),
               (0.74, (X - 15, -38, 11), (X + 12, 0, 5)), (1, (X + 5, -32, 8), (X + 18, 0, 5))], lens=32)

# --- S9 the water goes down, the ark rests on Mount Judi ------------------
X = 28000
a9, b9 = SHOT["s09"]
mtn = prim("cone", (X, 0, 0), (70, 70, 34), m=ROCK, vertices=64, name="judi", radius2=0.15)
tex = bpy.data.textures.new("judi_n", "CLOUDS")
tex.noise_scale = 14
mtn_sub = mtn.modifiers.new("sub", "SUBSURF")
mtn_sub.levels = mtn_sub.render_levels = 3
mtn_sub.subdivision_type = "SIMPLE"
dm = mtn.modifiers.new("d", "DISPLACE")
dm.texture, dm.strength = tex, 4
ark("ark9", (X, 0, 33.6))
w9 = ocean("water9", (X, 0, 30), 200, 0.8, 0.6, a9, b9, WATER, res=12, seed=9)
key(w9, "location", a9, Vector((X, 0, 30)))
key(w9, "location", b9, Vector((X, 0, 4)))
sky(a9, (0.25, 0.28, 0.33), 0.5, 1.0, (60, 0, 80), (0.8, 0.85, 0.9))
sky(at("s09", 0.45), (0.55, 0.62, 0.75), 0.8, 3.0, (50, 0, 80))
sky(b9, (0.55, 0.75, 1.0), 1.1, 5.5, (40, 0, 80))
camera("s09", [(0, (X - 110, -90, 40), (X, 0, 34)), (1, (X - 70, -110, 55), (X, 0, 30))], lens=35)

# --- S10/S11 stepping onto green land, lessons, outro ---------------------
X = 32000
a10, b10 = SHOT["s10"]
a11, b11 = SHOT["s11"]
ground("land10", (X, 0, -0.3), 160, GRASS, 0.8)
for i in range(30):
    tree((X + random.uniform(-120, 120), random.uniform(10, 120), 0), random.uniform(0.8, 1.4))
ark("ark10", (X - 25, 35, 3.5))
nuh_light("nuh10", (X - 6, 6, 0))
for i in range(6):
    p = person((X - 15, 25, 0), CLOTH[i % 5], 1.0, yaw=math.radians(-60))
    walk(p, a10 + i * 10, a10 + i * 10 + 10 * FPS, (X - 18 + i, 24 - i * 0.5, 0), (X - 4 + i * 1.5, 4 - i * 0.8, 0), bob=0.05)
for i, kd in enumerate(kinds):
    for j in range(2):
        an = animal(kd, (X - 20, 30, 0), yaw=math.radians(-50))
        walk(an, a10 + 30 + i * 12 + j * 6, b10, (X - 22 + j * 2, 28 - i, 0),
             (X + 8 + i * 4 + j * 2, -6 + i * 2.5, 0), bob=0.06)
hold_sky("s10", (0.95, 0.70, 0.50), 0.9, 4.0, (78, 0, 140), (1, 0.75, 0.5))
hold_sky("s11", (0.95, 0.70, 0.50), 0.9, 4.0, (78, 0, 140), (1, 0.75, 0.5))
camera("s10", [(0, (X + 10, -30, 6), (X - 10, 20, 3)), (1, (X + 4, -18, 4), (X - 4, 10, 2))], lens=32)
camera("s11", [(0, (X + 4, -18, 4), (X - 4, 10, 2)), (1, (X + 4, -25, 30), (X, 80, 40))], lens=32)

# ---------------------------------------------------------------- save / render
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "nuh_previz.blend"))
print("SHOTS", SHOT, "frames", sc.frame_end)
if "--render" in argv:
    if "--frames" in argv:
        fa, fb = argv[argv.index("--frames") + 1].split("-")
        sc.frame_start, sc.frame_end = int(fa), int(fb)
    bpy.ops.render.render(animation=True)
