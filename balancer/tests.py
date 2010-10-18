from django.conf import settings
from django.test import TestCase

from balancer.routers import WeightedRandomRouter


class WeightedRandomRouterTestCase(TestCase):
    
    def setUp(self):
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
