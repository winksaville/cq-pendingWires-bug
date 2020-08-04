import cadquery as cq

# The path that we'll sweep
path = cq.Workplane("XZ") .moveTo(0, 4) .radiusArc(endPoint=(4, 0), radius=4)
#show_object(path)

# Sketch 1
s1 = cq.Workplane("YZ").moveTo(0, 4).rect(2, 1)
#show_object(s1)

# Sketch 2
s2 = cq.Workplane("XY").moveTo(4, 0).circle(0.5)
#show_object(s2)

# BUG?: len(c.ctx.pendingWires) should equal 2 at this point, but it equals 1
c = s1.add(s2)
log(f"len(c.ctx.pendingWires)={len(c.ctx.pendingWires)}")
#show_object(c)

# This not the desired output, only the rectangle in s1 was used in the sweep
result = c.sweep(path, multisection=True)
show_object(result.translate((0, 0, 0)))

# Clearing pending wires and looking at each sets pendingWires
c.ctx.pendingWires = []
r = c.each(lambda shape: shape)
log(f"len(r.ctx.pendingWires)={len(r.ctx.pendingWires)}")

# This is the desired result, sweep from rectangle to circle
result = r.sweep(path, multisection=True)
show_object(result.translate((0, 5, 0)))
