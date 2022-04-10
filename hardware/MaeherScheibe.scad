$fn = 40;
outer_radius = 45;
inner_diameter = 10;
thickness = 4;
blade_length = 60;
blade_width = 20;
blade_thickness = 2;

difference() {
    cylinder(h = thickness + 2, r = outer_radius);
    translate([0,0,thickness -1])
        cylinder(h = 6, r = outer_radius - 10);
    cylinder(h = thickness + 2, d = inner_diameter);
    translate([- (blade_width / 2), blade_length / 3, 2]) cube(size = [blade_width, blade_length, blade_thickness]);
    translate([- (blade_width / 2), - (blade_length + (blade_length / 3)), 2]) cube(size = [blade_width, blade_length, blade_thickness]);
}