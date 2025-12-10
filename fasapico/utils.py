import sys
import ubinascii
from machine import Timer

# ==========================================
# Logging Utilities
# ==========================================

# Levels
LOG_NONE = 0
LOG_ERROR = 1
LOG_WARN = 2
LOG_INFO = 3
LOG_DEBUG = 4

# Current level (default: INFO)
CURRENT_LOG_LEVEL = LOG_INFO

def enable_logging_types(level):
    global CURRENT_LOG_LEVEL
    CURRENT_LOG_LEVEL = level

def log(level, tag, msg):
    if level <= CURRENT_LOG_LEVEL:
        print(f"[{tag}] {msg}")

def error(msg):
    if LOG_ERROR <= CURRENT_LOG_LEVEL:
        print(f"[ERROR] {msg}")

def warn(msg):
    if LOG_WARN <= CURRENT_LOG_LEVEL:
        print(f"[WARN] {msg}")

def info(msg):
    if LOG_INFO <= CURRENT_LOG_LEVEL:
        print(f"[INFO] {msg}")

def debug(msg):
    if LOG_DEBUG <= CURRENT_LOG_LEVEL:
        print(f"[DEBUG] {msg}")

def exception(e):
    if LOG_ERROR <= CURRENT_LOG_LEVEL:
        # print_exception is not available in standard python but microPython often has it in sys or use basic print
        print(f"[EXCEPTION] {e}")


# ==========================================
# General Utilities
# ==========================================

# scale a value x from one range [in_min, in_max] to a new range [out_min, out_max]
def scale(x, in_min, in_max, out_min, out_max):
    """ Maps two ranges together """
    try:
        if (in_max - in_min) == 0:
            return out_min
        return (x-in_min) * (out_max-out_min) / (in_max - in_min) + out_min
    except ZeroDivisionError:
        return out_min

# scale a value x from one range [in_min, in_max] to a new range [out_min, out_max], return an integer
def scale_to_int(x, in_min, in_max, out_min, out_max):
    return int(scale(x, in_min, in_max, out_min, out_max))

def decode_bytes(data):
    """
    Décode les bytes en string utf-8 de manière sûre.
    Retourne la donnée brute ou string.
    """
    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except:
            return data
    return data
