from django.conf import settings

from balancer.routers import RoundRobinRouter

from . import BalancerTestCase


class RoundRobinRouterTestCase(BalancerTestCase):

    def setUp(self):
        super(RoundRobinRouterTestCase, self).setUp()
        settings.DATABASE_POOL = ['default', 'other', 'utility']
        self.router = RoundRobinRouter()

    def test_sequential_db_selection(self):
        """Databases should cycle in order."""
        for i in range(10):
            self.assertEqual(self.router.get_next_db(), self.router.pool[0])
            self.assertEqual(self.router.get_next_db(), self.router.pool[1])
            self.assertEqual(self.router.get_next_db(), self.router.pool[2])
