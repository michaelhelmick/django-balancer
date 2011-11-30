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


class PinningMixin(object):
    """
    A mixin that pins actions to a specific database when requested.  It
    requires the MasterSlaveMixin above.
    """

    def db_for_read(self, model, **hints):
        # If the thread should be pinned to master, pin it and clear the flag.
        if pinning.pinned_to_master():
            pinning.pin_thread_to(self.master)
            pinning.clear_master_pin()

        db = pinning.get_pinned_db()
        if db is None:
            db = super(PinningMixin, self).db_for_read(model, **hints)

            # If the request should be pinned to the selected database, pin it
            # and clear the flag.
            if pinning.request_pinned():
                pinning.pin_thread_to(db)
                pinning.clear_request_pin()

        return db

    def db_for_write(self, model, **hints):
        pinning.set_db_write()
        pinning.pin_thread_to(self.master)
        db = super(PinningMixin, self).db_for_write(model, **hints)
