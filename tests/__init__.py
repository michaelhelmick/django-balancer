#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta


from django.conf import settings
from django.test import TestCase

import balancer
from balancer import pinning
from balancer.middleware import (
    PINNING_KEY, PINNING_SECONDS,
    PinningSessionMiddleware,
    PinningCookieMiddleware
)
from balancer.routers import WeightedRandomRouter


class BalancerTestCase(TestCase):

    def setUp(self):
        self.original_databases = settings.DATABASES
        settings.DATABASES = balancer.TEST_DATABASES

        self.original_master = getattr(settings, 'MASTER_DATABASE', None)
        settings.MASTER_DATABASE = balancer.TEST_MASTER_DATABASE

        self.original_pool = getattr(settings, 'DATABASE_POOL', None)
        settings.DATABASE_POOL = balancer.TEST_DATABASE_POOL

        class MockObj(object):
            class _state:
                db = None

        self.obj1 = MockObj()
        self.obj2 = MockObj()

    def tearDown(self):
        settings.DATABASES = self.original_databases
        settings.MASTER_DATABASE = self.original_master
        settings.DATABASE_POOL = self.original_pool


class MasterSlaveTestMixin(object):
    """A mixin for testing routers that use the MasterSlaveMixin."""

    def test_writes(self):
        """Writes should always go to master."""
        self.assertEqual(self.router.db_for_write(self.obj1), 'default')

    def test_relations(self):
        """
        Relations should be allowed for databases in the pool and the master.
        """
        settings.DATABASE_POOL = {
            'other': 1,
            'utility': 1,
        }
        self.router = WeightedRandomRouter()

        # Even though default isn't in the database pool, it is the master so
        # the relation should be allowed.
        self.obj1._state.db = 'default'
        self.obj2._state.db = 'other'
        self.assertTrue(self.router.allow_relation(self.obj1, self.obj2))


class PinningRouterTestMixin(object):
    """A mixin for testing routers that use the pinning mixin."""

    def setUp(self):
        super(PinningRouterTestMixin, self).setUp()

        class MockRequest(object):
            COOKIES = []
            method = 'GET'
            session = {}


        self.mock_request = MockRequest()

        class MockResponse(object):
            cookie = None

            def set_cookie(self, key, value, max_age):
                self.cookie = key

        self.mock_response = MockResponse()

    def test_pinning(self):
        # Check to make sure the 'other' database shows in in reads first
        success = False
        for i in range(100):
            db = self.router.db_for_read(self.obj1)
            if db == 'other':
                success = True
                break
        self.assertTrue(success, "The 'other' database was not offered.")

        # Simulate a write
        self.router.db_for_write(self.obj1)

        # Check to make sure that only the master database shows up in reads,
        # since the thread should now be pinned
        success = True
        for i in range(100):
            db = self.router.db_for_read(self.obj1)
            if db == 'other':
                success = False
                break
        self.assertTrue(success, "The 'other' database was offered in error.")

        pinning.unpin_thread()
        pinning.clear_db_write()

    def test_middleware(self):
        for middleware, vehicle in [(PinningSessionMiddleware(), 'session'),
                                    (PinningCookieMiddleware(), 'cookie')]:
            # The first request shouldn't pin the database
            middleware.process_request(self.mock_request)
            self.assertFalse(pinning.thread_is_pinned())

            # A simulated write also shouldn't, if the request isn't a POST
            pinning.set_db_write()
            middleware.process_request(self.mock_request)
            self.assertFalse(pinning.thread_is_pinned())

            # This response should set the session variable and clear the pin
            pinning.set_db_write()
            self.mock_request.method = 'POST'
            response = middleware.process_response(self.mock_request,
                                                   self.mock_response)
            self.assertFalse(pinning.thread_is_pinned())
            self.assertFalse(pinning.db_was_written())
            if vehicle == 'session':
                self.assertTrue(
                    self.mock_request.session.get(PINNING_KEY, False)
                )
            else:
                self.assertEqual(response.cookie, PINNING_KEY)
                self.mock_request.COOKIES = [response.cookie]

            # The subsequent request should then pin the database
            middleware.process_request(self.mock_request)
            self.assertTrue(pinning.thread_is_pinned())

            pinning.unpin_thread()

            if vehicle == 'session':
                # After the pinning period has expired, the request should no
                # longer pin the thread
                exp = timedelta(seconds=PINNING_SECONDS - 5)
                self.mock_request.session[PINNING_KEY] = datetime.now() - exp
                middleware.process_request(self.mock_request)
                self.assertFalse(pinning.thread_is_pinned())

                pinning.unpin_thread()
