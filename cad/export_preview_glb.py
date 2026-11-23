"""Create view-only glTF/GLB from the same parametric B-rep solids.
GLB is NOT editable engineering CAD; use STEP and Python source instead.
"""
import trimesh
import build_high_fidelity as cad
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parents[1]/'cad'/'CruiserIII_Retrofit_VIEW_ONLY.glb'
cad.base.build();mod,parts,ge= cad.construct()
sc=trimesh.Scene()
items=[(p['solid'],cad.base.COLORS.get(p['color'],cad.base.COLORS['metal']),p['name']) for p in cad.base.REGISTRY]
items.extend((p['shape'],cad.COLORS[p['color']],p['name']) for p in parts)
for j,(solid,color,name) in enumerate(items):
    pts,indices=solid.tessellate(.75,.22)
    if len(indices)==0:continue
    mesh=trimesh.Trimesh(vertices=np.array([p.toTuple() for p in pts]),faces=np.array(indices),process=False)
    rgba=np.array([int(round(min(1,max(0,v))*255)) for v in color.toTuple()[:3]]+[255],dtype=np.uint8)
    mesh.visual.face_colors=np.tile(rgba,(len(indices),1))
    sc.add_geometry(mesh,node_name=name,geom_name=name)
    if j%100==0:print('mesh',j,flush=True)
OUT.write_bytes(sc.export(file_type='glb'))
print('GLB',OUT.stat().st_size)
