# Image Writer Example
#
# USE THIS EXAMPLE WITH A USD CARD! Reset the camera after recording to see the file.
#
# This example shows how to use the Image Writer object to record snapshots of what your
# OpenMV Cam sees for later analysis using the Image Reader object. Images written to disk
# by the Image Writer object are stored in a simple file format readable by your OpenMV Cam.

import sensor
import image
import pyb
import time

record_time = 1000  # in milliseconds
NUMBER_OF_SEQUENCES = 2  # don't take more than 100: 100*10s -> ~3GB of data
FPS = 2

inter_frame_ms = int(1000/FPS)

sensor.reset()
sensor.set_pixformat(sensor.BAYER)
sensor.set_framesize(sensor.VGA)
sensor.skip_frames(time = 2000)
clock = time.clock()

# Red LED on means we are capturing frames.
red_led = pyb.LED(1)
blue_led = pyb.LED(3)

for a in range(NUMBER_OF_SEQUENCES):
    img_writer = image.ImageWriter("/" + str(pyb.rng()) + ".bin")

    blue_led.off()
    red_led.on()

    start = pyb.millis()
    while pyb.elapsed_millis(start) < record_time:
        clock.tick()
        frame_start = pyb.millis()
        img = sensor.snapshot()
        img_writer.add_frame(img)
        pyb.delay(inter_frame_ms - pyb.elapsed_millis(frame_start))
#       print(clock.fps())

    print("File size: " + str(img_writer.size()))
    img_writer.close()

    # Blue LED on means we are done.
    red_led.off()
    blue_led.on()
    pyb.delay(2000)


print("Done")
while(True):
    pyb.wfi()
    img = sensor.snapshot()
