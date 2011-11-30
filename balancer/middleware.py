from datetime import datetime, timedelta

from django.conf import settings

from balancer import pinning


class PinningSessionMiddleware(object):
    """
    Middleware to support the PinningMixin.  Sets a session variable if
    there was a database write, which will direct that user's subsequent reads
    to the master database.
    """

    def process_request(self, request):
        """
        Set the thread's pinning flag according to the presence of the session
        variable.
        """
        key = getattr(settings, 'MASTER_PINNING_KEY', 'master_db_pinned')
        pinned_until = request.session.get(key, False)

        if pinned_until and pinned_until > datetime.now():
            pinning.set_master_pin()

        if getattr(settings, 'REQUEST_PINNING', False):
            pinning.set_request_pin()

    def process_response(self, request, response):
        """
        If there was a write to the db, set the session variable to enable
        pinning.  If the variable already exists, the time will be reset.
        """
        if pinning.db_was_written():
            seconds = int(getattr(settings, 'MASTER_PINNING_SECONDS', 5))
            pinned_until = datetime.now() + timedelta(seconds=seconds)

            key = getattr(settings, 'MASTER_PINNING_KEY', 'master_db_pinned')
            request.session[key] = pinned_until

            pinning.clear_db_write()
        pinning.unpin_thread()
        return response


class PinningCookieMiddleware(object):
    """
    Middleware to support the PinningMixin.  Sets a cookie if there was a
    database write, which will direct that user's subsequent reads to the
    master database.
    """

    def process_request(self, request):
        """
        Set the thread's pinning flag according to the presence of the cookie.
        """
        key = getattr(settings, 'MASTER_PINNING_KEY', 'master_db_pinned')
        if key in request.COOKIES:
            pinning.set_master_pin()

        if getattr(settings, 'REQUEST_PINNING', False):
            pinning.set_request_pin()

    def process_response(self, request, response):
        """
        If this is a POST request and there was a write to the db, set the
        cookie to enable pinning.  If the cookie already exists, the time will
        be reset.
        """
        key = getattr(settings, 'MASTER_PINNING_KEY', 'master_db_pinned')
        seconds = int(getattr(settings, 'MASTER_PINNING_SECONDS', 5))

        if request.method == 'POST' and pinning.db_was_written():
            response.set_cookie(key, value='y', max_age=seconds)
        pinning.clear_db_write()
        pinning.unpin_thread()
        return response
