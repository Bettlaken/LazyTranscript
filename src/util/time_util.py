def convert_ms(ms, set_unit=False):
    """Converts ms to a nicely readable timestamp

    Args:
      ms:
      set_unit: if set, a "h" for hours will be added (Default value = False)

    Returns:

    """
    unit = "min"

    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    hours = int((ms / (1000 * 60 * 60)) % 24)

    if set_unit and hours > 0:
        unit = "h"

    return ((str(hours).zfill(2) + ":") if hours > 0 else "") + str(minutes).zfill(2) + ":" + str(seconds).zfill(2) + (unit if set_unit else "")

def create_time_string(current, max, unit=True):
    """Creates a time string with the current and max.

    E.g. 03:02/05:43h

    Args:
      current: Current time in ms.
      max: Max time in ms.
      unit: Sets the unit "h" at the end of the timestamp (Default value = True)

    Returns:

    """
    return convert_ms(current, False) + "/" + convert_ms(max, unit)