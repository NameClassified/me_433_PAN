from math import pi
import numpy as np
import matplotlib.pyplot as plt

scale = 3.3/1024

x_axis = list(range(0,100))

triangle = []
triangle.extend(list(range(0,1000,20)))
triangle.extend(list(range(1000,0,-20)))

#print(triangle)


def sine(n):
    return int((np.sin(n)*500)+500)

sinewave = np.arange(0,2*pi, pi/50)
result = map(sine,sinewave)
waveform0 = list(result)


print(waveform0)
fig = plt.plot(x_axis,waveform0)
plt.show()