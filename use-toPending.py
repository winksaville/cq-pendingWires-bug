import cadquery as cq

def dbg(wp: cq.Workplane, name=None):
    if name is None:
        name = str(id(wp))
    log(f"{name}: len({name}.objects)={len(wp.objects)} len({name}.ctx.pendingWires)={len(wp.ctx.pendingWires)}")
    for i in range(0, len(wp.objects)):
        log(f"{name} objects[{i}]: {str(id(wp.objects[i]))}")
    for i in range(0, len(wp.ctx.pendingWires)):
        log(f"{name} pendingWires[{i}]: {str(id(wp.ctx.pendingWires[i]))}")

# The path that we'll sweep
path = cq.Workplane("XZ") .moveTo(0, 4) .radiusArc(endPoint=(4, 0), radius=4)

# Sketch 1, 1 object, 1 wire pending
s1 = cq.Workplane("YZ").moveTo(0, 4).rect(2, 1)
dbg(s1, "s1")

# Sketch 2, 1 object, 1 wire pending
s2 = cq.Workplane("XY").moveTo(4, 0).circle(0.5)
dbg(s2, "s2")

# Use add s2 to s1, 1 object, 1 wire is pending
s1s2 = s1.add(s2)
dbg(s1s2, "s1s2")

# Now do s1s2.toPending(), 2 objects, 3 wires pending
c = s1s2.toPending()
dbg(c, "c")

# Doing another toPending, 2 objects, 5 wires pending
c5 = c.toPending()
dbg(c, "c5")

# We now sweep, 1 object, 0 wires pending
r = c5.sweep(path, multisection=True)
dbg(r, "r")
show_object(r.translate((0, 0, 0)), "r")
