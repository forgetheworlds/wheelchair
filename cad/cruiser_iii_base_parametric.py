"""Drive Medical Cruiser III — editable, multi-part CAD *reference reconstruction*.

CAD units: millimetres. X=forward, Y=left/right, Z=up.
Model: conceptual 18-inch-seat Cruiser III with swing-away footrests.
Manufacturer specifications constrain exterior dimensions. Most individual tube
locations, joints, fastener profiles, and hub details are estimates from the
manufacturer's parts drawing and product photographs, NOT measured geometry.

Run: python cruiser_iii_parametric.py
Requires: cadquery 2.8 (Python), OCP.
No motorization or retrofit included.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import math, json
import cadquery as cq
from cadquery import Color
from cadquery.occ_impl.shapes import Solid

OUT = Path(__file__).resolve().parent

@dataclass
class Spec:
    # OEM published references, mm
    seat_width: float = 18*25.4
    seat_depth: float = 16.5*25.4     # adjustable 16–18 inch, intermediate *estimated configuration*
    seat_height: float = 19*25.4      # adjustable 17.5–19.5 inch
    back_height: float = 16*25.4
    overall_width: float = 26*25.4
    overall_height: float = 35*25.4
    overall_length: float = 42*25.4  # w/ foot riggings
    rear_diameter: float = 24*25.4
    front_diameter: float = 8*25.4
    # estimated from photos / exploded diagram — verify from a physical chair
    rear_axle_x: float = -153.0
    rear_wheel_y: float = 297.5
    front_caster_x: float = 279.0
    front_caster_y: float = 241.0
    seat_rail_y: float = 239.0
    seat_back_x: float = -209.0
    seat_front_x: float = 209.0
    tube_outer_diameter: float = 22.0
    tire_width: float = 33.0
    rear_handrim_radius: float = 264.0
    footrest_front_x: float = 572.0
    footplate_center_x: float = 520.0

S=Spec()
A=cq.Assembly(name='Cruiser_III_18inch_Base_ONLY_Parametric_Reference')
REGISTRY=[]
COLORS={
    'metal': Color(0.42,0.44,0.46),
    'metal2': Color(0.60,0.62,0.64),
    'plastic': Color(0.12,0.13,0.15),
    'rubber': Color(0.09,0.10,0.11),
    'upholstery': Color(0.19,0.21,0.23),
    'pad': Color(0.11,0.12,0.14),
    'highlight': Color(0.30,0.32,0.34),
}

def add(obj, name, color='metal', category=''):
    """Keep every component as a named CAD solid, not a fused image mesh."""
    if isinstance(obj,cq.Workplane): obj=obj.val()
    if not obj.isValid(): raise ValueError('Bad solid '+name)
    A.add(obj,name=name,color=COLORS.get(color,color))
    REGISTRY.append(dict(name=name,group=category or name.split('_')[0], color=color,solid=obj))

def cylinder(rad, length, center, axis=(0,1,0)):
    v=cq.Vector(*axis).normalized(); c=cq.Vector(*center)
    return Solid.makeCylinder(rad, length, c-v*(length/2),v)

def tube(a,b,rad=None):
    if rad is None: rad=S.tube_outer_diameter/2
    p=cq.Vector(*a); q=cq.Vector(*b); v=q-p
    return Solid.makeCylinder(rad,v.Length,p,v.normalized())

def joint(a,b,rad=None):
    """Segment cylinder with rounded junctions (appearance, not exact bent tubing)."""
    return tube(a,b,rad)

def block(x,y,z,center):
    return cq.Workplane('XY').box(x,y,z).val().moved(cq.Location(cq.Vector(*center)))

def ring_y(r_outer,r_inner,width,center):
    return cylinder(r_outer,width,center).cut(cylinder(r_inner,width+1,center))

def torus_y(major,minor,center):
    return Solid.makeTorus(major,minor,cq.Vector(*center),cq.Vector(0,1,0))

def wheel_rear(side):
    name='left' if side==1 else 'right'
    wy=side*S.rear_wheel_y
    xx=S.rear_axle_x
    zz=S.rear_diameter/2
    # Product image: mag-style 8 spoke rim, not bicycle wire spokes
    add(ring_y(S.rear_diameter/2, S.rear_diameter/2-27, S.tire_width,(xx,wy,zz)),f'{name}_rear_tire','rubber','rear_wheels')
    add(ring_y(S.rear_diameter/2-29, S.rear_diameter/2-42, 14,(xx,wy,zz)),f'{name}_composite_outer_rim','plastic','rear_wheels')
    add(cylinder(20,34,(xx,wy,zz)),f'{name}_rear_hub','plastic','rear_wheels')
    # Eight molded cast-looking spokes. Their placement is photographic approximation.
    for i in range(8):
        angle=2*math.pi*i/8
        inner=24; outer=S.rear_diameter/2-37
        p=(xx+math.cos(angle)*inner,wy,zz+math.sin(angle)*inner)
        q=(xx+math.cos(angle)*outer,wy,zz+math.sin(angle)*outer)
        add(tube(p,q,8),f'{name}_mag_spoke_{i+1:02d}','plastic','rear_wheels')
    hy=wy+side*26
    add(torus_y(S.rear_handrim_radius,5,(xx,hy,zz)),f'{name}_handrim','metal2','rear_wheels')
    for i in range(8):
        theta=2*math.pi*i/8
        xh=xx+math.cos(theta)*S.rear_handrim_radius
        zh=zz+math.sin(theta)*S.rear_handrim_radius
        add(tube((xh,wy+side*7,zh),(xh,hy,zh),3),f'{name}_handrim_spacer_{i+1:02d}','metal2','rear_wheels')
    add(cylinder(8,45,(xx,side*263,zz)),f'{name}_rear_axle','metal2','rear_wheels')

def wheel_front(side):
    name='left' if side==1 else 'right'
    fx=S.front_caster_x; fy=side*S.front_caster_y
    z=S.front_diameter/2
    add(ring_y(S.front_diameter/2,S.front_diameter/2-20,28,(fx,fy,z)),f'{name}_caster_tire','rubber','front_casters')
    add(ring_y(S.front_diameter/2-22,S.front_diameter/2-33,16,(fx,fy,z)),f'{name}_caster_rim','plastic','front_casters')
    add(cylinder(12,32,(fx,fy,z)),f'{name}_caster_hub','plastic','front_casters')
    for i in range(5):
        t=2*math.pi*i/5
        p=(fx+math.cos(t)*16,fy,z+math.sin(t)*16)
        q=(fx+math.cos(t)*(S.front_diameter/2-29),fy,z+math.sin(t)*(S.front_diameter/2-29))
        add(tube(p,q,5),f'{name}_caster_spoke_{i+1:02d}','plastic','front_casters')
    # fork straddles wheel on both sides: two slanted blades, bridge and swivel stem
    for offset,loc in ((-1,'inner'),(1,'outer')):
        y=fy+offset*23
        add(tube((fx,y,z),(fx-11,y,203),8),f'{name}_fork_{loc}','metal2','front_casters')
    add(tube((fx-11,fy-25,203),(fx-11,fy+25,203),9),f'{name}_fork_bridge','metal2','front_casters')
    add(tube((fx-11,fy,203),(fx-16,fy,292),11),f'{name}_caster_steerer','metal2','front_casters')
    add(cylinder(15,30,(fx-14,fy,279),(0,0,1)),f'{name}_caster_bearing','plastic','front_casters')

def frame_sides(side):
    name='left' if side==1 else 'right'
    y=side*S.seat_rail_y
    # frame proportions from Cruiser exploded assembly. Straight tubes approximate bends.
    runs=[
      ('seat_rail',(-218,y,466),(228,y,466),11),
      ('back_post_low',(-217,y,466),(-234,y,670),11),
      ('back_post_high',(-234,y,670),(-248,y,862),11),
      ('rear_grip_slope',(-248,y,862),(-271,y,880),10),
      ('front_frame_down',(218,y,466),(250,y,290),11),
      ('caster_support',(250,y,290),(S.front_caster_x-13,side*S.front_caster_y,273),11),
      ('rear_down',(-207,y,460),(-218,y,265),11),
      ('rear_lower',(-218,y,265),(92,y,230),11),
      ('lower_front',(92,y,230),(250,y,290),11),
      ('stiffener',(-194,y,413),(75,y,278),8),
    ]
    for label,a,b,rad in runs:
        add(tube(a,b,rad),f'{name}_frame_{label}','metal','side_frame')
    add(block(38,36,24,(-220,y,466)),f'{name}_rear_seat_saddle','plastic','side_frame')
    add(block(35,40,24,(214,y,465)),f'{name}_front_seat_saddle','plastic','side_frame')
    add(cylinder(16,32,(245,y,275),(0,0,1)),f'{name}_caster_headset','plastic','side_frame')
    # Rear back push grip angled backwards at very top
    add(tube((-269,y,879),(-309,y,879),13),f'{name}_push_grip','rubber','side_frame')
    # wheel lock, mounted to rail ahead of wheel; not operational mechanism
    ax=80; az=471
    add(block(45,24,26,(ax,y+side*23,az)),f'{name}_wheel_lock_mount','plastic','wheel_locks')
    add(tube((ax+5,y+side*29,az),(ax+75,y+side*52,450),5.5),f'{name}_wheel_lock_shoe_arm','metal2','wheel_locks')
    add(block(23,17,18,(ax+78,y+side*52,450)),f'{name}_wheel_lock_tip','rubber','wheel_locks')
    add(tube((ax-2,y+side*30,az),(ax-24,y+side*26,546),7),f'{name}_wheel_lock_lever','metal2','wheel_locks')
    add(cylinder(11,32,(ax-24,y+side*26,548),(1,0,0)),f'{name}_wheel_lock_grip','plastic','wheel_locks')

def arms(side):
    name='left' if side==1 else 'right'
    y=side*(S.seat_width/2+29)
    # Flip-back/removable desk-length arms, continuous appearance formed from segments.
    add(tube((-168,y,473),(-168,y,649),9),f'{name}_arm_rear_post','metal2','armrests')
    add(tube((-168,y,649),(125,y,649),9),f'{name}_arm_top_rail','metal2','armrests')
    add(tube((125,y,649),(169,y,625),9),f'{name}_arm_front_curve','metal2','armrests')
    add(tube((169,y,625),(178,y,487),9),f'{name}_arm_front_post','metal2','armrests')
    add(block(258,52,30,(-6,y,673)),f'{name}_arm_pad','pad','armrests')
    add(block(255,6,81,(-9,y-side*7,566)),f'{name}_arm_side_guard','plastic','armrests')
    add(cylinder(12,30,(-167,y,484),(0,0,1)),f'{name}_arm_release_collar','metal2','armrests')

def footrests(side):
    name='left' if side==1 else 'right'
    y=side*(S.seat_width/2-20)
    # Swing-away removable rigging, approximate struts and footplate silhouette.
    path=[((229,y,463),(294,y,420)),((294,y,420),(380,y,260)),
          ((380,y,260),(464,y,148))]
    for j,(a,b) in enumerate(path,1):
        add(tube(a,b,10),f'{name}_footrest_tube_{j}','metal2','footrests')
    add(cylinder(15,43,(229,y,445),(0,0,1)),f'{name}_footrest_hinge','plastic','footrests')
    add(tube((465,y,148),(525,y,148),8),f'{name}_footrest_plate_stem','metal2','footrests')
    # Rectangular plate with rounded edges; plastic tread with a slight upturned front lip.
    cy=y+side*31
    plate=cq.Workplane('XY').box(148,145,12).edges('|Z').fillet(9).translate((S.footplate_center_x,cy,124)).val()
    add(plate,f'{name}_footplate','plastic','footrests')
    add(block(13,145,17,(S.footplate_center_x+68,cy,138)),f'{name}_footplate_front_lip','plastic','footrests')
    add(cylinder(12,36,(442,y,147)),f'{name}_footrest_peg','plastic','footrests')

def structure():
    # The sling, back upholstery, central X-cross brace and connector bands.
    seat_z=S.seat_height - 5
    # Cushion/sling not a rigid slab, approximated as a thin supported rectangle
    add(block(S.seat_depth,S.seat_width,14,(0,0,seat_z)), 'seat_sling', 'upholstery','upholstery')
    add(block(10,S.seat_width,325,(-231,0,662)), 'backrest_fabric', 'upholstery','upholstery')
    # Two top bars and a front/rear tie for seat fabric and folding arms.
    for x,lab in [(-194,'rear'),(200,'front')]:
        add(tube((x,-S.seat_rail_y,seat_z-20),(x,S.seat_rail_y,seat_z-20),8),f'seat_{lab}_cross_member','metal','crossframe')
    # Two crossed bars are angled diagonally both front/back and left/right
    add(tube((-135,-228,380),(142,228,288),9), 'folding_crossbrace_A','metal2','crossframe')
    add(tube((-135,228,380),(142,-228,288),9), 'folding_crossbrace_B','metal2','crossframe')
    add(tube((-150,-221,307),(-150,221,307),8),'rear_cross_tie','metal2','crossframe')
    add(tube((140,-225,325),(140,225,325),8),'front_cross_tie','metal2','crossframe')
    # rear seat cross stabilizer
    add(tube((-233,-S.seat_rail_y,530),(-233,S.seat_rail_y,530),7),'rear_backrest_tie','metal2','crossframe')


def build():
    structure()
    for side in (-1,1):
        frame_sides(side)
        wheel_rear(side)
        wheel_front(side)
        arms(side)
        footrests(side)
    return A

def main():
    build()
    report={'CAD_units':'mm', 'model':'Cruiser III 18-inch nominal reference reconstruction',
            'known_dimensions':{k:v for k,v in asdict(S).items() if k in {'seat_width','seat_depth','seat_height','back_height','overall_width','overall_height','overall_length','rear_diameter','front_diameter'}},
            'assumed_dimensions':{k:v for k,v in asdict(S).items() if k not in {'seat_width','seat_depth','seat_height','back_height','overall_width','overall_height','overall_length','rear_diameter','front_diameter'}},
            'components':[{'name':p['name'],'category':p['group']} for p in REGISTRY],
            'component_count':len(REGISTRY), 'purpose':'Visual assembly/retrofit space planning ONLY. Not a manufacturing drawing.'}
    (OUT/'components_and_parameters.json').write_text(json.dumps(report,indent=2))
    print('components',len(REGISTRY), flush=True)
    A.save(str(OUT/'Cruiser_III_base_reference.step'),exportType='STEP')
    print('STEP exported', (OUT/'Cruiser_III_base_reference.step').stat().st_size,flush=True)
    return report

if __name__=='__main__': main()
