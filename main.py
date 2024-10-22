import time
time.sleep(0.1) # Wait for USB to become ready


import ujson
import uio

import badger2040
import jpegdec


#Set some constants
CONFIGPATH = "/moods/"
CONFIGFILE = "config.json"
STATEFILE = "/state.txt"

badger = badger2040.Badger2040()
jpeg = jpegdec.JPEG(badger.display)


def write_mood(mood):
    f = uio.open(STATEFILE, 'wt') 
    f.write(str(mood))
    f.close()
    f = uio.open(STATEFILE, 'r')
    read_mood = f.read()
    f.close()
    return read_mood

def read_mood():
    f = uio.open(STATEFILE, 'r')
    read_mood = f.read()
    f.close()
    return read_mood


def refresh_screen(mood,speed):
    badger.set_update_speed(speed)
    badger.set_pen(15)
    badger.rectangle(0,0,badger2040.WIDTH,badger2040.HEIGHT)
    badger.set_thickness(3)
    badger.set_pen(0)
    badger.set_font('sans')

    badger.text(config['moods'][mood][0], 140,50, scale = .75)


    jpeg.open_file(CONFIGPATH + config['moods'][mood][1])
    jpeg.decode(0, 0)
    badger.update()
    
    

# Open the config file and read out the json
f = uio.open(CONFIGPATH + CONFIGFILE, mode='r')
json_data = f.read()
f.close()
config = ujson.loads(json_data)

# Open the saved state and read out the saved mood
try:
    mood_text = read_mood()
    saved_mood = int(mood_text)
except:
    saved_mood = 0
    write_mood(str(saved_mood))

if saved_mood >= len(config['moods']):
    saved_mood = 0
    write_mood(str(saved_mood))

mood = saved_mood



while True:
    now = time.time()
    while (time.time() - now < 3):
    
        if (badger.pressed_any()):
            now = time.time()
            if badger.pressed(badger2040.BUTTON_UP):
                mood += 1
                if mood >= len(config['moods']):
                    mood = 0
            
            elif badger.pressed(badger2040.BUTTON_DOWN):
                mood -= 1
                if mood < 0 :
                    mood = len(config['moods']) - 1

                
            write_mood(str(mood))
            refresh_screen(mood,badger2040.UPDATE_TURBO)

    refresh_screen(mood,badger2040.UPDATE_NORMAL)
    badger2040.turn_off()





