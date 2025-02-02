import time

time.sleep(0.1)  # Wait for USB to become ready


import badger2040
import jpegdec
import uio
import ujson

# Set some constants
CONFIGPATH = "/moods/"
CONFIGFILE = "config.json"
STATEFILE = "/state.txt"

badger = badger2040.Badger2040()
jpeg = jpegdec.JPEG(badger.display)


def write_mood(mood):
    f = uio.open(STATEFILE, "wt")
    f.write(str(mood))
    f.close()
    f = uio.open(STATEFILE, "r")
    read_mood = f.read()
    f.close()
    return read_mood


def read_mood():
    f = uio.open(STATEFILE, "r")
    read_mood = f.read()
    f.close()
    return read_mood


def refresh_screen(mood, num_moods, speed):
    badger.set_update_speed(speed)
    badger.set_pen(15)
    badger.rectangle(0, 0, badger2040.WIDTH, badger2040.HEIGHT)
    badger.set_thickness(3)
    badger.set_pen(0)
    badger.set_font("sans")

    badger.text(config["moods"][mood][0], 140, 50, scale=0.75)

    jpeg.open_file(CONFIGPATH + config["moods"][mood][1])
    jpeg.decode(0, 0)

    for i in range(num_moods):
        x = 286
        y = int((128 / 2) - (num_moods * 10 / 2) + (i * 10))
        badger.set_pen(0)
        badger.rectangle(x, y, 8, 8)
        if mood != i:
            badger.set_pen(15)
            badger.rectangle(x + 1, y + 1, 6, 6)

    badger.update()


# Open the config file and read out the json
f = uio.open(CONFIGPATH + CONFIGFILE, mode="r")
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

if saved_mood >= len(config["moods"]):
    saved_mood = 0
    write_mood(str(saved_mood))

mood = saved_mood

while True:
    display_was_changed = False
    now = time.time()
    while time.time() - now < 3:

        if badger.pressed_any():
            badger.led(10)
            now = time.time()
            if badger.pressed(badger2040.BUTTON_DOWN):
                badger.led(64)
                mood += 1
                if mood >= len(config["moods"]):
                    mood = 0
                write_mood(str(mood))
                # as fast as we can go without ghosting
                refresh_screen(
                    mood, len(config["moods"]), badger2040.UPDATE_TURBO
                )
                display_was_changed = True

            elif badger.pressed(badger2040.BUTTON_UP):
                badger.led(64)
                mood -= 1
                if mood < 0:
                    mood = len(config["moods"]) - 1
                write_mood(str(mood))
                # as fast as we can go without ghosting
                refresh_screen(
                    mood, len(config["moods"]), badger2040.UPDATE_TURBO
                )
                display_was_changed = True

            else:
                pass

            badger.led(0)

    # eliminate ghosting if they display was changed but has't changed for 3 seconds
    if display_was_changed:
        refresh_screen(mood, len(config["moods"]), badger2040.UPDATE_FAST)
        display_was_changed = False

    badger2040.turn_off()
