import unittest
from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase

import balancer
from balancer.routers import RandomRouter, WeightedRandomRouter, \
                             WeightedMasterSlaveRouter, \
                             PinningMasterSlaveRouter
from balancer.middleware import PINNING_KEY, PINNING_SECONDS, \
                                PinningSessionMiddleware, \
                                PinningCookieMiddleware

class BalancerTests(TestCase):

    def setUp(self):
        if not settings.ROOT_URLCONF == 'test_project.urls':
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
        if not settings.ROOT_URLCONF == 'test_project.urls':
            settings.DATABASES = self.original_databases
            settings.MASTER_DATABASE = self.original_master
            settings.DATABASE_POOL = self.original_pool


class RandomRouterTestCase(BalancerTests):

    def setUp(self):
        super(RandomRouterTestCase, self).setUp()
        self.router = RandomRouter()

    def test_random_db_selection(self):
        """Simple test to make sure that random database selection works."""
        for i in range(10):
            self.assertIn(self.router.get_random_db(),
                          settings.DATABASE_POOL.keys())

    def test_relations(self):
        """Relations should only be allowed for databases in the pool."""
        self.obj1._state.db = 'default'
        self.obj2._state.db = 'other'
        self.assertTrue(self.router.allow_relation(self.obj1, self.obj2))

        self.obj1._state.db = 'other'
        self.obj2._state.db = 'utility'
        self.assertFalse(self.router.allow_relation(self.obj1, self.obj2))


class WeightedRandomRouterTestCase(BalancerTests):

    def setUp(self):
        super(WeightedRandomRouterTestCase, self).setUp()
        self.router = WeightedRandomRouter()

    def test_weighted_db_selection(self):
        """
        Make sure that the weights are being applied correctly by checking to
        see if the rate that 'default' is selected is within 0.15 of the target
        rate.
        """
        def check_rate(target):
            hits = {'default': 0, 'other': 0}
            for i in range(1000):
                hits[self.router.get_random_db()] += 1
            rate = round(float(hits['default']) / float(hits['other']), 2)

            self.assertTrue((target - 0.15) <= rate <= (target + 0.15),
                            "The 'default' rate of %s was not close enough to "
                            "the target rate." % rate)

        # The initial target rate is 0.5, because 'default' has a weight of 1
        # and 'other' has a rate of 2 - 'default' should be selected roughly
        # half as much as 'other'.
        check_rate(target=0.5)

        original_weights = settings.DATABASE_POOL
        settings.DATABASE_POOL = {
            'default': 1,
            'other': 4,
        }
        # Reinitialize the router with new weights
        self.router = WeightedRandomRouter()
        check_rate(target=0.25)

        settings.DATABASE_POOL = original_weights


class WeightedMasterSlaveRouterTestCase(BalancerTests):

    def setUp(self):
        super(WeightedMasterSlaveRouterTestCase, self).setUp()
        self.router = WeightedMasterSlaveRouter()

    def test_writes(self):
        """Writes should always go to master."""
        self.assertEqual(self.router.db_for_write(self.obj1), 'default')

    def test_relations(self):
        """
        Relations should be allowed for databases in the pool and the master.
        """
        original_weights = settings.DATABASE_POOL
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

        settings.DATABASE_POOL = original_weights


class PinningMasterSlaveRouterTestCase(BalancerTests):
    
    def setUp(self):
        super(PinningMasterSlaveRouterTestCase, self).setUp()
        self.router = PinningMasterSlaveRouter()
        
        class MockRequest(object):
            session = {}
            COOKIES = []
        
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
        
        PinningMasterSlaveRouter.unpin_thread()
        PinningMasterSlaveRouter.clear_db_write()
    
    def test_middleware(self):
        for middleware, vehicle in [(PinningSessionMiddleware(), 'session'),
                                    (PinningCookieMiddleware(), 'cookie')]:
            # The first request shouldn't pin the database
            middleware.process_request(self.mock_request)
            self.assertFalse(PinningMasterSlaveRouter.is_pinned())
            
            # A simulated write should, however
            PinningMasterSlaveRouter.set_db_write()
            
            # The response should set the session variable and clear the locals
            response = middleware.process_response(self.mock_request,
                                                   self.mock_response)
            self.assertFalse(PinningMasterSlaveRouter.is_pinned())
            self.assertFalse(PinningMasterSlaveRouter.db_was_written())
            if vehicle == 'session':
                self.assertTrue(
                    self.mock_request.session.get(PINNING_KEY, False)
                )
            else:
                self.assertEqual(response.cookie, PINNING_KEY)
                self.mock_request.COOKIES = [response.cookie]
            
            # The subsequent request should then pin the database
            middleware.process_request(self.mock_request)
            self.assertTrue(PinningMasterSlaveRouter.is_pinned())
            
            PinningMasterSlaveRouter.unpin_thread()
            
            if vehicle == 'session':
                # After the pinning period has expired, the request should no
                # longer pin the thread
                exp = timedelta(seconds=PINNING_SECONDS - 5)
                self.mock_request.session[PINNING_KEY] = datetime.now() - exp
                middleware.process_request(self.mock_request)
                self.assertFalse(PinningMasterSlaveRouter.is_pinned())
                
                PinningMasterSlaveRouter.unpin_thread()
