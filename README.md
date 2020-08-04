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

![](ss_pendingWires.png)

