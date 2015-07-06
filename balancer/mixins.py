from balancer import pinning


class MasterSlaveMixin(object):
    """
    A mixin that randomly selects from a weighted pool of slave databases
    for read operations, but uses the default database for writes.
    """

    def __init__(self):
        super(MasterSlaveMixin, self).__init__()
        from django.conf import settings
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

    def allow_migrate(self, db, model):
        """Only allow syncdb on the master"""
        return db == self.master


class PinningMixin(object):
    """
    A mixin that pins reads to the database defined in the MASTER_DATABASE
    setting for a pre-determined period of time after a write.  Requires the
    PinningRouterMiddleware.
    """

    def db_for_read(self, model, **hints):
        from django.conf import settings
        if pinning.thread_is_pinned():
            return settings.MASTER_DATABASE
        return super(PinningMixin, self).db_for_read(model, **hints)

    def db_for_write(self, model, **hints):
        pinning.set_db_write()
        pinning.pin_thread()
        return super(PinningMixin, self).db_for_write(model, **hints)
