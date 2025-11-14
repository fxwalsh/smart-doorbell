#!/usr/bin/env python3
from picamera2 import Picamera2
from time import sleep

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

print("Warming up camera...")
sleep(2)

output_file = "test.jpg"
print(f"Capturing image to {output_file}...")
picam2.capture_file(output_file)

picam2.stop()
print("Done.")