"""Cruiser III + two friction drive modules: high-detail mechanical *CONCEPT* 0.4.
This generates true editable B-rep solids (CadQuery) not image mesh.
Motor 42GP-775-EN external envelope derived from published NFP model (but encoder
housing, bolt-hole PCD and mounting details are *estimated*). Bearings 6000-2RS
standard boundary 10x26x8. Parent wheelchair is photo-reconstructed, UNMEASURED.
Do not construct an occupied device from these dimensions.
"""
import sys, json, math, importlib.util
from pathlib import Path
from dataclasses import asdict, dataclass
import cadquery as cq
from cadquery import Color
from cadquery.occ_impl.shapes import Solid

ROOT=Path(__file__).resolve().parents[1]
BASE_ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cruiser_base',str(BASE_ROOT/'cruiser_iii_base_parametric.py'))
base=importlib.util.module_from_spec(spec);sys.modules['cruiser_base']=base;spec.loader.exec_module(base)

@dataclass
class Specs:
    wheel_d:float=609.6                 # OEM 24in tire
    tire_center_y:float=297.5         # estimated from base model
    angle_deg:float=130
    roller_od:float=50
    roller_width:float=34
    roller_core_d:float=36
    drive_gear_d:float=42             # NFP 42GP-775
    drive_gear_len:float=43.5        # published 13:1 gearbox
    dc775_can_d:float=42             # vendor nominal 775 motor
    dc775_can_len:float=66.7         # reference 775 motor nominal, not specific NFP drawing
    encoder_len:float=15            # assumed envelope
    drive_shaft_d:float=8            # NFP published output D-shaft
    drive_shaft_len:float=22         # NFP published length
    gearbox_front_y:float=213       # wheelchair centerline abs
    roller_axle_d:float=10
    bearing_od:float=26             # 6000-2RS standard boundary
    bearing_bore:float=10
    bearing_w:float=8
    bearing_centers_y:tuple=(253,273)
    frame_clamp_bore:float=22.8      # base model tube OD nominal 22, unmeasured
    guide_slide_mm:float=15
    nominal_contact_preload_N:float=140 # placeholder, not backed by spring data
    bracket_web_t:float=20
    bracket_web_h:float=25
    battery_box:tuple=(174,96,76)
    driver_box:tuple=(112,82,43)

C=Specs(); PARTS=[]
COLORS={
 'base':Color(.38,.40,.44),'mag':Color(.17,.18,.20),'plastic':Color(.13,.15,.17),
 'steel':Color(.69,.73,.76),'steel_dark':Color(.48,.52,.56),'aluminum':Color(.72,.75,.79),
 'motor':Color(.13,.18,.24),'gearbox':Color(.72,.75,.79),'motor_label':Color(.12,.48,.65),
 'rubber':Color(.075,.09,.105),'roller':Color(.12,.27,.24),'printed':Color(.24,.29,.36),
 'spring':Color(.82,.70,.31),'electronics':Color(.1,.25,.29),'battery':Color(.15,.21,.31),
 'copper':Color(.83,.45,.17),'accent':Color(.92,.58,.22), 'bolt':Color(.68,.69,.70),
 'seal':Color(.11,.12,.14),'joystick':Color(.17,.18,.23),'green':Color(.21,.45,.35)
}

def add(A,shape,name,category,color='steel',verified='CONCEPT'):
    if isinstance(shape,cq.Workplane):shape=shape.val()
    if not shape.isValid():raise ValueError('Invalid solid '+name)
    A.add(shape,name=name,color=COLORS.get(color,Color(.7,.7,.7)))
    PARTS.append(dict(name=name,category=category,source_status=verified,color=color,shape=shape))

def V(v):return cq.Vector(*v)
def cyl(r,len,center,axis=(0,1,0)):
    d=V(axis).normalized(); p=V(center)
    return Solid.makeCylinder(r,len,p-d*(len/2),d)
def ring(ro,ri,length,center,axis=(0,1,0)):
    return cyl(ro,length,center,axis).cut(cyl(ri,length+1.0,center,axis))
def box(dim,center,rounding=0):
    q=cq.Workplane('XY').box(*dim)
    if rounding:
        try:q=q.edges().fillet(rounding)
        except Exception:pass
    return q.val().translate(center)
def tube(a,b,r):
    p=V(a);d=V(b)-p
    return Solid.makeCylinder(r,d.Length,p,d.normalized())
def plate_between(a,b,width=24,thick=6):
    aa=V(a);bb=V(b);length=((bb.x-aa.x)**2+(bb.z-aa.z)**2)**.5
    angle=math.degrees(math.atan2(bb.z-aa.z,bb.x-aa.x))
    # 20 x 25 x 2 mm nominal aluminum rectangular hollow tube; bolted end joints TBD
    q=cq.Workplane('XY').box(length,thick,width).val()
    bore=cq.Workplane('XY').box(length+1,thick-4,width-4).val()
    q=q.cut(bore)
    return q.rotate((0,0,0),(0,1,0),-angle).translate(tuple((aa+bb)*.5))
def hex_nut(r,height,center,axis='Y'):
    s=cq.Workplane('XY').polygon(6,2*r).extrude(height).val()
    if axis=='Y':s=s.rotate((0,0,0),(1,0,0),90)
    return s.translate(center)
def cyl_bolt(A,basepoint,axis,span,tag,head_r=5):
    p=V(basepoint);direction=V(axis).normalized()
    add(A,cyl(2.5,span,tuple(p+direction*span/2),tuple(direction)),tag+'_M5_shank','fastener','bolt','STANDARD DIAMETER; FIT TBD')
    add(A,cyl(head_r,4,tuple(p+direction*(span-2)),tuple(direction)),tag+'_head','fastener','steel_dark','VISUAL')
    add(A,hex_nut(head_r+1,4,tuple(p+direction*1)),tag+'_nut','fastener','steel_dark','VISUAL')

def motor(A,side,x,z,tag):
    """Axis along y; motor terminals toward center, gearbox and shaft toward wheel."""
    ysign=side; front=C.gearbox_front_y
    gear_center=side*(front-C.drive_gear_len/2)
    can_center=side*(front-C.drive_gear_len-C.dc775_can_len/2)
    enc_center=side*(front-C.drive_gear_len-C.dc775_can_len-C.encoder_len/2)
    add(A,cyl(C.drive_gear_d/2,C.drive_gear_len,(x,gear_center,z)),tag+'_gearbox_42mm','gearmotor','gearbox','NFP GEARMOTOR ENVELOPE')
    # Decorative steel seams on gearbox and front machined face ring
    for offset in (7,27,42):
        add(A,ring(21.15,20.45,.7,(x,side*(front-offset),z)),tag+f'_gear_seam_{offset}','gearmotor','steel_dark','VISUAL')
    add(A,cyl(19.4,3,(x,side*(front+1.2),z)),tag+'_gear_output_flange','gearmotor','steel','PCD UNVERIFIED')
    # approximate tapped holes 32mm PCD and M4 size; NOT actual NFP mounting drawing
    for i in range(4):
        a=i*math.pi/2+math.pi/4
        xx=x+16*math.cos(a); zz=z+16*math.sin(a)
        add(A,cyl(2.1,1.1,(xx,side*(front+2.5),zz)),tag+f'_front_fastener_head_{i}','gearmotor','steel_dark','UNVERIFIED PCD')
    # motor can with rounded face and label strip
    add(A,cyl(C.dc775_can_d/2,C.dc775_can_len,(x,can_center,z)),tag+'_RS775_motor_can','gearmotor','motor','CAN 42x66.7 NOMINAL')
    add(A,ring(21.2,20.2,1.1,(x,side*(front-C.drive_gear_len-3),z)),tag+'_motor_seam','gearmotor','gearbox','VISUAL')
    add(A,cyl(20,3,(x,side*(front-C.drive_gear_len-C.dc775_can_len+1),z)),tag+'_motor_rear_cap','gearmotor','plastic','VISUAL')
    add(A,cyl(18.5,C.encoder_len,(x,enc_center,z)),tag+'_encoder_cap','gearmotor','plastic','ENCODER DIMENSION ESTIMATED')
    # Encoder multi-pin connector and trailing lead stubs
    add(A,box((13,7,11),(x+2,side*(front-C.drive_gear_len-C.dc775_can_len-C.encoder_len-3),z+10),1),tag+'_encoder_connector','gearmotor','green','ESTIMATED')
    for j,dx in enumerate((-5,5)):
        add(A,box((4,7,2.8),(x+dx,side*(front-C.drive_gear_len-C.dc775_can_len-5),z-5),.4),tag+f'_power_terminal_{j}','gearmotor','copper','ESTIMATED')
    # NFP 8mm D-shaft: same volume, flat removes material from one side
    shaft_center=side*(front+C.drive_shaft_len/2+2.0)
    shaft=cyl(4,C.drive_shaft_len,(x,shaft_center,z))
    shaft=shaft.cut(box((5,C.drive_shaft_len+1,3),(x,shaft_center,z+4.1)))
    add(A,shaft,tag+'_output_8mm_D_shaft','gearmotor','steel','NFP SHAFT 8x22 PUBLISHED; FLAT DEPTH CONCEPT')

def bearing(A,x,y,z,tag):
    # actual standard boundary geometry of 6000-2RS (10x26x8mm)
    add(A,ring(13,10.6,8,(x,y,z)),tag+'_outer_race','bearings','steel','ISO BEARING BOUNDARY')
    add(A,ring(7.0,5.0,8,(x,y,z)),tag+'_inner_race','bearings','steel','ISO BEARING BOUNDARY')
    for sign in (-1,1):
        add(A,ring(10.6,7.0,.6,(x,y+sign*3.7,z)),tag+f'_rubber_seal_{sign}','bearings','seal','SIMPLIFIED SEALS')
    # bearing seat block, actual press fit must be engineered; simplified swept saddle
    holder=box((39,13,42),(x+22,y,z),3).cut(cyl(13.1,15,(x,y,z)))
    add(A,holder,tag+'_aluminum_pillow_mount','bearing_support','aluminum','BEARING HOUSING HOLES NOT VERIFIED')
    for dz in (-12,12):
        add(A,cyl(3.5,6,(x+31,y,z+dz),(0,1,0)),tag+f'_mount_screw_{dz}','fasteners','steel_dark','VISUAL')

def roller(A,side,x,z,tag):
    yy=side*C.tire_center_y
    # 50 mm OD 34mm wide, bonded rubber tire on aluminum core
    add(A,ring(18.0,5.05,34,(x,yy,z)),tag+'_aluminum_core','roller','aluminum','CORE GEOMETRY CONCEPT')
    add(A,ring(25,18.05,34,(x,yy,z)),tag+'_rubber_tread','roller','roller','50x34 DESIGN ASSUMPTION')
    for j in range(2):
        y=yy+side*(-13 if j==0 else 13)
        add(A,ring(20.2,5.1,2.1,(x,y,z)),tag+f'_side_retainer_{j}','roller','steel_dark','CONCEPT')
    # contact tread scored lines to make machining/finish realistic (not validated for grip)
    for n in range(20):
        a=math.pi*2*n/20
        xx=x+25*math.cos(a);zz=z+25*math.sin(a)
        add(A,cyl(.52,32,(xx,yy,zz)),tag+f'_tread_groove_{n:02d}','roller_detail','rubber','VISUAL ONLY')

def clamp(A,side,z,tag):
    sy=side*base.S.seat_rail_y
    sx=-217-(z-466)*(17/204)
    # split along front/back X, two 24 mm-thick half shells clamp around 22 mm tube
    raw=box((49,44,29),(sx,sy,z),2).cut(cyl(C.frame_clamp_bore/2,30,(sx,sy,z),(0,0,1)))
    # separate left and right halves at Y=sy
    for k,offset in enumerate((-1,1)):
        half=raw.intersect(box((50,22,31),(sx,sy+offset*11,z)))
        add(A,half,tag+f'_clamp_jaw_{k}','frame_clamps','aluminum','FRAME TUBE Ø22 ESTIMATE')
    for xo in (-17,17):
        cyl_bolt(A,(sx+xo,sy-31,z),(0,1,0),62,tag+f'_clamp_{xo}')
    return (sx,sy,z)

def spring_helix(A,start,unit,tag):
    # parametric spring wound from wire; externally realistic but stiffness unverified
    length=36; radius=8; wire_r=1.35; turns=6
    pts=[]; start=V(start); e=V(unit).normalized(); tangent=V((0,1,0)); b=e.cross(tangent).normalized()
    for i in range(turns*16+1):
        theta=2*math.pi*turns*i/(turns*16)
        p=start+e*(length*i/(turns*16))+tangent*(radius*math.cos(theta))+b*(radius*math.sin(theta))
        pts.append(p)
    # coil built of small finite cylindrical segments (editable CAD solids), avoid expensive spline sweep
    for k in range(0,len(pts)-1,2):
        if k+2 <len(pts):
            add(A,tube(tuple(pts[k]),tuple(pts[k+2]),wire_r),tag+f'_coil_segment_{k//2:02d}','engagement_spring','spring','VISUAL; SPRING RATE UNKNOWN')

def construct(release=0):
    global PARTS
    PARTS=[]
    A=cq.Assembly(name='Cruiser_III_v04_high_detail_FRICTION_CONCEPT')
    a=math.radians(C.angle_deg)
    u=(math.cos(a),0,math.sin(a))
    R=C.wheel_d/2+C.roller_od/2+release
    wx=base.S.rear_axle_x; wz=base.S.rear_diameter/2
    x=wx+R*u[0]; z=wz+R*u[2]
    # Fixed frame mounts and bracket anchor are tied to the engaged reference,
    # while the carriage translates along its radial guide when released.
    x_engaged=wx+(C.wheel_d/2+C.roller_od/2)*u[0]
    z_engaged=wz+(C.wheel_d/2+C.roller_od/2)*u[2]
    for side in (-1,1):
        tag='RIGHT' if side<0 else 'LEFT'
        # actual base chair wheels and frame remain model reference
        up=clamp(A,side,555,tag+'_UPPER');lo=clamp(A,side,479,tag+'_LOWER')
        # two steel plates per side; structural load path (plate geometry not verified)
        anchor=(x_engaged+u[0]*40,z_engaged+u[2]*40)
        for k,oy in enumerate((side*223,side*247)):
            add(A,plate_between((up[0],oy,555),(anchor[0],oy,anchor[1]+11),25,20),tag+f'_upper_steel_web_{k}','primary_load_path','steel','UNMEASURED FRAME/20x25x2 AL TUBE')
            add(A,plate_between((lo[0],oy,479),(anchor[0],oy,anchor[1]-11),25,20),tag+f'_lower_steel_web_{k}','primary_load_path','steel','UNMEASURED FRAME/20x25x2 AL TUBE')
            # mounting bolts at both ends
            for j,(px,pz) in enumerate(((up[0],555),(anchor[0],anchor[1]))):
                add(A,cyl(5,8,(px,oy,pz)),tag+f'_web_{k}_M8_pin_{j}','fasteners','steel_dark','CONCEPT PIN')
        # radial slide guide: two ground shafts connecting fixed station and mobile carriage
        for j,oy in enumerate((side*222,side*247)):
            start=(x_engaged+u[0]*6,oy,z_engaged+u[2]*6)
            end=(x_engaged+u[0]*66,oy,z_engaged+u[2]*66)
            add(A,tube(start,end,4),tag+f'_linear_guide_shaft_{j}','engagement','steel','8mm ROD; FIT UNVERIFIED')
            carrier=(x+u[0]*28,oy,z+u[2]*28)
            add(A,box((21,16,25),carrier,2),tag+f'_slider_carriage_{j}','engagement','aluminum','SLIDING KINEMATICS CONCEPT')
        # bridge between slide carriages and bearing carriers
        add(A,box((58,35,29),(x+18,side*256,z),3),tag+'_metal_motor_carriage','metal_plate','aluminum','CONCEPT ENVELOPE')
        # spring pushes roller inward toward the tire (no actual performance rating)
        spring_start=(x_engaged+u[0]*14,side*234,z_engaged+u[2]*14)
        spring_helix(A,spring_start,u,tag+'_preload_spring')
        add(A,cyl(4,8,(x+u[0]*56,side*234,z+u[2]*56),(0,1,0)),tag+'_spring_adjuster','engagement','accent','MECHANISM NOT VALIDATED')
        # cam lever disengage drawn realistically with pivot and ergonomic grip
        pivot=(x_engaged+u[0]*40,side*273,z_engaged+u[2]*40)
        add(A,cyl(5,26,pivot),tag+'_quick_release_clevis','engagement','steel','CONCEPT')
        add(A,plate_between(pivot,(pivot[0]+38,pivot[1],pivot[2]+28),10,6),tag+'_release_lever_steel','engagement','steel_dark','CONCEPT')
        add(A,cyl(8,22,(pivot[0]+38,pivot[1],pivot[2]+28),(1,0,0)),tag+'_release_lever_knob','engagement','printed','PRINT CANDIDATE')
        # motor-gear assembly, bearing-supported 10mm shaft, sleeve coupling 8->10mm
        motor(A,side,x,z,tag)
        coupling_y=side*238
        add(A,cyl(11,29,(x,coupling_y,z)),tag+'_jaw_flex_coupling_8_to_10','coupling','steel_dark','COUPLING CONCEPT')
        for ky in (-5,5):
            add(A,cyl(3.5,6,(x+8,coupling_y+side*ky,z+5)),tag+f'_coupling_grub_screw_{ky}','fasteners','steel','VISUAL')
        add(A,cyl(5,80,(x,side*285,z)),tag+'_steel_axle_10mm','roller_shaft','steel','STANDARD ROUND BAR NOMINAL')
        for k,by in enumerate(C.bearing_centers_y):
            bearing(A,x,side*by,z,tag+f'_6000_2RS_{k}')
        roller(A,side,x,z,tag)
    # UNDERSEAT boxes remain preliminary envelope; ribs and fastener detailing for visualization
    def enclosure(center,dims,tag,color):
        dx,dy,dz=dims
        shell=box(dims,center,5).cut(box((dx-5,dy-5,dz-6),(center[0],center[1],center[2]+3),3))
        add(A,shell,tag+'_shell','electronics_enclosure',color,'UNSOURCED DIMENSIONS')
        add(A,box((dx+2,dy+2,3),(center[0],center[1],center[2]+dz/2+1),3),tag+'_lid','enclosure_print','printed','PRINT CANDIDATE')
        for sx in (-1,1):
            for sy in (-1,1):
                add(A,cyl(2.2,3,(center[0]+sx*(dx/2-10),center[1]+sy*(dy/2-10),center[2]+dz/2+4),(0,0,1)),tag+f'_lid_screw_{sx}_{sy}','fasteners','steel','VISUAL')
        add(A,box((14,9,10),(center[0]+dx/2+3,center[1],center[2]-dz/6),1),tag+'_cable_gland','connectors','plastic','CONCEPT')
    enclosure((44,0,425),C.battery_box,'UNDERSEAT_24V_BATTERY','battery')
    enclosure((-140,0,400),C.driver_box,'UNDERSEAT_DUAL_CONTROLLER','electronics')
    # actual PCB dimensions unknown: color-coded heat sink fins / terminal connections, accessible top
    for i in range(8):
        add(A,box((48,2,13),(-156,-28+i*7,431),.3),f'DRIVER_HEATSINK_FIN_{i:02d}','electronics','aluminum','VISUAL / DIMENSION UNSOURCED')
    add(A,box((50,35,18),(-83,3,412),3),'UNDERSEAT_FUSE_AND_MAIN_SWITCH','power','printed','CONCEPT')
    add(A,cyl(9,8,(-83,3,424),(0,0,1)),'MAIN_POWER_SWITCH_CAP','power','accent','VISUAL')
    # spring centered joystick on armrest
    joystick_xy=(36,-275)
    add(A,box((60,57,30),(joystick_xy[0],joystick_xy[1],694),7),'JOYSTICK_ENCLOSURE','joystick','printed','CLAMP DIMENSIONS UNVERIFIED')
    for sy in (-1,1):
        add(A,box((32,7,14),(36,joystick_xy[1]+sy*27,674),2),f'JOYSTICK_ARMREST_SADDLE_{sy}','joystick','steel_dark','CONCEPT')
    add(A,cyl(15,7,(36,-275,713),(0,0,1)),'JOYSTICK_RUBBER_BOOT','joystick','rubber','VISUAL')
    add(A,cyl(4.2,32,(36,-275,735),(0,0,1)),'JOYSTICK_STALK','joystick','steel','VISUAL')
    add(A,cyl(11,24,(36,-275,757),(0,0,1)),'JOYSTICK_GRIP','joystick','joystick','VISUAL')
    add(A,cyl(3.5,1,(15,-293,710),(0,0,1)),'JOYSTICK_STATUS_LED','joystick','green','VISUAL')
    dims={'axle_radius_mm':C.wheel_d/2,'roller_center_left_mm':[x,C.tire_center_y,z],
          'roller_center_right_mm':[x,-C.tire_center_y,z],
          'motor_mount_gearing':'NFP-42GP-775-EN 24V 13:1 candidate; no actual purchased motor; mounting PCD estimated',
          'radial_gap_mm':release, 'radial_contact_assumed':release==0}
    return A,PARTS.copy(),dims


def build(export_full=True):
    base.build()
    modules,parts,dims=construct(0)
    assembly=cq.Assembly(name='CruiserIII_Photo_Reconstruction_With_Detailed_Friction_Modules')
    for p in base.REGISTRY:
        assembly.add(p['solid'],name='BASE_'+p['name'],color=base.COLORS.get(p['color'],base.COLORS['metal']))
    for p in parts:assembly.add(p['shape'],name=p['name'],color=COLORS[p['color']])
    if export_full:
        print('EXPORT: full STEP',len(parts),flush=True)
        assembly.save(str(ROOT/'cad'/'CruiserIII_Retrofit_Detailed_V04.step'),exportType='STEP')
    print('EXPORT: detachable assembly STEP',flush=True)
    modules.save(str(ROOT/'cad'/'Friction_Drive_Modules_Detailed_V04.step'),exportType='STEP')
    print('EXPORT: released geometry STEP',flush=True)
    released,released_parts,rdims=construct(C.guide_slide_mm)
    released.save(str(ROOT/'cad'/'Friction_Drive_Modules_Released_V04.step'),exportType='STEP')
    # Printed preview STL components only, not ready-to-print nor use
    made=[]
    for p in parts:
        if p['category'] in ('enclosure_print','joystick') and ('lid' in p['name'].lower() or 'ENCLOSURE' in p['name'] or 'GRIP' in p['name']):
            filename=p['name']+'.stl'
            cq.exporters.export(p['shape'],str(ROOT/'cad'/filename),tolerance=.14,angularTolerance=.20)
            made.append(filename)
    manifest={'base_solids':len(base.REGISTRY),'retrofit_solids':len(parts),'total_solids':len(base.REGISTRY)+len(parts),
              'config':asdict(C),'contact_geometry':dims,'released_geometry':rdims,'printed_STL_visual_only':made,
              'parts':[ {k:v for k,v in p.items() if k!='shape'} for p in parts],
              'limitations':['Wheelchair frame reconstructed from photos, no physical measurements',
              'Gear motor cylindrical dimensions based on manufacturer family, bolt-circle and encoder estimate',
              'Battery and controller packaging approximate: no exact products selected',
              'Non-functional engagement hinge, spring rate and sliding rail fit not engineered',
              'No full-chair FEA, structural fatigue, occupant validation or brake failure safety verification']}
    (ROOT/'cad'/'manifest_v04.json').write_text(json.dumps(manifest,indent=2))
    print('COMPLETE',manifest['total_solids'],'parts',flush=True)
    return assembly,parts,manifest

if __name__=='__main__':build()
