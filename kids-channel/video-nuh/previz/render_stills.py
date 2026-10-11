"""Render one still per shot (or given frames) from nuh_previz.blend: blender -b nuh_previz.blend -P render_stills.py -- out_dir f1 f2 ..."""
import bpy, sys, os, time
a = sys.argv[sys.argv.index("--") + 1:]
out, frames = a[0], [int(x) for x in a[1:]]
sc = bpy.context.scene
for f in frames:
    t = time.time()
    sc.frame_set(f)
    sc.render.filepath = os.path.join(out, f"still_{f:05d}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", f, round(time.time() - t, 1), "s", flush=True)
