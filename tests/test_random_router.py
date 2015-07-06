from django.conf import settings

from balancer.routers import RandomRouter

from . import BalancerTestCase


class RandomRouterTestCase(BalancerTestCase):

    def setUp(self):
        super(RandomRouterTestCase, self).setUp()
        self.router = RandomRouter()

    def test_random_db_selection(self):
        """Simple test to make sure that random database selection works."""
        for i in range(10):
            self.assertTrue(self.router.get_random_db() in
                            settings.DATABASE_POOL.keys(),
                            "The database selected is not in the pool.")

    def test_relations(self):
        """Relations should only be allowed for databases in the pool."""
        self.obj1._state.db = 'default'
        self.obj2._state.db = 'other'
        self.assertTrue(self.router.allow_relation(self.obj1, self.obj2))

        self.obj1._state.db = 'other'
        self.obj2._state.db = 'utility'
        self.assertFalse(self.router.allow_relation(self.obj1, self.obj2))
