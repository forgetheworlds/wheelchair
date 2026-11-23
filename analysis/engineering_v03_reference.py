"""First-principles parameter study; NOT measurements, CFD, physical or certification tests."""
import json, math
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
OUT=HERE.parent
@dataclass
class Assumptions:
    total_mass_kg: float=120.0
    g: float=9.81
    wheelchair_wheel_d_m: float=0.6096
    roller_d_m: float=0.050
    target_kmh: float=3.0
    rolling_resistance: float=0.020
    grade: float=0.05
    accel_mps2: float=0.30
    brake_decel_mps2: float=0.50
    mu_dry: float=0.60        # HYPOTHETICAL, DO NOT USE AS TESTED TIRE DATA
    mu_wet: float=0.15        # HYPOTHETICAL, DO NOT USE AS TESTED TIRE DATA
    preload_N_per_side: float=140.0  # illustrative; NOT proven compatible with wheelchair tire
    motor_continuous_Nm: float=2.0  # proposed requirement, not sourced motor rating
    motor_peak_Nm: float=3.5
    motor_max_rpm: float=350.0
    drivetrain_efficiency: float=0.65
    battery_nominal_V: float=25.6
    battery_nominal_Ah: float=6.0
    battery_usable_fraction: float=0.7
    fixed_electronics_W: float=8.0
    # surrogate bracket geometry. Two straight rectangular steel cantilevers carry load equally.
    bracket_length_mm: float=170.0
    bracket_width_mm: float=30.0
    bracket_weak_thickness_mm: float=8.0
    bracket_E_MPa: float=200000.0
    bracket_yield_MPa: float=250.0  # illustrative low-carbon steel
    shock_multiplier: float=2.0

S=Assumptions()
def force_uphill(m, grade, crr, a=0.0):
    return m*(S.g*(grade+crr)+a)
def force_downhill_brake(m, grade, crr, decel):
    return m*(S.g*(grade-crr)+decel)
def available_force(mu, preload, torque, roller_r):
    return min(2*mu*preload, 2*torque/roller_r)
def feed_speed(roller_d, kmh):
    return (kmh/3.6)/(math.pi*roller_d)*60

def solve_beam_fea(length_mm, width_mm, thickness_mm, load_N, E_MPa=200000., n_elements=20):
    """Euler-Bernoulli 2-DOF/node cantilever. Weak-axis idealization; linear isotropic, no fastener/slip/bearing bending."""
    I=width_mm*thickness_mm**3/12.0
    le=length_mm/n_elements
    ke=E_MPa*I/le**3*np.array([[12,6*le,-12,6*le], [6*le,4*le**2,-6*le,2*le**2],
                                      [-12,-6*le,12,-6*le], [6*le,2*le**2,-6*le,4*le**2]],float)
    n=2*(n_elements+1); K=np.zeros((n,n)); f=np.zeros(n); f[-2]=load_N
    for i in range(n_elements):
        ind=[2*i,2*i+1,2*i+2,2*i+3]; K[np.ix_(ind,ind)]+=ke
    u=np.zeros(n); u[2:]=np.linalg.solve(K[2:,2:],f[2:])
    M=load_N*length_mm
    sigma=M*(thickness_mm/2)/I
    delta_analytic=load_N*length_mm**3/(3*E_MPa*I)
    return dict(tip_displacement_mm=float(u[-2]),analytic_displacement_mm=float(delta_analytic),
                max_bending_MPa=float(sigma), bending_section_I_mm4=float(I),
                factor_to_yield=float(S.bracket_yield_MPa/sigma))

def simulate(grade, mu, power=True, speed0=0., target=3/3.6, t_end=8, step=.01):
    """1D translational idealized traction-saturated dynamics, not true multi-body dynamics.
    grade: + uphill. - downhill. Negative motor force on downhills assumes working active driver.
    """
    v=float(speed0); x=0.; t_list=[]; v_list=[]; x_list=[]; slippage=0.
    for t in np.arange(0,t_end+step/2,step):
        if power:
            a_req=np.clip((target-v)*1.5,-S.brake_decel_mps2,S.accel_mps2)
            f_cmd=S.total_mass_kg*(a_req+S.g*grade+S.g*S.rolling_resistance*np.sign(v if abs(v)>.005 else (target-v or 1)))
            f_cap=available_force(mu,S.preload_N_per_side,S.motor_peak_Nm,S.roller_d_m/2)
            f_drive=float(np.clip(f_cmd,-f_cap,f_cap))
            if abs(f_drive-f_cmd)>.0001: slippage+=step
        else:
            f_drive=0.
        resistance=S.total_mass_kg*S.g*S.rolling_resistance*np.sign(v if abs(v)>.005 else (f_drive-S.total_mass_kg*S.g*grade))
        a=(f_drive-resistance-S.total_mass_kg*S.g*grade)/S.total_mass_kg
        v+=a*step; x+=v*step
        t_list.append(t);v_list.append(v);x_list.append(x)
    return dict(t=np.array(t_list),v=np.array(v_list),x=np.array(x_list),last_speed_mps=float(v),distance_m=float(x),traction_saturated_seconds=round(slippage,2))

def run():
    speed= S.target_kmh/3.6; r=S.roller_d_m/2
    f_up=force_uphill(S.total_mass_kg,S.grade,S.rolling_resistance)
    f_up_accel=force_uphill(S.total_mass_kg,S.grade,S.rolling_resistance,S.accel_mps2)
    f_down=force_downhill_brake(S.total_mass_kg,S.grade,S.rolling_resistance,S.brake_decel_mps2)
    f_gear=f_up/2*r
    cases={
        'level_dry':(0, S.mu_dry, True,0,speed),
        'uphill_5pct_dry':(S.grade,S.mu_dry,True,0,speed),
        'uphill_5pct_wet':(S.grade,S.mu_wet,True,0,speed),
        'downhill_5pct_dry_stop':(-S.grade,S.mu_dry,True,speed,0),
        'downhill_5pct_wet_stop':(-S.grade,S.mu_wet,True,speed,0),
        'downhill_5pct_power_loss':(-S.grade,S.mu_dry,False,speed,0),
    }
    traces={k:simulate(*v,t_end=7) for k,v in cases.items()}
    res={
        'assumptions':asdict(S),
        'kinematics':{'roller_rpm_at_target':feed_speed(S.roller_d_m,S.target_kmh),'rear_wheel_rpm_at_target':feed_speed(S.wheelchair_wheel_d_m,S.target_kmh)},
        'propulsion':{'uphill_5pct_force_N':f_up,'uphill_with_acceleration_force_N':f_up_accel,'steady_roller_torque_Nm_per_side':f_gear,'power_W_at_wheels':f_up*speed,'electrical_power_W_est':f_up*speed/S.drivetrain_efficiency+S.fixed_electronics_W,'theoretical_uphill_range_km':(S.battery_nominal_V*S.battery_nominal_Ah*S.battery_usable_fraction)/(f_up*speed/S.drivetrain_efficiency+S.fixed_electronics_W)*S.target_kmh/1000*1000},
        'braking':{'downhill_force_for_half_mps2_decel_N':f_down,'dry_normal_preload_min_N_side':f_down/2/S.mu_dry,'wet_normal_preload_min_N_side':f_down/2/S.mu_wet,'available_dry_total_force_N':2*S.mu_dry*S.preload_N_per_side,'available_wet_total_force_N':2*S.mu_wet*S.preload_N_per_side,'power_loss_downhill_net_accel_mps2':S.g*(S.grade-S.rolling_resistance)},
        'bracket':{}, 'scenarios':{}
    }
    # Wheel reaction from grade + accel; applied to two arms, with shock factor.
    tangential_per_side=f_up_accel/2
    reaction_side=math.hypot(S.preload_N_per_side,tangential_per_side)
    test_F=S.shock_multiplier*reaction_side/2 # shared between TWO surrogate plates
    fea=solve_beam_fea(S.bracket_length_mm,S.bracket_width_mm,S.bracket_weak_thickness_mm,test_F,S.bracket_E_MPa)
    res['bracket']={**fea,'roller_reaction_N_per_side':reaction_side,'design_load_N_per_side':S.shock_multiplier*reaction_side,
                     'assumed_force_per_plate_N':test_F,'support_model':'2 identical fixed-free steel weak-axis beams; end point load; DOES NOT MODEL clamping, eccentric torsion, fatigue, frame, tires or attachment' }
    for name,trace in traces.items():
        res['scenarios'][name]={k:round(float(trace[k]),4) for k in ('last_speed_mps','distance_m','traction_saturated_seconds')}
    # parameter sweep - no probability claims
    res['traction_sensitivity']=[]
    for grade in (0,0.03,0.05,0.08):
        for mu in (.1,.15,.25,.4,.6):
            req=force_uphill(S.total_mass_kg,grade,S.rolling_resistance,S.accel_mps2)
            avail=available_force(mu,S.preload_N_per_side,S.motor_continuous_Nm,r)
            res['traction_sensitivity'].append(dict(grade=grade,mu=mu,demand_N=round(req,2),available_N=round(avail,2),margin=round(avail/req,3),meets_selected_load=bool(avail>=req)))
    (OUT/'analysis'/'results.json').write_text(json.dumps(res,indent=2))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig,ax=plt.subplots(figsize=(9,5.2))
    for name in ['level_dry','uphill_5pct_dry','uphill_5pct_wet']:
        tr=traces[name];ax.plot(tr['t'],tr['v']*3.6,label=name.replace('_',' '),lw=2)
    ax.axhline(3,color='black',lw=0.8,linestyle='--',label='3 km/h target')
    ax.set(xlabel='Time (s)',ylabel='Forward speed (km/h)',title='Idealized 1D motion: start from rest (illustrative friction)');ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(OUT/'images'/'drive_simulation.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5.2))
    for name in ['downhill_5pct_dry_stop','downhill_5pct_wet_stop','downhill_5pct_power_loss']:
        tr=traces[name];ax.plot(tr['t'],tr['v']*3.6,label=name.replace('_',' '),lw=2)
    ax.axhline(0,color='black',lw=0.8)
    ax.set(xlabel='Time (s)',ylabel='Signed downhill speed (km/h)',title='Idealized 1D braking: command STOP on 5% descent');ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(OUT/'images'/'braking_simulation.png',dpi=150);plt.close(fig)
    grades=np.linspace(0,.10,101);mus=[.15,.3,.6]
    fig,ax=plt.subplots(figsize=(9,5.2))
    for mu in mus:
        req=force_uphill(S.total_mass_kg,grades,S.rolling_resistance,S.accel_mps2)
        ax.plot(grades*100,available_force(mu,S.preload_N_per_side,S.motor_continuous_Nm,r)/req,label=f'Assumed mu={mu:g}',lw=2)
    ax.axhline(1,color='black',ls='--',lw=1)
    ax.set(xlabel='Uphill grade (%)',ylabel='Available / required tangential force',title='Traction sensitivity; margin below 1 means saturation');ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(OUT/'images'/'traction_margin.png',dpi=150);plt.close(fig)
    thickness=np.arange(4,13,.5)
    stress=[solve_beam_fea(S.bracket_length_mm,S.bracket_width_mm,t,test_F)['max_bending_MPa'] for t in thickness]
    delta=[solve_beam_fea(S.bracket_length_mm,S.bracket_width_mm,t,test_F)['tip_displacement_mm'] for t in thickness]
    fig,ax=plt.subplots(figsize=(9,5.2));ax.plot(thickness,stress,label='Bending stress (MPa)');ax.axhline(S.bracket_yield_MPa,color='black',ls='--',label='Assumed steel yield 250 MPa');
    ax.set(xlabel='Metal plate thickness (mm)',ylabel='Peak idealized bending stress (MPa)',title='Two-beam surrogate: sensitivity to bracket thickness');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(OUT/'images'/'beam_sensitivity.png',dpi=150);plt.close(fig)
    print(json.dumps({'propulsion':res['propulsion'],'braking':res['braking'],'bracket':res['bracket'],'scenarios':res['scenarios']},indent=2))
    return res

if __name__=='__main__': run()
