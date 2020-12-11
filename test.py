# This file is required. Use the same name, "test.py". Below you see an example
# of importing a class from "source.py", instantiating a new object and printing
# that object. Replace the code below with your own.

from source import Channel

# Checking HW 8 Problem 4
ch = Channel(b=12, zleft=0, zright=0, n=0.015, slope=0.0087, q=300)

print(ch.norm_depth())

# Checking HW 9 Problem 2
ch = Channel(b=160, zleft=2, zright=2, n=0.014, slope=0.0034, q=83700, y1=15, y2=17, alpha=1.05)

print(ch.direct_step(tograph=True))