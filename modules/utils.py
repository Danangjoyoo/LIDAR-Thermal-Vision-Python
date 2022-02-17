import argparse

def getKwargv():
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--thermal", required = False, type = int, default = False, help = 'Enable Thermal Measurement')
    ap.add_argument("-tf", "--thermal-frame", required = False, type = int, default = False, help = 'show thermal frame')
    # ap.add_argument("-st", "--show-temp", required = False, type = int, default = False, help = 'show temperature value')
    ap.add_argument("-dt", "--draw-thermal", required = False, type = int, default = False, help = 'draw box in thermal frame')
    ap.add_argument("-df", "--depth-frame", required = False, type = int, default = False, help = 'show depth frame')
    ap.add_argument("-dd", "--draw-depth", required = False, type = int, default = False, help = 'draw box in depth frame')
    ap.add_argument("-sd", "--show-distance", required = False, type = int, default = False, help = 'show distance value')
    ap.add_argument("-sid", "--show-id", required = False, type = int, default = False, help = 'show object id')    
    return vars(ap.parse_args())