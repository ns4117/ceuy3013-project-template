# This file is required. Use the same name, "test.py". Below you see an example
# of importing a class from "source.py", instantiating a new object and printing
# that object. Replace the code below with your own.

from source import Channel

ch = Channel(160, 2, 2, 0.014, 0.0034, 83700, 15, 17)

if __name__ == '__main__':
    print(ch)
