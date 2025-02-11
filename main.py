import time

time.sleep(0.1)  # Wait for USB to become ready


import badger2040
import jpegdec
import uio
import ujson

# Set some constants
CONFIGPATH = "/moods/"
CONFIGFILE = "config.json"
STATEFILE = "/state.json"
MOOD_TEXT_INDEX = 0
MOOD_IMAGE_INDEX = 1

# Keys used in the STATEFILE
CONFIGFILE_MOODS_KEY = "moods"
CONFIG_FILE_INITIAL_KEY = "initial"

# Keys used in the STATEFILE
STATEFILE_MOODSET_KEY = "moodset"
STATEFILE_MOOD_KEY = "mood"

badger = badger2040.Badger2040()
jpeg = jpegdec.JPEG(badger.display)

current_moodset = 0
current_mood = 0


# moodset is the index that determines the moodset
# mood is the index that determines the mood in the current moodset
# this could update the globals to simplify all the other code
#   but segregation of concerns says no
def write_mood(moodset, mood):
    f = uio.open(STATEFILE, "wt")
    ujson.dump({STATEFILE_MOODSET_KEY: moodset, STATEFILE_MOOD_KEY: mood}, f)
    f.close()
    return read_mood()


# JSON object with {moodset: int, mood: int}
# this could update the globals to simplify all the other code
#   but segregation of concerns says no
def read_mood():
    f = uio.open(STATEFILE, "r")
    read_mood_data = f.read()
    f.close()
    return ujson.loads(read_mood_data)


def refresh_screen(moodset, mood, num_moods, speed):
    badger.set_update_speed(speed)
    badger.set_pen(15)
    badger.rectangle(0, 0, badger2040.WIDTH, badger2040.HEIGHT)
    badger.set_thickness(3)
    badger.set_pen(0)
    badger.set_font("sans")

    # This could do bounds checking here
    badger.text(
        config[CONFIGFILE_MOODS_KEY][moodset][mood][MOOD_TEXT_INDEX],
        140,
        50,
        scale=0.75,
    )

    jpeg.open_file(
        CONFIGPATH
        + config[CONFIGFILE_MOODS_KEY][moodset][mood][MOOD_IMAGE_INDEX]
    )
    jpeg.decode(0, 0)

    # a square for each avaialble mood in this moodset
    for i in range(num_moods):
        x = 286
        y = int((128 / 2) - (num_moods * 10 / 2) + (i * 10))
        badger.set_pen(0)
        badger.rectangle(x, y, 8, 8)
        if mood != i:
            badger.set_pen(15)
            badger.rectangle(x + 1, y + 1, 6, 6)

    badger.update()


def load_config():
    # Open the config file and read out the json
    f = uio.open(CONFIGPATH + CONFIGFILE, mode="r")
    json_data = f.read()
    f.close()
    return ujson.loads(json_data)


config = load_config()


# Open the saved state and read out the saved mood
try:
    # default to 0
    current_moodset = 0
    # defualt to 0
    current_mood = config[CONFIG_FILE_INITIAL_KEY][current_moodset]
    # then override with the read
    mood_composite = read_mood()
    current_moodset = mood_composite[STATEFILE_MOODSET_KEY]
    current_mood = mood_composite[STATEFILE_MOOD_KEY]
except:
    pass

# If the saved moodset is out of bounds for the current moodset, reset it to 0
if current_mood >= len(config[CONFIGFILE_MOODS_KEY][current_moodset]):
    current_mood = 0
    write_mood(current_moodset, current_mood)

while True:
    display_was_changed = False
    now = time.time()
    while time.time() - now < 3:

        if badger.pressed_any():
            badger.led(10)
            now = time.time()
            if badger.pressed(badger2040.BUTTON_DOWN):
                badger.led(64)
                current_mood += 1
                if current_mood >= len(
                    config[CONFIGFILE_MOODS_KEY][current_moodset]
                ):
                    current_mood = 0
                write_mood(current_moodset, current_mood)
                # as fast as we can go without ghosting
                refresh_screen(
                    current_moodset,
                    current_mood,
                    len(config[CONFIGFILE_MOODS_KEY][current_moodset]),
                    badger2040.UPDATE_TURBO,
                )
                display_was_changed = True

            elif badger.pressed(badger2040.BUTTON_UP):
                badger.led(64)
                current_mood -= 1
                if current_mood < 0:
                    current_mood = (
                        len(config[CONFIGFILE_MOODS_KEY][current_moodset]) - 1
                    )
                write_mood(current_moodset, current_mood)
                # as fast as we can go without ghosting
                refresh_screen(
                    current_moodset,
                    current_mood,
                    len(config[CONFIGFILE_MOODS_KEY][current_moodset]),
                    badger2040.UPDATE_TURBO,
                )
                display_was_changed = True
            elif badger.pressed(badger2040.BUTTON_A):
                badger.led(64)
                current_moodset = 0
                # should the current_mood index remain the same if possible?
                current_mood = config[CONFIG_FILE_INITIAL_KEY][current_moodset]
                write_mood(current_moodset, current_mood)
                # as fast as we can go without ghosting
                refresh_screen(
                    current_moodset,
                    current_mood,
                    len(config[CONFIGFILE_MOODS_KEY][current_moodset]),
                    badger2040.UPDATE_FAST,
                )
                # Only need to redisplay if using TURBO
                display_was_changed = False
            elif badger.pressed(badger2040.BUTTON_B):
                badger.led(64)
                if len(config[CONFIGFILE_MOODS_KEY]) > 1:
                    current_moodset = 1
                else:
                    current_moodset = 0
                # should the current_mood index remain the same if possible?
                current_mood = config[CONFIG_FILE_INITIAL_KEY][current_moodset]
                write_mood(current_moodset, current_mood)
                # as fast as we can go without ghosting
                refresh_screen(
                    current_moodset,
                    current_mood,
                    len(config[CONFIGFILE_MOODS_KEY][current_moodset]),
                    badger2040.UPDATE_FAST,
                )
                # Only need to redisplay if using TURBO
                display_was_changed = False
            elif badger.pressed(badger2040.BUTTON_C):
                badger.led(64)
                badger.led(64)
                if len(config[CONFIGFILE_MOODS_KEY]) > 2:
                    current_moodset = 2
                else:
                    current_moodset = 0
                # should the current_mood index remain the same if possible?
                current_mood = config[CONFIG_FILE_INITIAL_KEY][current_moodset]
                write_mood(current_moodset, current_mood)
                # as fast as we can go without ghosting
                refresh_screen(
                    current_moodset,
                    current_mood,
                    len(config[CONFIGFILE_MOODS_KEY][current_moodset]),
                    badger2040.UPDATE_FAST,
                )
                # Only need to redisplay if using TURBO
                display_was_changed = False
            else:
                pass

            badger.led(0)

    # eliminate ghosting if the display was changed but has't changed for 3 seconds
    if display_was_changed:
        refresh_screen(
            current_moodset,
            current_mood,
            len(config[CONFIGFILE_MOODS_KEY][current_moodset]),
            badger2040.UPDATE_FAST,
        )
        display_was_changed = False

    badger2040.turn_off()
