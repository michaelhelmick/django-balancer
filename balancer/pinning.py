import threading

_locals = threading.local()


def pin_thread():
    """
    Mark this thread as 'pinned', so that future reads will temporarily go
    to the master database for the current user.  
    """
    _locals.pinned = True


def unpin_thread():
    """
    Clear the 'pinned' flag so that future reads are distributed normally.
    """
    if getattr(_locals, 'pinned', False):
        del _locals.pinned


def thread_is_pinned():
    """Check whether the current thread is pinned."""
    return getattr(_locals, 'pinned', False)


def set_db_write():
    """Indicate that the database was written to."""
    _locals.db_write = True


def clear_db_write():
    if getattr(_locals, 'db_write', False):
        del _locals.db_write


def db_was_written():
    """Check whether a database write was performed."""
    return getattr(_locals, 'db_write', False)
