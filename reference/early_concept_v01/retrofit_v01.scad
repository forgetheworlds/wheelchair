/*
Open-source friction-drive wheelchair retrofit / CONCEPT CAD V0.1.
All dimensions mm. This is an envelope/fit exploration; NOT a validated
mobility device or validated load-bearing design. No occupied testing.

Select 'assembly' for layout, or printable concepts:
 'tpu_roller_sleeve', 'tube_shim', 'joystick_shell', 'battery_tray',
 'electronics_tray'. Alter parameters after measuring your chair and
obtaining full mechanical datasheets from suppliers.

Axes: X forward, Y left/right, Z upward; rear-wheel axle at X=0.
The motor bodies are deliberately inboard and under/rearward of the seat.
Metal arm and clamp in assembly are visual placeholders, NOT printable.
*/
$fn=60;
part="assembly";

// --- reference geometry (PROVISIONAL; measure the actual chair) ---
wheel_outer_d=610;        // 24-inch-class outer tire envelope (not rim nominal)
wheel_track=590;          // tire center-to-center; NOT seat width
wheel_tire_width=32;
wheel_rad=wheel_outer_d/2;
frame_tube_od=25;         // chair frame tube outside diameter
seat_width=430;
seat_height=505;

// --- friction-drive cartridge envelope ---
roller_d=50;
roller_width=30;
roller_hub_id=30;        // TPU sleeve bore onto positively retained metal hub
motor_d=60;              // change to 42 for smaller motor option
motor_length=112;       // incl. gearbox, illustrative only
shaft_gap=10;
contact_angle=150;      // degrees measured from +X, X-Z rear-upper quadrant
shaft_d=8;              // illustrative (unknown until motor selected)

// --- enclosure and battery envelopes ---
battery_length=152;
battery_width=97;
battery_height=65;      // battery rotated flat under seat; see datasheet
battery_clearance=5;
joy_length=74;
joy_width=63;
joy_height=28;

function rx()=(wheel_rad + roller_d/2)*cos(contact_angle);
function rz()=wheel_rad + (wheel_rad + roller_d/2)*sin(contact_angle);
function motor_y(side)=side*(wheel_track/2-roller_width/2-shaft_gap-motor_length/2);
function roller_y(side)=side*wheel_track/2;

// Cylindrical solid with its axis in global Y
module cyl_y(h, r, center=true) rotate([90,0,0]) cylinder(h=h,r=r,center=center);

module wheel_reference(side){
  color([0.17,0.18,0.2,0.55]) translate([0,roller_y(side),wheel_rad])
    difference(){
      cyl_y(wheel_tire_width,wheel_rad);
      cyl_y(wheel_tire_width+2,wheel_rad-26);
    }
  color([0.64,0.65,0.68,0.7]) translate([0,roller_y(side),wheel_rad])
    difference(){cyl_y(10,wheel_rad-26);cyl_y(12,wheel_rad-40);}
  color([0.56,0.57,0.60]) translate([0,roller_y(side),wheel_rad]) cyl_y(20,12);
}

module wheelchair_reference(){
  // Rear axle, seat, back, simplified frame for SPATIAL CONTEXT ONLY
  wheel_reference(-1); wheel_reference(1);
  color([0.37,0.42,0.47,0.7]){
    for(s=[-1,1]){
      translate([-128,s*205,235]) cylinder(h=300, r=frame_tube_od/2);
      translate([130,s*205,235]) cylinder(h=270, r=frame_tube_od/2);
      translate([-4,s*205,440]) rotate([0,90,0]) cylinder(h=245,r=11,center=true);
    }
    translate([-128,0,350]) cube([18,410,18],center=true);
  }
  color([0.30,0.39,0.50,0.25]) translate([20,0,seat_height]) cube([380,seat_width,18],center=true);
  color([0.3,0.4,0.52,0.2]) translate([-135,0,620]) cube([18,seat_width,210],center=true);
}

module metal_placeholder_arm(side){
  // Two sheet-metal members in CAD are conceptual ONLY, not 3D-print instructions.
  pivot=[-128,side*205,445];
  mount=[rx(),motor_y(side),rz()];
  color([0.42,0.47,0.50]){
    hull(){
      translate(pivot) sphere(r=10,$fn=24);
      translate([mount[0],side*205,mount[2]]) sphere(r=10,$fn=24);
    }
    // two hypothetical metal tube U-bolts at pivot
    translate(pivot) cyl_y(14,15);
  }
}

module drive_cartridge(side){
  metal_placeholder_arm(side);
  // Motor: orientation parallel to wheel axle, body inboard of the wheel
  color([0.32,0.35,0.40]) translate([rx(),motor_y(side),rz()])
    cyl_y(motor_length,motor_d/2);
  // Metal shaft/coupler envelope
  color([0.74,0.75,0.75]) translate([rx(),side*(wheel_track/2-roller_width/2-shaft_gap/2),rz()])
    cyl_y(shaft_gap+4,shaft_d/2);
  // Soft roller against tread
  color([0.04,0.55,0.59]) translate([rx(),roller_y(side),rz()])
    difference(){cyl_y(roller_width,roller_d/2); cyl_y(roller_width+2,roller_hub_id/2);}
  color([0.62,0.62,0.66]) translate([rx(),roller_y(side),rz()]) cyl_y(roller_width,roller_hub_id/2);
}

module battery_tray(){
  inner_x=battery_length+2*battery_clearance;
  inner_y=battery_width+2*battery_clearance;
  outer_x=inner_x+6; outer_y=inner_y+6;
  difference(){
    union(){
      cube([outer_x,outer_y,4],center=false);
      for(x=[0,outer_x-3]) translate([x,0,0]) cube([3,outer_y,27]);
      for(y=[0,outer_y-3]) translate([0,y,0]) cube([outer_x,3,27]);
    }
    // slots for two nonprinted restraint straps
    for(x=[outer_x*0.30,outer_x*0.70],y=[4,outer_y-22])
      translate([x-3,y, -0.5]) cube([6,18,6]);
    // drainage/inspection openings
    for(x=[outer_x*.22,outer_x*.78]) translate([x-8,outer_y/2-18,-0.5]) cube([16,36,6]);
  }
}

module joystick_shell(){
  // OPEN-TOP printed enclosure. Lid/secure control mounting NOT yet designed.
  difference(){
    cube([joy_length,joy_width,joy_height],center=false);
    translate([3,3,3]) cube([joy_length-6,joy_width-6,joy_height+2]);
    translate([joy_length/2,-1,12]) rotate([-90,0,0]) cylinder(h=5,d=10);
    for(x=[10,joy_length-10],y=[9,joy_width-9])
      translate([x,y,-1]) cylinder(h=6,d=4.4);
  }
}

module electronics_tray(){
  // Only a placeholder until the specific board(s) and cooling are chosen.
  difference(){
    cube([128,88,31]);
    translate([3,3,3]) cube([122,82,34]);
    for(x=[9,119],y=[8,80]) translate([x,y,-1]) cylinder(h=6,d=4.5);
  }
}

module tpu_roller_sleeve(){
  // TPU test sleeve; metal keyed hub & positive mechanical capture REQUIRED.
  difference(){
    cylinder(h=roller_width, d=roller_d);
    translate([0,0,-1]) cylinder(h=roller_width+2,d=roller_hub_id);
    // 2 shallow circumferential traction grooves
    for(z=[8,21]) translate([0,0,z])
      difference(){cylinder(h=2,d=roller_d+0.5);cylinder(h=2,d=roller_d-2.2);}
  }
}

module tube_shim(){
  // Flexible nonstructural liner; 2 per mounting location. Clamp is METAL.
  shim_len=45; shim_wall=2.2; gap=0.8;
  difference(){
    cylinder(h=shim_len,d=frame_tube_od+2*shim_wall);
    translate([0,0,-1]) cylinder(h=shim_len+2,d=frame_tube_od+0.35);
    translate([-gap/2,-frame_tube_od, -1]) cube([gap,frame_tube_od,shim_len+2]);
  }
}


module motor_alignment_saddle(){
  // Printable, non-load-bearing HALF-COLLAR used to align a motor against
  // a separately engineered METAL support strap; not a structural clamp.
  shell_t=3.5; saddle_len=48;
  difference(){
    intersection(){
      difference(){
        cylinder(h=saddle_len,d=motor_d+2*shell_t);
        translate([0,0,-1]) cylinder(h=saddle_len+2,d=motor_d+0.8);
      }
      translate([-(motor_d+2*shell_t),-motor_d-2*shell_t,-1])
        cube([2*(motor_d+2*shell_t),motor_d+2*shell_t,saddle_len+2]);
    }
  }
}

module assembly(){
  wheelchair_reference();
  drive_cartridge(-1); drive_cartridge(1);
  // tray and battery centred below the seat; envelope only
  translate([0,-(battery_width+2*battery_clearance+6)/2,375])
    color([0.12,0.47,0.69]) battery_tray();
  color([0.17,0.20,0.23,0.75]) translate([3,0,375+4+battery_height/2])
    cube([battery_length,battery_width,battery_height],center=true);
  // controller near front edge of battery
  color([0.20,0.55,0.45]) translate([112,-44,425]) electronics_tray();
  // occupant joystick control near right armrest; envelope only
  color([0.12,0.55,0.70]) translate([95,-seat_width/2-20,seat_height+45])
    joystick_shell();
}

if(part=="assembly") assembly();
else if(part=="tpu_roller_sleeve") tpu_roller_sleeve();
else if(part=="tube_shim") tube_shim();
else if(part=="joystick_shell") joystick_shell();
else if(part=="battery_tray") battery_tray();
else if(part=="electronics_tray") electronics_tray();
else if(part=="motor_alignment_saddle") motor_alignment_saddle();
else echo("Unknown part");
