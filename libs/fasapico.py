# map (scale) a value x from one range [in_min, in_max] to a new range [out_min, out_max]
def map(x, in_min, in_max, out_min, out_max):
    """ Maps two ranges together """
    return (x-in_min) * (out_max-out_min) / (in_max - in_min) + out_min