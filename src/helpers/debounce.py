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
        @wraps(fn) # Without wrapping the deboucer breaks in Nuitka
        def debounced(*args, **kwargs):
            def call_it():
                debounced._timer = None
                fn(*args, **kwargs)

            if debounced._timer is not None:
                debounced._timer.cancel()

            debounced._timer = threading.Timer(wait, call_it)
            debounced._timer.start()

        debounced._timer = None
        return debounced

    return decorator
