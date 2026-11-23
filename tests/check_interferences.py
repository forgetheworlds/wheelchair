"""Geometry-only collision screening against photo-reconstructed base (NOT measured CAD)."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'cad'))
import build_high_fidelity as cad
cad.base.build();A,parts,geometry=cad.construct(0)
focus=['RS775_motor_can','gearbox_42mm','rubber_tread','metal_motor_carriage','UNDERSEAT_24V_BATTERY_shell',
       'UNDERSEAT_DUAL_CONTROLLER_shell','JOYSTICK_ENCLOSURE', 'steel_axle_10mm','release_lever_steel']
selected=[p for p in parts if any(q in p['name'] for q in focus)]
baseparts=cad.base.REGISTRY

def overlap(a,b,tol=.001):
    return all((getattr(a,d+'min')<getattr(b,d+'max')-tol and getattr(a,d+'max')>getattr(b,d+'min')+tol) for d in ('x','y','z'))
results=[];tested=0
for p in selected:
 a=p['shape'];bb=a.BoundingBox()
 for q in baseparts:
    b=q['solid'];bbb=b.BoundingBox()
    if not overlap(bb,bbb):continue
    tested+=1
    intr=a.intersect(b)
    volume=float(intr.Volume())
    if volume>2.0:
        results.append({'retrofit':p['name'],'wheelchair':q['name'],'intersect_volume_mm3':round(volume,1),
                        'base_category':q['group']})
report={'tested_broad_phase_candidates':tested,'significant_overlap_count':len(results),
        'significant_overlaps':sorted(results,key=lambda o:-o['intersect_volume_mm3']),
        'warning':'Base chair approximated. Some contacts are expected (clamps, joystick mount). This checks only selected components.'}
(ROOT/'analysis'/'geometric_interference_screen.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
