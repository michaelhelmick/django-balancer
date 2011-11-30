import threading

_locals = threading.local()


# Operations

def pin_thread_to(db):
    """
    Mark this thread as 'pinned', so that future reads will temporarily go to
    the specified database for the current user.
    """
    _locals.pinned = db


def unpin_thread():
    """
    Clear the 'pinned' flag so that future reads are distributed normally.
    """
    if hasattr(_locals, 'pinned'):
        del _locals.pinned


def get_pinned_db():
    """If pinned, retrieve the db that the current thread is pinned to."""
    return getattr(_locals, 'pinned', None)


# Flags

def set_db_write():
    """Indicate that the database was written to."""
    _locals.db_write = True


def clear_db_write():
    if hasattr(_locals, 'db_write'):
        del _locals.db_write


def db_was_written():
    """Check whether a database write was performed."""
    return getattr(_locals, 'db_write', False)


def set_master_pin():
    """
    Indicate that the thread should be pinned to the master database.
    """
    _locals.master_pin = True


def clear_master_pin():
    if hasattr(_locals, 'master_pin'):
        del _locals.master_pin


def pinned_to_master():
    return getattr(_locals, 'master_pin', False)


def set_request_pin():
    """
    Indicate that the router should select the database normally, but then pin
    the thread to the selected database so that future reads will go there.
    """
    _locals.request_pin = True


def clear_request_pin():
    if hasattr(_locals, 'request_pin'):
        del _locals.request_pin


def request_pinned():
    return getattr(_locals, 'request_pin', False)
