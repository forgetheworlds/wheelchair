"""8-node hex solid FEA, 20x25x2 hollow rectangular 6061-T6 tube.
Illustrative fixed-root / distributed tip shear test only. NO bolted joint, frame or fatigue.
2x 5%-grade accelerated roller reaction is applied as transverse tip force to one
of two effective braces. Python+SciPy, true 3D linear elasticity, not beam-only FEM.
"""
import numpy as np,json
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# 24 stations along x: 8.54mm elements, y and z include boundaries at 2mm wall positions
L=205; nx=24; xs=np.linspace(0,L,nx+1)
ys=np.array([-10,-8,-5,0,5,8,10.],float)
zs=np.array([-12.5,-10.5,-7,0,7,10.5,12.5],float)
ny=len(ys)-1;nz=len(zs)-1
coords=np.array([[x,y,z] for x in xs for y in ys for z in zs],float)
id_of=lambda i,j,k:i*(ny+1)*(nz+1)+j*(nz+1)+k
# keep cell only if exterior hollow-wall cross section; central interior is omitted
els=[]
for i in range(nx):
 for j in range(ny):
  for k in range(nz):
   if 1<=j<=ny-2 and 1<=k<=nz-2:continue
   els.append([id_of(i,j,k),id_of(i+1,j,k),id_of(i+1,j+1,k),id_of(i,j+1,k),
               id_of(i,j,k+1),id_of(i+1,j,k+1),id_of(i+1,j+1,k+1),id_of(i,j+1,k+1)])
# remove unconnected interior nodes: needed to avoid singular K
used=sorted(set(n for el in els for n in el));remap={old:i for i,old in enumerate(used)}
coords=coords[used];els=np.array([[remap[n] for n in el] for el in els],dtype=int)
E=69000.;nu=.33
lam=E*nu/((1+nu)*(1-2*nu));G=E/(2*(1+nu))
C=np.array([[lam+2*G,lam,lam,0,0,0],[lam,lam+2*G,lam,0,0,0],[lam,lam,lam+2*G,0,0,0],
 [0,0,0,G,0,0],[0,0,0,0,G,0],[0,0,0,0,0,G]])
signs=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],
                [-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]])
GP=[-1/(3**.5),1/(3**.5)]
def element_B(xyz,xi,eta,zeta):
    q=np.array([xi,eta,zeta])
    dref=np.empty((8,3))
    for n,(sx,sy,sz) in enumerate(signs):
        dref[n]=[sx*(1+sy*eta)*(1+sz*zeta)/8,
                  sy*(1+sx*xi)*(1+sz*zeta)/8,
                  sz*(1+sx*xi)*(1+sy*eta)/8]
    jac=dref.T@xyz
    det=np.linalg.det(jac)
    if det<=0:raise RuntimeError('bad element jacobian '+str(det))
    grads=dref@np.linalg.inv(jac)
    B=np.zeros((6,24))
    for a,(dx,dy,dz) in enumerate(grads):
        ii=3*a
        B[0,ii]=dx;B[1,ii+1]=dy;B[2,ii+2]=dz
        B[3,ii+1]=dz;B[3,ii+2]=dy
        B[4,ii]=dz;B[4,ii+2]=dx
        B[5,ii]=dy;B[5,ii+1]=dx
    return B,det
rows=[];cols=[];vals=[]
for ii,el in enumerate(els):
    xyz=coords[el];Kel=np.zeros((24,24))
    for xi in GP:
     for eta in GP:
      for zeta in GP:
       B,det=element_B(xyz,xi,eta,zeta)
       Kel+=B.T@C@B*det
    dofs=np.array([3*n+d for n in el for d in range(3)])
    rows.extend(np.repeat(dofs,24));cols.extend(np.tile(dofs,24));vals.extend(Kel.flatten())
ndof=3*len(coords)
K=coo_matrix((vals,(rows,cols)),shape=(ndof,ndof)).tocsr()
f=np.zeros(ndof)
# full idealized design load on each of TWO braces supporting module, 2x acceleration/normal reaction
F=152.00288419632042
endpoints=np.flatnonzero(np.isclose(coords[:,0],L))
for n in endpoints:f[n*3+1]+=F/len(endpoints)
fixed_nodes=np.flatnonzero(np.isclose(coords[:,0],0))
fixed=np.array([3*n+d for n in fixed_nodes for d in range(3)],dtype=int)
mask=np.ones(ndof,dtype=bool);mask[fixed]=False;free=np.flatnonzero(mask)
u=np.zeros(ndof);u[free]=spsolve(K[free][:,free],f[free])

stress=[]
for i,el in enumerate(els):
    xyz=coords[el];ud=u[np.array([3*n+d for n in el for d in range(3)])]
    B,_=element_B(xyz,0,0,0)
    sig=C@(B@ud)
    sx,sy,sz,tyz,txz,txy=sig
    vm=(((sx-sy)**2+(sy-sz)**2+(sz-sx)**2+6*(txy*txy+tyz*tyz+txz*txz))/2)**.5
    stress.append((float(np.mean(xyz[:,0])),float(vm),float(sx)))
ss=np.array(stress)
tip_disp=np.mean(u[3*endpoints+1])
root_stress=max(vm for x,vm,sx in stress if x<L*.10)
max_vm=float(ss[:,1].max())
max_u_mm=float(np.linalg.norm(u.reshape(-1,3),axis=1).max())
# classic closed-form weak-axis: defl=F L^3/(3EI), sigma=M c/I. y-width20, z-height25
I_about_z=(25*20**3-21*16**3)/12
beam_disp=F*L**3/(3*E*I_about_z)
beam_stress=F*L*10/I_about_z
report={'model':'3D linear elastic hexahedral solid FEM, 20x25x2 mm hollow rectangular aluminum tube',
        'mesh_nodes':len(coords),'hex_elements':len(els),'dof':ndof,
        'material_E_MPa':E,'material_poisson':nu,'load_direction':'transverse y',
        'tip_total_load_N':F,'span_mm':L,'root_bc':'all displacement DOF fully fixed x=0',
        'tip_displacement_mm':float(tip_disp),'max_displacement_mm':max_u_mm,
        'max_element_center_von_mises_MPa':max_vm,'root_near_von_mises_MPa':root_stress,
        'beam_closed_form_tip_mm':beam_disp,'beam_closed_form_bending_stress_MPa':beam_stress,
        'assumed_6061T6_yield_MPa':240.,'nominal_yield_margin':240/max_vm,
        'limitations':['No fastening holes or local stress concentrations, joints, clamp slip, tube buckling or fatigue',
                       'Load distributed over full tube tip and fully fixed clamped root idealization',
                       'Wheelchair frame itself not solved; effective two-brace load split assumed',
                       'Material property nominal, actual stock/temper unknown; mesh is coarse']}
(ROOT/'analysis'/'tube_3d_fea_results.json').write_text(json.dumps(report,indent=2))
# trend by position of worst element center VM
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
xx=sorted(set(ss[:,0]))
max_by_x=[np.max(ss[np.isclose(ss[:,0],x),1]) for x in xx]
fig,ax=plt.subplots(figsize=(9,4.5))
ax.plot(xx,max_by_x,lw=2.7,label='3D hex FEM peak cross-section stress')
ax.plot(xx,[F*(L-x)*10/I_about_z for x in xx],lw=1.8,ls='--',label='Euler-Bernoulli nominal bending')
ax.axhline(240,color='black',ls=':',lw=1,label='Assumed nominal yield 240 MPa')
ax.set(xlabel='Position along brace from fixed frame joint (mm)',ylabel='Stress (MPa)',title='3D tube FEM — 152 N transverse end force, representative shock scenario')
ax.grid(alpha=.18);ax.legend(fontsize=9);fig.tight_layout();fig.savefig(ROOT/'images'/'tube_3d_fea_v04.png',dpi=160)
print(json.dumps(report,indent=2))
