import sys,math,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'analysis'));sys.path.insert(0,str(ROOT/'cad'))
from engineering_v04 import P,required_force,braking_force,motor_limit_Nm,normal_contact,wheel_rpm,tubular_I_and_area,beam_fem,simulate
import build_high_fidelity as cad

class Physics(unittest.TestCase):
 def test_target_roller_speed(self):self.assertAlmostEqual(wheel_rpm(),318.309886,places=4)
 def test_motor_at_rated(self):self.assertAlmostEqual(motor_limit_Nm(300),2.94)
 def test_motor_at_no_load(self):self.assertAlmostEqual(motor_limit_Nm(630),0.)
 def test_required_uphill_accel(self):self.assertAlmostEqual(required_force(accel=.3),118.404,places=3)
 def test_braking_force(self):self.assertAlmostEqual(braking_force(),95.316,places=3)
 def test_wet_failure(self):self.assertLess(normal_contact(.15),braking_force())
 def test_dry_success(self):self.assertGreater(normal_contact(.6),braking_force())
 def test_beam_FEM_linear_analytic(self):
  Iy,Iz,area=tubular_I_and_area();I=min(Iy,Iz);F=152.002884;L=205
  f=beam_fem(I,F,L);closed=F*L**3/(3*P.aluminum_E_MPa*I)
  self.assertAlmostEqual(f,closed,places=6)
 def test_power_failure_accelerates(self):
  r=simulate('downhill_failure',mu=.6)
  self.assertGreater(r['final_speed_mps'],2.8)
 def test_powered_dry_stops(self):
  r=simulate('downhill_dry_stop',mu=.6)
  self.assertLess(r['final_speed_mps'],0.005)
 def test_powered_wet_keeps_moving(self):
  r=simulate('downhill_wet_stop',mu=.15)
  self.assertGreater(r['final_speed_mps'],.3)

class Geometry(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.A,cls.items,cls.geo=cad.construct(0)
  cls.AR,cls.p_released,cls.geo_release=cad.construct(15)
 def test_per_side_drive_present(self):
  names={i['name'] for i in self.items}
  for side in ('LEFT','RIGHT'):
   for suffix in ('gearbox_42mm','RS775_motor_can','rubber_tread','steel_axle_10mm'):
    self.assertIn(f'{side}_{suffix}',names)
 def test_contact_geometry(self):
  for sign in (-1,1):
   c=self.geo['roller_center_left_mm'] if sign>0 else self.geo['roller_center_right_mm']
   d=math.hypot(c[0]-cad.base.S.rear_axle_x,c[2]-cad.base.S.rear_diameter/2)
   self.assertAlmostEqual(d,cad.C.wheel_d/2+cad.C.roller_od/2,places=5)
 def test_release_moves_friction_roller_15mm(self):
  b=self.geo['roller_center_left_mm'];a=self.geo_release['roller_center_left_mm']
  self.assertAlmostEqual(math.dist(a,b),15,places=5)
 def test_release_does_not_move_fixed_clamps(self):
  data=lambda parts:{p['name']:p['shape'].Center() for p in parts if 'clamp_jaw' in p['name']}
  b=data(self.items);a=data(self.p_released)
  for name in b:self.assertLess((b[name]-a[name]).Length,1e-7)
 def test_standard_6000_bearing_dims(self):
  self.assertEqual((cad.C.bearing_bore,cad.C.bearing_od,cad.C.bearing_w),(10,26,8))
 def test_shell_parts_valid(self):
  self.assertTrue(all(i['shape'].isValid() for i in self.items))

if __name__=='__main__':unittest.main(verbosity=2)
