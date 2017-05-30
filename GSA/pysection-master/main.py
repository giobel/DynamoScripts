import json
import math

import shape
import material
import section
import slab

def dump_json(obj,indent=None):
    return json.dumps(obj, default=lambda o: o.__dict__,indent=indent)

def test_rect_section():
    #create materials
    conc = material.Concrete(30)
    steel = material.Steel(500,200000)

    #define profile
    profile = shape.Rectangle(500,700)
    bars = [
        #section.Bar(steel,section.Bar.diam_20M, 65),
        #section.Bar(steel,section.Bar.diam_20M, 65),
        #section.Bar(steel,section.Bar.diam_20M, 65),
        #section.Bar(steel,section.Bar.diam_20M, 65),
        section.Bar(steel,section.Bar.diam_30M,635),
        section.Bar(steel,section.Bar.diam_30M,635),
        section.Bar(steel,section.Bar.diam_30M,635),
        section.Bar(steel,section.Bar.diam_30M,635)]
    sec = section.Section(conc,profile,bars)

    #set material factors
    sec.concrete_factor = 0.65
    sec.steel_factor = 0.85

    #calc peak axial strength
    #print(sec.calc_peak_axial_strength())

    #print MN Chart
    file = open('mn.csv', 'w')

    for M,N in sec.calc_M_N().entries:
        file.write(str(M) + "," + str(N) + "\n")



test_rect_section()

def test_circle_section():
    #create materials
    conc = material.Concrete(40)
    steel = material.Steel(463,194000)

    #define profile
    profile = shape.Circle(355.6)
    bars = [
        section.Bar(steel,12.5, 50.00),
        section.Bar(steel,12.5,115.25),
        section.Bar(steel,12.5,115.25),
        section.Bar(steel,12.5,244.75),
        section.Bar(steel,12.5,244.75),
        section.Bar(steel,12.5,309.50)]
    sec = section.Section(conc,profile,bars)

    #set material factors
    sec.concrete_factor = 1
    sec.steel_factor = 1

    #calc peak axial strength
    #print(sec.calc_peak_axial_strength())

    #print MN Chart
    file = open('mn.csv', 'w')

    for M,N in sec.calc_M_N().entries:
        file.write(str(M) + "," + str(N) + "\n")

def test_slab():
    #create materials
    conc = material.Concrete(45)
    steel = material.Steel(420,200000)

    #define slab with materials and thickness
    s = slab.Slab(conc,steel,1525)

    #set slab properties
    s.cover_top = 40
    s.cover_bot = 75
    s.aggregate_size = 19
    s.inner_layer = "X"

    #add bars to slab
    #In X: 2X25 @150 TF2 TF4 BF2 BF4
    #In Y: 2X25 @150 TF2 TF4 2X32 @150 BF2 BF4
    s.layers_x_top = [slab.BarLayer([25],150),slab.BarLayer([25],150)]
    s.layers_x_bot = [slab.BarLayer([25],150),slab.BarLayer([25],150)]

    s.layers_y_top = [slab.BarLayer([25],150),slab.BarLayer([25],150)]
    s.layers_y_bot = [slab.BarLayer([32],150),slab.BarLayer([32],150)]

    #set concrete factors before updating sections
    s.concrete_factor = 0.65
    s.steel_factor = 0.85

    s.update_sections()

    #output MN Chart
    file = open('mn.csv', 'w')

    MNChart = s.section_x.calc_M_N()

    for M,N in MNChart.entries:
        file.write(str(M) + "," + str(N) + "\n")



def test_materials():
    print(dump_json(conc))
    print()

    print("Hognestad")
    print(conc.calc_stress_hognestad(-0.0040))
    print(conc.calc_stress_hognestad(-0.0030))
    print(conc.calc_stress_hognestad(-0.0020))
    print(conc.calc_stress_hognestad(-0.0010))
    print(conc.calc_stress_hognestad( 0.0000))
    print(conc.calc_stress_hognestad( 0.0010))
    print(conc.calc_stress_hognestad( 0.0020))
    print(conc.calc_stress_hognestad( 0.0030))
    print()

    print("Popovics NSC")
    print(conc.calc_stress_popovics_nsc(-0.0040))
    print(conc.calc_stress_popovics_nsc(-0.0030))
    print(conc.calc_stress_popovics_nsc(-0.0020))
    print(conc.calc_stress_popovics_nsc(-0.0010))
    print(conc.calc_stress_popovics_nsc( 0.0000))
    print(conc.calc_stress_popovics_nsc( 0.0010))
    print(conc.calc_stress_popovics_nsc( 0.0020))
    print(conc.calc_stress_popovics_nsc( 0.0030))
    print()

    print("Popovics HSC")
    print(conc.calc_stress_popovics_hsc(-0.0040))
    print(conc.calc_stress_popovics_hsc(-0.0030))
    print(conc.calc_stress_popovics_hsc(-0.0020))
    print(conc.calc_stress_popovics_hsc(-0.0010))
    print(conc.calc_stress_popovics_hsc( 0.0000))
    print(conc.calc_stress_popovics_hsc( 0.0010))
    print(conc.calc_stress_popovics_hsc( 0.0020))
    print(conc.calc_stress_popovics_hsc( 0.0030))
    print()

    print("Hoshikuma")
    print(conc.calc_stress_hoshikuma(-0.0040))
    print(conc.calc_stress_hoshikuma(-0.0030))
    print(conc.calc_stress_hoshikuma(-0.0020))
    print(conc.calc_stress_hoshikuma(-0.0010))
    print(conc.calc_stress_hoshikuma( 0.0000))
    print(conc.calc_stress_hoshikuma( 0.0010))
    print(conc.calc_stress_hoshikuma( 0.0020))
    print(conc.calc_stress_hoshikuma( 0.0030))
    print()

    print(dump_json(steel))
    print()

    print(steel.calc_stress(-0.0020))
    print(steel.calc_stress(-0.0010))
    print(steel.calc_stress( 0.0000))
    print(steel.calc_stress( 0.0000))
    print(steel.calc_stress( 0.0010))
    print(steel.calc_stress( 0.0020))
    print(steel.calc_stress( 0.0030))
    print(steel.calc_stress( 0.0040))
    print(steel.calc_stress( 0.0050))
    print(steel.calc_stress( 0.0060))
    print(steel.calc_stress( 0.0070))
    print(steel.calc_stress( 0.0080))
    print()

def test_shapes():
    circle = shape.Circle(2)

    print(dump_json(circle))
    print()

    print(circle.area())
    print(circle.sector_head(0))
    print(circle.sector_head(0.5))
    print(circle.sector_head(1))
    print(circle.sector_head(1.5))
    print(circle.sector_head(2))

    triangle = shape.TriangleDown(10,5)

    print(dump_json(triangle))
    print()

    print(triangle.area())
    print(triangle.area_slice(0,1))
    print(triangle.area_slice(1,2))
    print(triangle.area_slice(0,2))
    print(triangle.area_slice(0,3))
    print(triangle.area_slice(0,4))
    print(triangle.area_slice(0,5))

    diameter = 355.6
    beam = shape.Circle(diameter)

    for i in range(0,19):
        start = diameter/2-190
        area = beam.area_slice(start+i*20,start+(i+1)*20)

#def test_image():
    #https://pypi.python.org/pypi/Pillow/4.1.0
    #from PIL import Image, ImageDraw

    #im = Image.new("RGB",(640,480),0xffffff)

    #draw = ImageDraw.Draw(im)
    #draw.line([(0,0),(320,240)],fill=0xff0077,width=3)

    #im.show()
