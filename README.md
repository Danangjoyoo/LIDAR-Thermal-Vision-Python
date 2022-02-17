## Research Journals
- https://docs.google.com/document/d/1wTaqokRTCPI-C6tkusbhQnFXuTEDnBpD9FGaUGyI0M0/edit?pli=1

## Prerequisites
- Ubuntu 20.04
- CUDA 11.5
- CuDNN 8.3
- OpenCV 4.4.0 CUDA
- GCC 7

## How To Setup Prerequisites Fresh
- check 'hot-to-setup.txt' or 'initialSetup.sh'

## How to run?
- `python3 main.py -t 1` to run with thermal tracking
- `python3 main.py` to run without thermal tracking
- `python3 main.py -h` to see helps
- Helps
```
usage: main.py [-h] [-t THERMAL] [-tf THERMAL_FRAME] [-dt DRAW_THERMAL] [-df DEPTH_FRAME] [-dd DRAW_DEPTH]
               [-sd SHOW_DISTANCE] [-sid SHOW_ID]

optional arguments:
  -h, --help            show this help message and exit
  -t THERMAL, --thermal THERMAL
                        Enable Thermal Measurement
  -tf THERMAL_FRAME, --thermal-frame THERMAL_FRAME
                        show thermal frame
  -dt DRAW_THERMAL, --draw-thermal DRAW_THERMAL
                        draw box in thermal frame
  -df DEPTH_FRAME, --depth-frame DEPTH_FRAME
                        show depth frame
  -dd DRAW_DEPTH, --draw-depth DRAW_DEPTH
                        draw box in depth frame
  -sd SHOW_DISTANCE, --show-distance SHOW_DISTANCE
                        show distance value
  -sid SHOW_ID, --show-id SHOW_ID
                        show object id
```

## GUI Handler
while Video GUI / player is shown, you can press the hotkey below
```
KEYS:
  u -> enter update session
  b -> enable/disable boundary show
  1 -> set up entry line
  2 -> set up exit line
  s -> save boundary
  r -> reverse/swap entry and exit
  q -> exit update session
```

![Alt text](help/config_update_session.png?raw=true "config_update_session.png")