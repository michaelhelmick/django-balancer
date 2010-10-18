from django.conf import settings
from django.test import TestCase

from balancer.routers import WeightedRandomRouter, WeightedMasterSlaveRouter


class BalancerTests(TestCase):
    
    def setUp(self):
        self.original_databases = settings.DATABASES
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            },
            'other': {
                'ENGINE': 'django.db.backends.sqlite3',
                'TEST_NAME': 'other_db',
            },
            'utility': {
                'ENGINE': 'django.db.backends.sqlite3',
                'TEST_NAME': 'utility_db',
            }
        }
        
        self.original_master = getattr(settings, 'MASTER_DATABASE', None)
        settings.MASTER_DATABASE = 'default'
        
        self.original_pool = getattr(settings, 'DATABASE_POOL', None)
        settings.DATABASE_POOL = {
            'default': 1,
            'other': 2,
        }
        
        class MockObj(object):
            class _state:
                db = None
        
        self.obj1 = MockObj()
        self.obj2 = MockObj()
    
    def tearDown(self):
        settings.DATABASES = self.original_databases
        settings.MASTER_DATABASE = self.original_master
        settings.DATABASE_POOL = self.original_pool


class WeightedRandomRouterTestCase(BalancerTests):
    
    def setUp(self):
        super(WeightedRandomRouterTestCase, self).setUp()
        self.router = WeightedRandomRouter()
                
        
    def test_random_db_selection(self):
        """Simple test to make sure that random database selection works."""
        for i in range(10):
            self.assertIn(self.router.get_random_db(),
                          settings.DATABASE_POOL.keys())
    
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

    def test_relations(self):
        """Relations should only be allowed for databases in the pool."""
        self.obj1._state.db = 'default'
        self.obj2._state.db = 'other'
        self.assertTrue(self.router.allow_relation(self.obj1, self.obj2))
        
        self.obj1._state.db = 'other'
        self.obj2._state.db = 'utility'
        self.assertFalse(self.router.allow_relation(self.obj1, self.obj2))

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
