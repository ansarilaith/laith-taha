# notify
print('RUN: main.py')

# run the cube
import cube
cuber = cube.CUBE()
cuber.timezone  = -5
cuber.clocktype = 12
cuber.dmode = 1
cuber.useconfig = False
cuber.run()
print('CUBE CLOSED')

