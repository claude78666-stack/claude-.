"""Create the rigged 3D Sifa with MPFB (MakeHuman) and save it.

Run: blender -b -P make_human.py -- <out.blend>
"""
import sys

import bpy

from bl_ext.user_default.mpfb.services.humanservice import HumanService

OUT = sys.argv[sys.argv.index("--") + 1]

bpy.ops.wm.read_factory_settings(use_empty=True)

info = HumanService._create_default_human_info_dict()
info["name"] = "Sifa"
info["phenotype"].update({"gender": 0.0, "age": 0.42, "muscle": 0.45, "weight": 0.42,
                          "proportions": 0.75, "height": 0.52, "cupsize": 0.5, "firmness": 0.55})
info["phenotype"]["race"] = {"asian": 0.0, "caucasian": 1.0, "african": 0.0}
info["rig"] = "cmu_mb"
info["eyes"] = "high-poly/high-poly.mhclo"
info["eyebrows"] = "eyebrow001/eyebrow001.mhclo"
info["eyelashes"] = "eyelashes01/eyelashes01.mhclo"
info["hair"] = "long01/long01.mhclo"
info["clothes"] = ["male_casualsuit02/male_casualsuit02.mhclo", "shoes01/shoes01.mhclo"]
info["skin_mhmat"] = "young_caucasian_female/young_caucasian_female.mhmat"
info["skin_material_type"] = "ENHANCED_SSS"

settings = HumanService.get_default_deserialization_settings()
settings["subdiv_levels"] = 1
basemesh = HumanService.deserialize_from_dict(info, settings)

rig = basemesh.parent
print("RIG", rig.name if rig else None, "BONES", len(rig.data.bones) if rig else 0)
for o in bpy.data.objects:
    print("OBJ", o.name, o.type, [m.name for m in getattr(o.data, "materials", [])] if o.type == "MESH" else "")

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
