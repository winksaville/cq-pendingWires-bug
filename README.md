# Pending wire bug

John Billingsley reported a [problem with sweep]( https://groups.google.com/g/cadquery/c/UrPx8CiSdY0/m/rYtuHCR6AgAJ).

While looking into John's Billingsley problem and learning how to use sweep
I ran into a problem that I feel is a bug.

When I create two separate sketches, then put them both on the stack using
`add()` and then do a sweep(). The result is a shape that was created only
using the rectangle in s1. See the shape on the left in the screenshot below
and lines 1..22 in the code:
```
(cq-dev) wink@3900x:~/prgs/CadQuery/projects/pendingWires-bug
$ cat -n pendingWires-bug.py 
     1	import cadquery as cq
     2	
     3	# The path that we'll sweep
     4	path = cq.Workplane("XZ") .moveTo(0, 4) .radiusArc(endPoint=(4, 0), radius=4)
     5	#show_object(path)
     6	
     7	# Sketch 1
     8	s1 = cq.Workplane("YZ").moveTo(0, 4).rect(2, 1)
     9	#show_object(s1)
    10	
    11	# Sketch 2
    12	s2 = cq.Workplane("XY").moveTo(4, 0).circle(0.5)
    13	#show_object(s2)
    14	
    15	# BUG?: len(c.ctx.pendingWires) should equal 2 at this point, but it equals 1
    16	c = s1.add(s2)
    17	log(f"len(c.ctx.pendingWires)={len(c.ctx.pendingWires)}")
    18	#show_object(c)
    19	
    20	# This not the desired output, only the rectangle in s1 was used in the sweep
    21	result = c.sweep(path, multisection=True)
    22	show_object(result.translate((0, 0, 0)))
    23	
    24	# Clearing pending wires and looking at each sets pendingWires
    25	c.ctx.pendingWires = []
    26	r = c.each(lambda shape: shape)
    27	log(f"len(r.ctx.pendingWires)={len(r.ctx.pendingWires)}")
    28	
    29	# This is the desired result, sweep from rectangle to circle
    30	result = r.sweep(path, multisection=True)
    31	show_object(result.translate((0, 5, 0)))```
```
A work around, lines 24..31 above, is to use
[each()](https://github.com/CadQuery/cadquery/blob/cc1f8f3183a16a1d222959c5860280e7bd3259bb/cadquery/cq.py#L2077)
to look at all of the items on the stack. What `each()` does is if an item
is a `Wire` and not `forConstruction`
[it calls](https://github.com/CadQuery/cadquery/blob/cc1f8f3183a16a1d222959c5860280e7bd3259bb/cadquery/cq.py#L2121)
the method [_addPendingWire()](https://github.com/CadQuery/cadquery/blob/cc1f8f3183a16a1d222959c5860280e7bd3259bb/cadquery/cq.py#L1982).
Which appends the `Wire` to ctx.pendingWires. The result is that the desired shape is created.
See the shape on the right in the screenshot below:

![](ss_pendingWires-bug.png)

Adam suggests using `toPending`, that works and processes both wires and edges.
```
(cq-dev) wink@3900x:~/prgs/CadQuery/projects/pendingWires-bug (master)
$ cat -n use-toPending.py 
     1	import cadquery as cq
     2	
     3	def dbg(wp: cq.Workplane, name=None):
     4	    if name is None:
     5	        name = str(id(wp))
     6	    log(f"{name}: len({name}.objects)={len(wp.objects)} len({name}.ctx.pendingWires)={len(wp.ctx.pendingWires)}")
     7	    for i in range(0, len(wp.objects)):
     8	        log(f"{name} objects[{i}]: {str(id(wp.objects[i]))}")
     9	    for i in range(0, len(wp.ctx.pendingWires)):
    10	        log(f"{name} pendingWires[{i}]: {str(id(wp.ctx.pendingWires[i]))}")
    11	
    12	# The path that we'll sweep
    13	path = cq.Workplane("XZ") .moveTo(0, 4) .radiusArc(endPoint=(4, 0), radius=4)
    14	
    15	# Sketch 1, 1 object, 1 wire pending
    16	s1 = cq.Workplane("YZ").moveTo(0, 4).rect(2, 1)
    17	dbg(s1, "s1")
    18	
    19	# Sketch 2, 1 object, 1 wire pending
    20	s2 = cq.Workplane("XY").moveTo(4, 0).circle(0.5)
    21	dbg(s2, "s2")
    22	
    23	# Use add s2 to s1, 1 object, 1 wire is pending
    24	s1s2 = s1.add(s2)
    25	dbg(s1s2, "s1s2")
    26	
    27	# Now do s1s2.toPending(), 2 objects, 3 wires pending
    28	c = s1s2.toPending()
    29	dbg(c, "c")
    30	
    31	# Doing another toPending, 2 objects, 5 wires pending
    32	c5 = c.toPending()
    33	dbg(c, "c5")
    34	
    35	# We now sweep, 1 object, 0 wires pending
    36	r = c5.sweep(path, multisection=True)
    37	dbg(r, "r")
    38	show_object(r.translate((0, 0, 0)), "r")
```
But using `toPending()` has a similar problem as `each()` in that `toPending()`
uses `extends()` to add the wires and edges which causes duplicates. In the
code above I to two `toPending()` calls and we end up with `c5` having 5 pendingWires
where as there are only two wire objects, s1 & s2. Luckily `sweep()` handles the
duplication fine, but it doesn't smell right to me.

Also, I find it weird that `each()` is adding pendingWires. But now doubly weird
that since it add to pendingWires why not pendingEdges? In actual, fact why iterating
over objects should there be any modifications of either pendingWires or pendingEdges?

Here is the screenshot for use-toPending.py:

![](./ss_use-toPending.png)