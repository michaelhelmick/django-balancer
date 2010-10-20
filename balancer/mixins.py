import threading

from django.conf import settings


_locals = threading.local()


class MasterSlaveMixin(object):
    """
    A mixin that randomly selects from a weighted pool of slave databases
    for read operations, but uses the default database for writes.
    """

    def __init__(self):
        super(MasterSlaveMixin, self).__init__()
        self.master = settings.MASTER_DATABASE

    def db_for_write(self, model, **hints):
        """Send all writes to the master"""
        return self.master

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow any relation between two objects in the slave pool or the master.
        """
        pool = self.pool + [self.master]
        if obj1._state.db in pool and obj2._state.db in pool:
            return True
        return None

    def allow_syncdb(self, db, model):
        """Only allow syncdb on the master"""
        return db == self.master


class PinningMixin(object):
    """
    A mixin that pins reads to the database defined in the MASTER_DATABASE
    setting for a pre-determined period of time after a write.  Requires the
    PinningRouterMiddleware.
    """
    
    def db_for_read(self, model, **hints):
        if PinningMixin.is_pinned():
            return settings.MASTER_DATABASE
        return super(PinningMixin, self).db_for_read(model, **hints)
    
    def db_for_write(self, model, **hints):
        PinningMixin.set_db_write()
        PinningMixin.pin_thread()
        return super(PinningMixin, self).db_for_write(model, **hints)
    
    
    @staticmethod
    def pin_thread():
        """
        Mark this thread as 'pinned', so that future reads will temporarily go
        to the master database for the current user.  
        """
        _locals.pinned = True
    
    @staticmethod
    def unpin_thread():
        """
        Clear the 'pinned' flag so that future reads are distributed normally.
        """
        if getattr(_locals, 'pinned', False):
            del _locals.pinned
    
    @staticmethod
    def is_pinned():
        """Check whether the current thread is pinned."""
        return getattr(_locals, 'pinned', False)
    
    @staticmethod
    def set_db_write():
        """Indicate that the database was written to."""
        _locals.db_write = True
    
    @staticmethod
    def clear_db_write():
        if getattr(_locals, 'db_write', False):
            del _locals.db_write
    
    @staticmethod
    def db_was_written():
        """Check whether a database write was performed."""
        return getattr(_locals, 'db_write', False)