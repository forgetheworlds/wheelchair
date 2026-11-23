"""V04 physically interpretable but still PARAMETRIC engineering load study.
Not physical tests, not full-chair FEA. Data-derived motor specs from NFP 42GP-775-EN
24V 13:1; rolling resistance, tire-roller mu, preload and structure are assumptions.
Units SI unless specified.
"""
from pathlib import Path
from dataclasses import dataclass,asdict
import math,json,numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parents[1]
@dataclass
class Params:
    mass_kg:float=120.0
    g:float=9.81
    tire_d_m:float=.6096
    roller_d_m:float=.050
    speed_mps:float=3/3.6
    grade:float=.05
    rolling_resistance:float=.020    # UNMEASURED
    acceleration_mps2:float=.30
    stopping_decel_mps2:float=.50
    preload_N_per_side:float=140.0 # UNMEASURED
    mu_dry:float=.60              # HYPOTHETICAL, NOT TESTED ON SOLID TIRES
    mu_wet:float=.15              # HYPOTHETICAL, NOT TESTED
    motor_rated_Nm:float=2.94    # 30 kgf.cm = 2.941995 Nm (published)
    motor_rated_rpm:float=300    # published, rated load
    motor_no_load_rpm:float=630 # published at 24V, ±15%
    motor_peak_current_A:float=24.5 # published stall; NOT continuous
    motor_rated_current_upper_A:float=13.0 # upper-bound, NOT calibrated draw
    battery_V:float=25.6
    battery_Ah:float=6.0
    battery_usable_fraction:float=.7
    electronics_W:float=8.0
    drivetrain_efficiency_low:float=.35 # illustrative total losses
    drivetrain_efficiency_high:float=.70
    spring_stiffness_N_per_mm:float=15.0 # proposed nominal, no spring selected
    tire_runout_mm:float=2.0
    axle_d_mm:float=10.0
    shaft_bearing_inner_y_mm:float=253.0
    shaft_bearing_outer_y_mm:float=273.0
    tire_center_y_mm:float=297.5
    beam_external_y_mm:float=20
    beam_external_z_mm:float=25
    beam_wall_mm:float=2
    beam_span_mm:float=205
    aluminum_E_MPa:float=69000
    aluminum_yield_MPa:float=240 # representative nominal 6061-T6, VERIFY GRADE
    steel_shaft_yield_MPa:float=250 # illustrative conservative low-carbon value
    bracket_shock_multiplier:float=2.0
    assumed_effective_braces_per_side:int=2 # conservatively ignore other two as load-bearing
P=Params()

def wheel_rpm(speed=P.speed_mps,diam=P.roller_d_m):return speed/(math.pi*diam)*60

def required_force(m=P.mass_kg,grade=P.grade,crr=P.rolling_resistance,accel=0):
    return m*(P.g*(grade+crr)+accel)

def braking_force(m=P.mass_kg,down_grade=P.grade,crr=P.rolling_resistance,decel=P.stopping_decel_mps2):
    return m*(decel+P.g*(down_grade-crr))

def motor_limit_Nm(rpm):
    # conservative rated torque clamp below rated RPM, linear derate toward no load
    return max(0, P.motor_rated_Nm*min(1.,(P.motor_no_load_rpm-abs(rpm))/(P.motor_no_load_rpm-P.motor_rated_rpm)))

def normal_contact(mu,preload=P.preload_N_per_side,rot_speed=P.speed_mps):
    # two rollers; both independently satisfy min(motor torque capacity, friction limit)
    motor_force=motor_limit_Nm(wheel_rpm(rot_speed))/ (P.roller_d_m/2)
    return 2*min(mu*preload,motor_force)

def tubular_I_and_area():
    b=P.beam_external_y_mm;h=P.beam_external_z_mm;t=P.beam_wall_mm
    return ((b*h**3-(b-2*t)*(h-2*t)**3)/12,
            (h*b**3-(h-2*t)*(b-2*t)**3)/12,
            b*h-(b-2*t)*(h-2*t))

def beam_fem(I,load,span,element_count=24):
    n=element_count;le=span/n;E=P.aluminum_E_MPa
    K=np.zeros((2*(n+1),2*(n+1)));f=np.zeros(K.shape[0]);f[-2]=load
    ek=(E*I/le**3)*np.array([[12,6*le,-12,6*le],[6*le,4*le**2,-6*le,2*le**2],[-12,-6*le,12,-6*le],[6*le,2*le**2,-6*le,4*le**2]])
    for i in range(n):
        ix=[2*i,2*i+1,2*i+2,2*i+3]
        K[np.ix_(ix,ix)]+=ek
    x=np.linalg.solve(K[2:,2:],f[2:]);return float(x[-2])

def simulate(mode='uphill',mu=.6,t=7,dt=.005):
    """1D commanded acceleration & finite-speed motor torque + roller slip.
    No road bumps, wheel deformation, yaw, tilting or true battery circuit.
    """
    downhill=mode.startswith('downhill')
    power='failure' not in mode
    target=0 if ('stop' in mode or not power) else P.speed_mps
    v=P.speed_mps if downhill else 0.
    x=0.; traces=[]; saturated=0.; n=int(t/dt)
    for k in range(n+1):
        now=k*dt
        # vehicle forward coordinate positive downhill or uphill; gravity sign changes
        gravitational=P.mass_kg*P.g*(P.grade if downhill else -P.grade)
        fric=P.mass_kg*P.g*P.rolling_resistance*(1 if v>1.e-4 else (1 if downhill else -1))
        if power:
            a_des=max(-P.stopping_decel_mps2,min(P.acceleration_mps2,(target-v)*1.6))
            motor_request=P.mass_kg*a_des-gravitational+fric
            motor_capacity=normal_contact(mu,rot_speed=max(abs(v),0))
            motor_F=max(-motor_capacity,min(motor_capacity,motor_request))
            if abs(motor_request)>motor_capacity:saturated+=dt
        else:motor_F=0
        acc=(gravitational-fric+motor_F)/P.mass_kg
        if abs(v)<.005 and target==0 and power and abs(motor_request)<=motor_capacity:
            v=0;acc=0
        else:
            v=max(0.,v+acc*dt)
        x+=v*dt
        if k%max(int(.1/dt),1)==0:traces.append((now,v,x,motor_F))
    return dict(mode=mode,mu=mu,final_speed_mps=float(v),distance_m=float(x),traction_limit_seconds=float(saturated),time_series=traces)

def run():
    f_up=required_force(accel=0); f_acc=required_force(accel=P.acceleration_mps2)
    f_brk=braking_force(); r=P.roller_d_m/2;rpm=wheel_rpm()
    result={'assumptions':asdict(P),'motor':{'target_roller_rpm':rpm,
             'target_wheel_rpm':wheel_rpm(diam=P.tire_d_m),
             'rated_torque_Nm':P.motor_rated_Nm,
             'continuous_torque_at_target_Nm_linear_approx':motor_limit_Nm(rpm),
             'estimated_required_torque_5pct_cruise_Nm_per_side':f_up*r/2,
             'estimated_required_torque_5pct_accel_Nm_per_side':f_acc*r/2,
             'torque_margin_5pct_accel':motor_limit_Nm(rpm)/(f_acc*r/2),
             'note':'NFP data have no published duty-cycle/temperature curve. 13A is upper bound, 150W max listing vs 24V*13A = 312W, so cannot infer precise efficiency/heat.'},
            'traction':{},'braking':{},'bracket':{},'shaft':{},'battery':{},'scenarios':{}}
    for k,mu in [('dry_assumed',P.mu_dry),('wet_assumed',P.mu_wet)]:
        result['traction'][k]={'mu':mu,'Fmax_N_at_speed':normal_contact(mu),'required_F_5pct_cruise_N':f_up,'required_F_5pct_accel_N':f_acc,
                         'accel_margin':normal_contact(mu)/f_acc,
                         'required_preload_N_per_side_for_accel':f_acc/(2*mu),
                         'meets_5pct_accel':normal_contact(mu)>=f_acc}
    result['traction']['spring']={'nominal_N':P.preload_N_per_side,
                    'nominal_compression_mm_at_15N_per_mm':P.preload_N_per_side/P.spring_stiffness_N_per_mm,
                    'runout_N_range':[P.preload_N_per_side-P.spring_stiffness_N_per_mm*P.tire_runout_mm,P.preload_N_per_side+P.spring_stiffness_N_per_mm*P.tire_runout_mm],
                    'requires_test_of_tire_deformation':True}
    result['braking']={'required_N_for_0_5mps2_downhill':f_brk,
           'torque_Nm_per_side':f_brk*r/2,
           'normal_N_required_dry':f_brk/(2*P.mu_dry),
           'normal_N_required_wet':f_brk/(2*P.mu_wet),
           'loss_of_power_accel_downhill_mps2':P.g*(P.grade-P.rolling_resistance),
           'power_loss_speed_after_3s_kmh':(P.speed_mps+P.g*(P.grade-P.rolling_resistance)*3)*3.6,
           'power_loss_distance_after_7s_m':P.speed_mps*7+.5*P.g*(P.grade-P.rolling_resistance)*7**2,
           'critical_limit':'No independent fail-safe wheel braking; user parking locks cannot safely stop a moving chair.'}
    side_tangential=f_acc/2
    side_reaction=math.hypot(P.preload_N_per_side,side_tangential)
    factored_side=side_reaction*P.bracket_shock_multiplier
    per_member=factored_side/P.assumed_effective_braces_per_side
    Iy,Iz,area=tubular_I_and_area();weak=min(Iy,Iz);c=max(P.beam_external_z_mm,P.beam_external_y_mm)/2
    sigma=per_member*P.beam_span_mm*c/weak
    delta=beam_fem(weak,per_member,P.beam_span_mm)
    closed_form=per_member*P.beam_span_mm**3/(3*P.aluminum_E_MPa*weak)
    result['bracket']={'profile':'aluminum rectangular hollow 20x25x2 mm, UNKNOWN actual alloy/temper',
         'idealized_length_mm':P.beam_span_mm,'reaction_per_side_N':side_reaction,
         'two_x_shock_reaction_per_side_N':factored_side,
         'load_per_effective_brace_N':per_member,
         'section_I_weak_mm4':weak,'cross_section_mm2':area,
         'linear_beam_fem_tip_deflection_mm':delta,'closed_form_tip_mm':closed_form,
         'idealized_max_stress_MPa':sigma,
         'nominal_FOS_to_yield':P.aluminum_yield_MPa/sigma,
         'rough_8_braces_total_mass_kg':area*(P.beam_span_mm*8)*2.7e-6,
         'critical_limitations':'Fixed-end beam surrogate ignores hollow-tube bolt-hole stress concentrations, joint slip, fatigue, wheelchair tube wall thickness, twisting and local buckling.'}
    reaction=side_reaction
    L=P.shaft_bearing_outer_y_mm-P.shaft_bearing_inner_y_mm
    over=P.tire_center_y_mm-P.shaft_bearing_outer_y_mm
    outer_N=reaction*(1+over/L);inner_N=reaction*(over/L)
    M=reaction*over
    stress=32*M/(math.pi*P.axle_d_mm**3)
    result['shaft']={'model':'solid 10mm round steel, two 6000-2RS bearings 253/273mm, roller center 297.5mm',
                     'shaft_overhang_mm':over,'bearing_spacing_mm':L,
                     'radial_load_N_at_5pct_accel':reaction,
                     'outer_bearing_reaction_N':outer_N,
                     'inner_bearing_reaction_N_opposite_direction':inner_N,
                     'max_shaft_bending_Nmm':M,
                     'max_nominal_bending_stress_MPa':stress,
                     'two_x_shock_bending_MPa':stress*P.bracket_shock_multiplier,
                     'nominal_FOS_to_yield_under_2x_shock':P.steel_shaft_yield_MPa/(stress*P.bracket_shock_multiplier),
                     'limitations':'Bearing L10 life, shaft keyway, coupling misalignment, torsion and press-fit details not assessed.'}
    wheel_mech=f_up*P.speed_mps
    results=[]
    for eta in (P.drivetrain_efficiency_low,.45,P.drivetrain_efficiency_high):
        elec=wheel_mech/eta+P.electronics_W
        Wh=P.battery_V*P.battery_Ah*P.battery_usable_fraction
        results.append({'assumed_total_efficiency':eta,'power_W':elec,'average_current_A':elec/P.battery_V,
                        'ideal_5pct_grade_range_km':Wh/elec*(P.speed_mps*3.6),'runtime_minutes':Wh/elec*60})
    result['battery']={'nominal_Wh':P.battery_V*P.battery_Ah,'assumed_usable_Wh':Wh,
             'five_percent_grade_estimates':results,
             'driver_and_bms':'24.5A listed stall PER MOTOR; two motors could demand >40A in a startup fault. Current limit, fuse, controller voltage and BMS coordination require real testing.'}
    for mode,mu in [('uphill_dry',P.mu_dry),('uphill_wet',P.mu_wet),('downhill_dry_stop',P.mu_dry),('downhill_wet_stop',P.mu_wet),('downhill_failure',P.mu_dry)]:
        res=simulate(mode,mu)
        result['scenarios'][mode]={k:v for k,v in res.items() if k!='time_series'}
    # stress/traction margins plots
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
    fig,ax=plt.subplots(figsize=(8.5,4.8))
    for mode,mu in [('uphill_dry',.6),('uphill_wet',.15),('downhill_dry_stop',.6),('downhill_wet_stop',.15),('downhill_failure',.6)]:
        data=simulate(mode,mu)['time_series']
        ax.plot([v[0] for v in data],[v[1]*3.6 for v in data],lw=2,label=mode.replace('_',' '))
    ax.axhline(3,ls='--',c='black',lw=.8)
    ax.set(xlabel='Time (s)',ylabel='Speed (km/h)',title='Idealized 1D motion — assumed roller adhesion')
    ax.grid(alpha=.2);ax.legend(fontsize=8,ncol=2);fig.tight_layout();fig.savefig(HERE/'images'/'motion_cases_v04.png',dpi=165);plt.close(fig)
    grades=np.linspace(0,.1,100)
    fig,ax=plt.subplots(figsize=(8.5,4.8))
    for mu in (.15,.3,.45,.6):
        margins=[normal_contact(mu)/required_force(grade=g,accel=P.acceleration_mps2) for g in grades]
        ax.plot(100*grades,margins,lw=2,label=f'assumed μ={mu}')
    ax.axhline(1,lw=.9,ls='--',c='black')
    ax.set(xlabel='Uphill grade (%)',ylabel='Available roller force / drive requirement',title='Adhesion limits for 120 kg and 0.30 m/s² acceleration')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(HERE/'images'/'adhesion_envelope_v04.png',dpi=165);plt.close(fig)
    lengths=np.linspace(120,235,100)
    fig,ax=plt.subplots(figsize=(8.5,4.8))
    values=[per_member*L*c/weak for L in lengths]
    ax.plot(lengths,values,label='Idealized bending stress',lw=2)
    ax.axhline(P.aluminum_yield_MPa,c='black',ls='--',label='Representative nominal yield')
    ax.set(xlabel='Brace effective span (mm)',ylabel='Stress under 2x reaction load (MPa)',title='20 × 25 × 2 mm hollow aluminum brace surrogate')
    ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(HERE/'images'/'brace_stress_v04.png',dpi=165);plt.close(fig)
    (HERE/'analysis'/'engineering_results_v04.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:result[k] for k in ['motor','traction','braking','bracket','shaft','battery','scenarios']},indent=2))
    return result
if __name__=='__main__':run()
