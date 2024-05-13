import time

from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)

picam2.start()
time.sleep(2)

'''
size = picam2.capture_metadata()['ScalerCrop'][2:]

full_res = picam2.camera_properties['PixelArraySize']

print(size)
'''

'''
for _ in range(16):
    # This syncs us to the arrival of a new camera frame:
    picam2.capture_metadata()

    size = [int(s * 0.95) for s in size]
    offset = [(r - s) // 2 for r, s in zip(full_res, size)]
    picam2.set_controls({"ScalerCrop": offset + size})
    print(offset+ size)
'''

#picam2.set_controls({"ScalerCrop":[1546, 728, 1516, 1135]})

i =0

while i<120:
    if(input("Enter")!=1):
        job = picam2.autofocus_cycle(wait=False)
        success = picam2.wait(job)
        if success:
            picam2.capture_file(f'threepin{i}.jpg')
            i+=1

time.sleep(2)
