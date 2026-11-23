"""Render original parametric CadQuery solids with vtk. No image generation or texture substitution."""
import sys, importlib, math
from pathlib import Path
import vtk
from PIL import Image, ImageDraw, ImageFont
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'cad'))
import build_high_fidelity as model
base=model.base
base.build()
modules,parts,geo=model.construct(0)
items=[]
for p in base.REGISTRY:items.append((p['solid'],base.COLORS.get(p['color'],base.COLORS['metal']),p['name']))
for p in parts:items.append((p['shape'],model.COLORS[p['color']],p['name']))


def mk_actor(shape,color,name):
    points,indices=shape.tessellate(.95,.22)
    verts=vtk.vtkPoints()
    verts.SetNumberOfPoints(len(points))
    for i,p in enumerate(points):verts.SetPoint(i,p.x,p.y,p.z)
    triangles=vtk.vtkCellArray()
    for tri in indices:
        cell=vtk.vtkTriangle()
        for i in range(3):cell.GetPointIds().SetId(i,int(tri[i]))
        triangles.InsertNextCell(cell)
    pd=vtk.vtkPolyData();pd.SetPoints(verts);pd.SetPolys(triangles)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(pd);normals.SetFeatureAngle(45);normals.SplittingOff();normals.ConsistencyOn();normals.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());mapper.SetScalarVisibility(False)
    a=vtk.vtkActor();a.SetMapper(mapper)
    r,g,b=color.toTuple()[:3]
    prop=a.GetProperty();prop.SetColor(r,g,b);prop.SetAmbient(.21);prop.SetDiffuse(.75);prop.SetSpecular(.22);prop.SetSpecularPower(28)
    if name.startswith('BASE_'): prop.SetSpecular(.14)
    return a

print('Building render actors',len(items),flush=True)
actors=[]
for i,(shape,color,name) in enumerate(items):
    try:actors.append(mk_actor(shape,color,name))
    except Exception as exc:print('ACTOR FAILED',name,str(exc)[:100])
    if i%100==0:print('actors',i,flush=True)

REN=vtk.vtkRenderer(); REN.SetBackground(.972,.978,.986)
REN.SetUseFXAA(False)
for a in actors:REN.AddActor(a)
# ground plane is visual only
plane=vtk.vtkPlaneSource();plane.SetOrigin(-700,-500,-1.5);plane.SetPoint1(800,-500,-1.5);plane.SetPoint2(-700,500,-1.5)
plane.Update();pmap=vtk.vtkPolyDataMapper();pmap.SetInputConnection(plane.GetOutputPort());pactor=vtk.vtkActor();pactor.SetMapper(pmap);pactor.GetProperty().SetColor(.90,.92,.94);pactor.GetProperty().SetOpacity(.55);REN.AddActor(pactor)
light=vtk.vtkLight();light.SetPosition(-900,-400,1500);light.SetFocalPoint(-80,0,450);light.SetIntensity(1.15);REN.AddLight(light)
light2=vtk.vtkLight();light2.SetPosition(1100,1200,900);light2.SetFocalPoint(0,0,450);light2.SetIntensity(.56);REN.AddLight(light2)
win=vtk.vtkRenderWindow();win.OffScreenRenderingOn();win.AddRenderer(REN);win.SetSize(1500,1000);win.SetMultiSamples(0)
cam=REN.GetActiveCamera();cam.ParallelProjectionOn()
views={
 'hero_rear':((-1370,-1320,1050),(-35,-10,455),900),
 'hero_front':((1430,-1280,1020),(0,0,420),950),
 'side':((0,-1800,540),(0,0,435),950),
 'rear':((-1800,0,550),(-70,0,470),830),
 'module_detail':((-760,-650,755),(-352,-265,560),255),
 'underside':((-500,-850,160),(-50,-40,410),580),
}
for key,(pos,focal,scale) in views.items():
    cam.SetPosition(*pos);cam.SetFocalPoint(*focal);cam.SetViewUp(0,0,1);cam.SetParallelScale(scale*.59)
    REN.ResetCameraClippingRange();win.Render()
    w2i=vtk.vtkWindowToImageFilter();w2i.SetInput(win);w2i.ReadFrontBufferOff();w2i.Update()
    wr=vtk.vtkPNGWriter();wr.SetFileName(str(HERE/'images'/f'{key}_raw.png'));wr.SetInputConnection(w2i.GetOutputPort());wr.Write()
    print('Rendered',key,flush=True)
# Annotated presentation composites (not used as dimensional evidence)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';boldpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(fontpath,28);fontb=ImageFont.truetype(boldpath,43);small=ImageFont.truetype(fontpath,23)
for key in views:
    src=Image.open(HERE/'images'/f'{key}_raw.png').convert('RGB')
    canvas=Image.new('RGB',(src.width,src.height+122),'#f8fafc');canvas.paste(src,(0,110))
    d=ImageDraw.Draw(canvas)
    title={'hero_rear':'FRICTION RETROFIT  |  REAR QUARTER','hero_front':'FRICTION RETROFIT  |  FRONT QUARTER','side':'SIDE PROFILE  |  24-INCH REAR WHEELS','rear':'REAR PROFILE  |  TWO MOTOR MODULES','module_detail':'DRIVE MODULE  |  COMPONENT-LEVEL CAD','underside':'UNDERSEAT PACKAGING  |  CONCEPT'}[key]
    d.text((46,24),title,font=fontb,fill='#192b3c')
    d.text((49,78),'V0.4  •  CadQuery B-rep solids  •  photo-reconstructed base  •  NOT a validated build',font=small,fill='#526578')
    canvas.save(HERE/'images'/f'{key}.png')
# Quad views
from PIL import ImageOps
quad=Image.new('RGB',(1800,1320),'#e9eef3')
qds=ImageDraw.Draw(quad);qds.text((35,22),'CRUISER III — DETAILED RETROFIT / V0.4',fill='#223348',font=fontb)
for i,key in enumerate(['hero_rear','hero_front','side','module_detail']):
    raw=Image.open(HERE/'images'/f'{key}_raw.png').convert('RGB')
    resized=ImageOps.contain(raw,(870,570))
    x=24+(i%2)*900;y=95+(i//2)*610
    quad.paste(resized,(x,y))
    qds.text((x+18,y+555),key.replace('_',' ').upper(),fill='#2c3e50',font=small)
quad.save(HERE/'images'/'four_views_v04.png')
print('RENDER FINISHED')
