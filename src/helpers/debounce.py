import time
import threading
from functools import wraps

def debounce(wait):
    """
    A simple debouncer largely based on MrSpider's implementation at:
    https://gist.github.com/walkermatt/2871026?permalink_comment_id=2844099#gistcomment-2844099.
    It seems to massively help with the problems caused when the GUI is abused by a user.
    """

    def decorator(fn):
        timers = {}  # Dictionary to store timers per function instance

        @wraps(fn)  # Preserve function metadata
        def debounced(*args, **kwargs):
            instance = args[0]  # Get the instance (e.g., self in a class method)

            def call_it():
                timers[instance] = None
                fn(*args, **kwargs)

            # Cancel previous timer if it exists
            if instance in timers and timers[instance] is not None:
                timers[instance].cancel()

            # Set new timer
            timers[instance] = threading.Timer(wait, call_it)
            timers[instance].start()

        return debounced

    return decorator
