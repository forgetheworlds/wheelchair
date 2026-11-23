from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak,KeepTogether,HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Cruiser_III_Engineering_Review_V04.pdf'
NAVY=colors.HexColor('#183248');INK=colors.HexColor('#253748');TEAL=colors.HexColor('#13758b');GRAY=colors.HexColor('#596b79');PALE=colors.HexColor('#e9f1f4');RED=colors.HexColor('#9c3f3c')
PDFREG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
PDFBOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DejaVu',PDFREG));pdfmetrics.registerFont(TTFont('DejaVuB',PDFBOLD))
styles={
 'title':ParagraphStyle('title',fontName='DejaVuB',fontSize=23,leading=29,textColor=NAVY,spaceAfter=8),
 'sub':ParagraphStyle('sub',fontName='DejaVu',fontSize=10.4,leading=15,textColor=GRAY,spaceAfter=14),
 'h':ParagraphStyle('h',fontName='DejaVuB',fontSize=15,leading=19,textColor=NAVY,spaceBefore=10,spaceAfter=10),
 'h2':ParagraphStyle('h2',fontName='DejaVuB',fontSize=10.8,leading=15,textColor=TEAL,spaceBefore=9,spaceAfter=5),
 'p':ParagraphStyle('p',fontName='DejaVu',fontSize=9,leading=14.2,textColor=INK,spaceAfter=7),
 'tiny':ParagraphStyle('tiny',fontName='DejaVu',fontSize=7.6,leading=11.8,textColor=GRAY,spaceAfter=5),
 'em':ParagraphStyle('em',fontName='DejaVuB',fontSize=9,leading=14,textColor=RED,spaceAfter=8),
 'cell':ParagraphStyle('cell',fontName='DejaVu',fontSize=8,leading=11.8,textColor=INK),
 'cellbold':ParagraphStyle('cellbold',fontName='DejaVuB',fontSize=8,leading=11.8,textColor=NAVY),
 'bullet':ParagraphStyle('bullet',fontName='DejaVu',fontSize=8.7,leading=13,leftIndent=10,firstLineIndent=-9,spaceAfter=5),
}
PAGE_W,PAGE_H=A4
content_w=PAGE_W-80

def para(txt,sty='p'):return Paragraph(txt,styles[sty])
def smallimg(key,w=500):
    from PIL import Image as PI
    path=ROOT/'images'/key
    im=PI.open(path);x,y=im.size
    return Image(str(path),width=w,height=w*y/x)
def table(headers,rows,widths=None):
    allrows=[[para(str(x),'cellbold') for x in headers]]+[[para(str(x),'cell') for x in row] for row in rows]
    t=Table(allrows,colWidths=widths or [content_w/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,TEAL),
                            ('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d7dfe4')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    return t

def bullet(s):return para('• '+s,'bullet')

def pg(canvas,doc):
 canvas.saveState()
 canvas.setFillColor(NAVY);canvas.rect(0,PAGE_H-14,PAGE_W,14,stroke=0,fill=1)
 canvas.setFont('DejaVu',8);canvas.setFillColor(GRAY)
 canvas.drawString(40,25,'CRUISER III  /  FRICTION RETROFIT  /  RESEARCH ONLY')
 canvas.drawRightString(PAGE_W-40,25,f'V0.4  |  {doc.page}')
 canvas.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=36,bottomMargin=43,title='Cruiser III friction retrofit: engineering feasibility V0.4',author='Research prototype CAD and computation')
story=[]
# PAGE 1
story += [Spacer(1,18),para('Cruiser III<br/>Friction-drive retrofit','title'),
  para('Component-level CAD  |  propulsion analysis  |  finite-element stress study  |  November 20, 2026','sub'),
  smallimg('hero_rear.png',content_w),Spacer(1,10),
  para('STATUS: UNVERIFIED PROTOTYPE — NOT CLEARED FOR OCCUPIED USE','em'),
  para('Two 50-mm friction rollers, independent 24V geared motors, manual roller disengagement and under-seat power electronics. The CAD is editable and includes detailed hardware, but the original wheelchair is reconstructed from photographs, not physically measured.'),
  table(['Nominal target','Preliminary result','Major unresolved issue'],[
    ['3 km/h, 120 kg loaded','Drive torque appears sufficient on assumed dry traction','Unknown real tire friction'],
    ['5% incline','Calculated 1.48 N·m motor output per side while accelerating','Motor thermal/current duty unverified'],
    ['0.5 m/s² downhill stop','Fails illustrative low-adhesion case','No fail-safe power-off braking']],[115,183,content_w-298]),PageBreak()]
# PAGE 2
story += [para('1 / Detailed mechanical architecture','h'),
  para('A parametric 456-solid STEP assembly includes the 145-solid reference wheelchair plus 311 retrofit and detail solids. The parts are named and reusable, rather than baked into a rendering.'),
  smallimg('module_detail.png',content_w),Spacer(1,6),
  table(['Part','Modeled geometry','Confidence'],[
    ['Motor + gearbox','42 mm body; 43.5 mm gearbox; 8 x 22 mm D-shaft','Manufacturer family dimensions; mount pattern estimated'],
    ['Two bearings / module','6000-2RS, each 10 x 26 x 8 mm','Standard boundary dimensions'],
    ['Friction roller','50 mm OD, 34 mm width and aluminum core','Custom design — untested tread/adhesion'],
    ['Frame + mounts','20 x 25 x 2 mm hollow tubes, split clamps','Tube stock nominal; attachment positions unmeasured'],
    ['Battery + controller','Detailed enclosures, lids and cable outlets','Packaging placeholder — no confirmed battery']],[112,170,content_w-282]),
  para('The engaged and 15-mm-released assemblies are exported separately. The release cam and preload spring are visual mechanisms only: kinematics and spring data are not validated.','tiny'),PageBreak()]
# PAGE 3
story += [para('2 / Motor sizing and roller adhesion','h'),
   para('At m = 120 kg, grade = 5%, rolling resistance coefficient = 0.020 and a = 0.30 m/s², the uphill force is 118.4 N. Two 25-mm-radius rollers therefore need 1.48 N·m each. Speed 3 km/h requires 318 RPM per roller.'),
   table(['Motor/force metric','Value'],[
    ['NFP 42GP-775-EN, 13:1 ratio','Rated 2.94 N·m at 300 RPM; 630 RPM no load'],
    ['Motor model estimate at 318 RPM','2.78 N·m per side; approximate linear interpolation'],
    ['Dry assumed roller coefficient μ = 0.60','168 N total available at 140 N normal preload / side'],
    ['Wet assumed coefficient μ = 0.15','42 N total available: fails 118 N hill acceleration'],
    ['Minimum μ for acceleration at that preload','0.423 (not a tire test result)']],[225,content_w-225]),
   Spacer(1,10),smallimg('adhesion_envelope_v04.png',content_w),
   para('Friction coefficient assumptions are intentionally illustrative. Data for pneumatic tire anti-rollback mechanisms do not establish friction on the Cruiser III solid tires. The roller and tire must be tested.','tiny'),PageBreak()]
# PAGE 4
story += [para('3 / Stopping and power-loss behavior','h'),
   para('For a powered downhill stop on a 5% slope, a 0.50 m/s² target deceleration demands approximately 95.3 N of total roller braking force. This exceeds the illustrative wet-contact limit of 42 N.'),
   smallimg('motion_cases_v04.png',content_w),Spacer(1,12),
   table(['7-second scenario','Final speed','Distance'],[
    ['5% downhill, dry assumed μ=0.60, stop commanded','0 km/h','0.79 m'],
    ['5% downhill, wet assumed μ=0.15, stop commanded','1.60 km/h','4.47 m'],
    ['5% downhill, complete electrical drive/brake failure','10.42 km/h','13.06 m']],[282,93,content_w-375]),
   Spacer(1,10),para('CRITICAL FAILURE: the motor-only architecture cannot ensure stopping when power or roller adhesion is lost. The Cruiser III built-in wheel locks are parking devices, not running brakes.','em'),PageBreak()]
# PAGE 5
story += [para('4 / Mechanical stress assessment','h'),
   para('A 140 N roller normal force plus 59.2 N tangential load creates approximately 152 N resultant per module. For screening, a 2× multiplier is applied, then shared across two effective support members per side.'),
   smallimg('tube_3d_fea_v04.png',content_w),Spacer(1,10),
   table(['3D tube FEA, isolated support','Result'],[
    ['20 x 25 x 2 mm hollow aluminum, 205 mm span','480 hexahedral elements, 1,000 nodes'],
    ['Distributed tip load, clamped root','152 N per effective member'],
    ['3D finite-element tip deflection','0.646 mm'],
    ['Peak sampled element-center von Mises','27.1 MPa'],
    ['Analytical beam check','0.666 mm; 32.8 MPa nominal bending'],
    ['Steel roller shaft, 10 mm diameter, 2× shock','75.9 MPa nominal bending stress']],[285,content_w-285]),
   para('This is a true 3D linear elastic solid-element solve of ONE member—not a full wheelchair frame simulation. The modeled member has no bolt holes, realistic clamp joints or cyclic-fatigue conditions. Passing this member check cannot establish safe mounting.','tiny'),PageBreak()]
# PAGE 6
story += [para('5 / Geometric verification and limits','h'),
   table(['Verification performed','Result'],[
    ['Full assembly STEP reimport','456 valid B-rep solids'],
    ['Analytical roller / rear tire geometry','Both rollers tangent at idealized zero gap'],
    ['15 mm release pose','Motor/roller module translates; frame clamps remain fixed'],
    ['Width envelope','Approximate reference chair remains widest (657 mm nominal)'],
    ['Selected part / base collision test','Only intentional joystick-on-armrest penetration remains'],
    ['Unit test suite','17 / 17 passing']],[290,content_w-290]),
   Spacer(1,8),para('Known unknowns','h2'),
   bullet('Chair frame geometry is reverse-engineered from photos; crossbraces, thin-wall tubing, bearings and axle settings require real measurements.'),
   bullet('The motor housing is dimensioned at family level; encoder shape and mounting bolt-circle are still assumptions.'),
   bullet('The under-seat battery/controller are unselected envelopes; no compliant powertrain electronics or wiring schematic is finalized.'),
   bullet('No full-frame nonlinear FEA, fatigue, wheel-to-ground traction, real ramp stopping, motor thermal or occupant tests have been performed.'),
   Spacer(1,6),para('Required next experimental gates','h2'),
   bullet('Measure a real Cruiser III; fit-check clamps, folds and wheel runout.'),
   bullet('Bench-verify traction on clean/wet/worn solid tires and failure braking with unoccupied ballast.'),
   bullet('Engineer spring/cam retention, clamp crush strength and complete power-failure stopping.'),
   bullet('Acquire real motor and battery drawings/data, then perform thermal, fatigue, electrical and braking test protocols.'),PageBreak()]
# PAGE7
story += [para('6 / Sources and standards','h'),
  para('Dimensions and specifications in this report come from manufacturer pages and acknowledged assumptions. None of the simulation results constitutes a certification claim.'),
  bullet('Drive Medical Cruiser III 18-inch official product page — shop.drivemedical.com/ca, model K318DDA-SF.'),
  bullet('NFP Motor NFP-42GP-775-EN — published 24V / 13:1 motor dimensions and motor rating table (nfpmotor.com).'),
  bullet('6000-series standard sealed ball bearing dimensions — 6000-2RS, 10 x 26 x 8 mm.'),
  bullet('Anti-rollback roller research: Applied Sciences 2025, 15(23), 12768; pneumatic tire tests are not transferable directly to solid Cruiser III tires.'),
  bullet('ISO 7176-1:2014: wheelchair static stability test methods.'),
  bullet('ISO 7176-3:2012: wheelchairs, effectiveness of brakes.'),
  bullet('ISO 7176-14:2022 + Amd.1:2025: power and control systems for powered wheelchairs.'),
  para('Important files in package','h2'),
  table(['File','Purpose'],[
    ['cad/CruiserIII_Retrofit_Detailed_V04.step','Full editable, grouped B-rep assembly'],
    ['cad/Friction_Drive_Modules_Detailed_V04.step','Add-on assembly only'],
    ['cad/Friction_Drive_Modules_Released_V04.step','15-mm disengaged configuration'],
    ['cad/build_high_fidelity.py','Parametric CAD source code'],
    ['analysis/engineering_v04.py','Load, motor, adhesion, braking and battery models'],
    ['analysis/tube_3d_fea.py','Real 3D elastic FE solver for hollow tube'],
    ['docs/ENGINEERING_REVIEW.md','Source details, calculations and test gates']],[292,content_w-292]),
   Spacer(1,12),para('Verdict: useful unoccupied design-research prototype, but occupant operation is NOT APPROVED. Dry-case torque is plausible; adhesion, braking failure behavior and frame clamp integrity are unresolved.','em')]
doc.build(story,onFirstPage=pg,onLaterPages=pg)
print(OUT,OUT.stat().st_size)
