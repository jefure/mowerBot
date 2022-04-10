$fs = 0.01;
wheel_radius = 80;

module wheel() {
    thickness = 12;
    
    difference() {
        cylinder(h=thickness,r=wheel_radius);
        translate([0,0,-2])  cylinder(h=14, r=2);
    }
}

difference() {
    wheel();
    translate([0,0,2]) hexagon(indiameter=13);    
}

function indiameter_to_diameter(d) = d/(sqrt(3)/2);
module hexagon(indiameter, height = 12){
    diameter = indiameter_to_diameter(indiameter);
    translate([0,0,0])  cylinder(d=diameter, h = height + 4, $fn=6);
};
module tooth() {
    cube([4, 4, 12]);
}

for(i=[0:15]) //n is number of teeth
    rotate([0,0,i*360/15])
        translate([wheel_radius - 1,0,0]) // r is radius of circle
            tooth();
