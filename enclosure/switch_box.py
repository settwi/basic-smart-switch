# ---
# All units are in millimeter
# W.S. Nov 2022
# --- 
import cadquery as cq
import numpy as np

wall_thick = 5
bevel = 3

outer_height = 70
outer_width = 110
outer_length = 190
inner = lambda x: x - (2 * wall_thick)

# loose fit
fit_pad = 0.25
lip_depth = 2
post_inner_diameter = 4 + fit_pad
post_outer_diameter = post_inner_diameter + wall_thick
post_inset = (wall_thick + post_outer_diameter) / 2

# M4 x 0.7 screw and nut
counterbore_diam = 7.2 + fit_pad
mounting_nut_diam = 7.2 + fit_pad
mounting_nut_depth = 3 + fit_pad
nut_slice_width = 15
nut_hole_dz = outer_height - 30
counterbore_depth = post_inner_diameter

compy_spacing = 10
compy_post_wid = 49
compy_post_len = 58
compy_post_h = 8

compy_post_rad = 2.75 / 2 - fit_pad
thicker_delta = 0.5
thicker_portion = 0.4
compy_thick_post_height = compy_post_h * thicker_portion
compy_thin_post_height = compy_post_h * (1 - thicker_portion)
compy_thick_post_rad = compy_post_rad + thicker_delta

screw_post_x = outer_width - (2 * post_inset)
screw_post_y = outer_length - (2 * post_inset)


outer_shell = (
    cq.Workplane('XY')
    .rect(outer_width, outer_length)
    .extrude(until=outer_height + lip_depth)
    .edges()
    .fillet(radius=bevel)
)


inner_chunk = (
    outer_shell
    .faces('<Z')
    .workplane(offset=wall_thick, invert=True)
    .rect(inner(outer_width), inner(outer_length))
    .extrude(until=inner(outer_height), combine=False)
)

sliced = outer_shell.cut(inner_chunk)

sliced = (
    sliced
    .faces(">Z")
    .workplane(offset=-wall_thick)
    .rect(screw_post_x, screw_post_y, forConstruction=True)
    .vertices()
    # .rect(post_outer_diameter, post_outer_diameter)
    .circle(post_outer_diameter / 2)
    .circle(post_inner_diameter / 2)
    .extrude(-1 * (outer_height + lip_depth - wall_thick), combine=True)
)

lid, bottom = (
    sliced
    .faces(">Z")
    .workplane(-1 * (wall_thick + lip_depth))
    .split(keepTop=True, keepBottom=True)
    .all()
)

lid = (
    lid
    .translate((0, 0, -lip_depth))
    .cut(bottom)
    .translate((outer_width + wall_thick, 0, wall_thick - outer_height + lip_depth))
    .faces('>Z')
    .workplane(centerOption='CenterOfBoundBox')
    .rect(screw_post_x, screw_post_y, forConstruction=True)
    .vertices()
    .cboreHole(
        diameter=post_inner_diameter,
        cboreDiameter=counterbore_diam,
        cboreDepth=counterbore_depth,
        depth=2 * wall_thick)
    .rotateAboutCenter(
        axisEndPoint=(1, 0, 0),
        angleDegrees=180)
)

base_screw_stuff = (
    cq.Workplane('XY')
    .rect(screw_post_x, screw_post_y, forConstruction=True)
    .vertices()
)

nut_holes = (
    base_screw_stuff
    .rect(nut_slice_width, nut_slice_width)
    .extrude(until=mounting_nut_depth)
    .translate((0, 0, nut_hole_dz))
)

screw_through = (
    base_screw_stuff
    .circle(radius=post_inner_diameter / 2)
    .extrude(until=2 * wall_thick)
)

bottom = (
    bottom
    .cut(nut_holes)
    .cut(screw_through)
)

def add_compy_posts(bottom, distance_from_wall: float):
    def compy_post_vertices(bottom_portion):
        return (
            bottom_portion
            .faces('<Z')
            .translate((0, 0, wall_thick))
            .rect(compy_post_wid, compy_post_len, forConstruction=True)
            .vertices()
        )

    dx = (inner(outer_width) - compy_post_wid)/2 - distance_from_wall - compy_thick_post_rad
    dy = (-inner(outer_length) + compy_post_len)/2 + distance_from_wall + compy_thick_post_rad
    bottom = (
        compy_post_vertices(bottom)
        .translate((dx, dy, 0))
        .circle(radius=compy_post_rad + thicker_delta)
        .extrude(until=compy_post_h * thicker_portion)
    )

    bottom = (
        compy_post_vertices(bottom)
        .translate((dx, dy, compy_thick_post_height))
        .circle(radius=compy_post_rad)
        .extrude(until=compy_thin_post_height)
    )
    return dx, dy, bottom


compy_x_ctr, compy_y_ctr, bottom = add_compy_posts(bottom, distance_from_wall=compy_spacing)
compy_leftwall_x = compy_x_ctr - compy_spacing - compy_post_wid/2 - wall_thick/2 - compy_thick_post_rad
compy_leftwall_len = 2*compy_spacing + compy_post_len + 2*compy_thick_post_rad
# fill in otherwise empty corner
compy_leftwall_len += 2 * wall_thick
compy_wall_height_mult = 0.8
bottom = (
    bottom
    .faces('<Z')
    .translate((compy_leftwall_x, compy_y_ctr, wall_thick))
    .rect(wall_thick, compy_leftwall_len)
    .extrude(inner(outer_height) * compy_wall_height_mult)
)

compy_topwall_y = compy_y_ctr + compy_spacing + compy_post_len/2 + wall_thick/2 + compy_thick_post_rad
compy_topwall_len = 2*compy_spacing + compy_post_wid + 2*compy_thick_post_rad
bottom = (
    bottom
    .faces('<Z')
    .translate((compy_x_ctr, compy_topwall_y, wall_thick))
    .rect(compy_topwall_len, wall_thick)
    .extrude(inner(outer_height) * compy_wall_height_mult)
)


compy_top_slot_height = 12
compy_top_slot_width = 32
compy_top_slot_offset = 5
compy_top_slot_x = compy_x_ctr + compy_top_slot_offset
compy_top_slot_y = compy_topwall_y + wall_thick/2
compy_top_slot_z = wall_thick + compy_top_slot_height/2
compy_top_slot = (
    cq.Workplane('XZ')
    .rect(compy_top_slot_width, compy_top_slot_height)
    .extrude(until=wall_thick)
    .translate((compy_top_slot_x, compy_top_slot_y, compy_top_slot_z))
)
bottom = bottom.cut(compy_top_slot)

usb_slot_width = 20
usb_slot_height = usb_slot_width / 2
# offset for usb plug on the board (~1/4" ~= 6mm)
usb_slot_x_offset = 10
usb_slot_x = compy_x_ctr - compy_post_wid/2  + usb_slot_x_offset
usb_slot_y = -outer_length/2 + wall_thick
usb_slot_z = wall_thick + usb_slot_height/2 + compy_thick_post_height
usb_slot = (
    cq.Workplane('XZ')
    .rect(usb_slot_width, usb_slot_height)
    .extrude(until=wall_thick)
    .translate((usb_slot_x, usb_slot_y, usb_slot_z))
)

cord_diameter = 6.5
cord_space_from_wall = 10
cord_slot_z = wall_thick + cord_diameter/2
cord_slot_y = 0
cord_slot_x = -inner(outer_width)/2 + cord_space_from_wall + cord_diameter/2
mains_slot = (
    cq.Workplane('XZ')
    .rect(cord_diameter, cord_diameter)
    .extrude(until=outer_length)
    .translate((cord_slot_x, cord_slot_y + outer_length/2, cord_slot_z))
)

relay_post_dy = 12
wall_relay_post_center_to_center = 52
wall_relay_post_width = 10
wall_relay_post_length = 9.5
wall_relay_post_height = 50
wall_relay_post_crds = (
    outer_width/2 - wall_thick - wall_relay_post_width/2,
    compy_top_slot_y + relay_post_dy + wall_relay_post_length/2,
    wall_thick
)


wall_relay_posts = (
    cq.Workplane('XY')
    .pushPoints(((0, 0), (0, wall_relay_post_center_to_center)))
    .rect(wall_relay_post_width, wall_relay_post_length)
    .extrude(until=wall_relay_post_height)
    .translate(wall_relay_post_crds)
)

relay_displace_from_left = 77
rcap_dims = (5, 25)
rcap_height = wall_relay_post_height
rcap_ctr = (
    inner(outer_width)/2 - relay_displace_from_left - rcap_dims[0]/2,
    wall_relay_post_crds[1] + wall_relay_post_center_to_center/2,
    wall_thick
)
relay_cap = (
    cq.Workplane('XY')
    .rect(*rcap_dims)
    .extrude(rcap_height)
    .translate(rcap_ctr)
)

def drill_lid_holes(lid, width, length, edge_pad, num, diam):
    slot_length = width - 2*edge_pad
    occupy_width = (length - 2*edge_pad)

    slot_centers = [
        (0, y, 0) for y in np.linspace(-occupy_width/2, occupy_width/2, num=num)
    ]

    return (
        lid
        .workplane(offset=wall_thick + lip_depth)
        .pushPoints(slot_centers)
        .slot2D(length=slot_length, diameter=diam, angle=0)
        .cutThruAll()
    )

# fillet before hole cutting
lid = drill_lid_holes(
    lid=lid,
    width=outer_width,
    length=outer_length,
    edge_pad=15,
    num=8,
    diam=4
)

bottom = (
    bottom
    .cut(compy_top_slot)
    .cut(usb_slot)
    .cut(mains_slot)
    .union(wall_relay_posts)
    .union(relay_cap)
)
cq.exporters.export(bottom, 'bottom.stl')
cq.exporters.export(lid, 'lid.stl')
