from django.conf import settings
from django.test import TestCase

from balancer.routers import WeightedRandomRouter


class WeightedRandomRouterTestCase(TestCase):
        
    def test_random_db_selection(self):
        router = WeightedRandomRouter()
        self.assertIn(router.get_random_db(), settings.DATABASE_POOL.keys())
