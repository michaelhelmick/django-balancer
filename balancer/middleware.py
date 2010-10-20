from datetime import datetime, timedelta

from django.conf import settings

from balancer.routers import PinningRouterMixin


# The name of the session variable or cookie used by the middleware
PINNING_KEY = getattr(settings, 'MASTER_PINNING_KEY', 'master_db_pinned')

# The number of seconds to direct reads to the master database after a write
PINNING_SECONDS = int(getattr(settings, 'MASTER_PINNING_SECONDS', 5))


class PinningSessionMiddleware(object):
    """
    Middleware to support the PinningRouterMixin.  Sets a session variable if
    there was a database write, which will direct that user's subsequent reads
    to the master database.
    """
    
    def process_request(self, request):
        """
        Set the thread's pinning flag according to the presence of the session
        variable.
        """
        pinned_until = request.session.get(PINNING_KEY, False)
        if pinned_until and pinned_until > datetime.now():
            PinningRouterMixin.pin_thread()
        
    def process_response(self, request, response):
        """
        If there was a write to the db, set the session variable to enable
        pinning.  If the variable already exists, the time will be reset.
        """
        if PinningRouterMixin.db_was_written():
            pinned_until = datetime.now() + timedelta(seconds=PINNING_SECONDS)
            request.session[PINNING_KEY] = pinned_until
            PinningRouterMixin.clear_db_write()
        PinningRouterMixin.unpin_thread()
        return response


class PinningCookieMiddleware(object):
    """
    Middleware to support the PinningRouterMixin.  Sets a cookie if there was a
    database write, which will direct that user's subsequent reads to the
    master database.
    """
    
    def process_request(self, request):
        """
        Set the thread's pinning flag according to the presence of the cookie.
        """
        if PINNING_KEY in request.COOKIES:
            PinningRouterMixin.pin_thread()
    
    def process_response(self, request, response):
        """
        If there was a write to the db, set the cookie to enable pinning.  If
        the cookie already exists, the time will be reset.
        """
        if PinningRouterMixin.db_was_written():
            response.set_cookie(PINNING_KEY, value='y',
                                max_age=PINNING_SECONDS)
            PinningRouterMixin.clear_db_write()
        PinningRouterMixin.unpin_thread()
        return response
