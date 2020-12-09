# This file is required. Use the same name, "test.py". Below you see an example
# of importing a class from "source.py", instantiating a new object and printing
# that object. Replace the code below with your own.

from source import Channel

ch = Channel(b=160, zleft=2, zright=2, n=0.014, slope=0.0034, q=83700, y1=15, y2=17, alpha=1.05)

if __name__ == '__main__':
    print(ch.direct_step(tograph=True))