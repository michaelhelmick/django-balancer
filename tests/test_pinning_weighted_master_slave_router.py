from balancer.routers import PinningWMSRouter

from . import BalancerTestCase, PinningRouterTestMixin


class PinningWMSRouterTestCase(PinningRouterTestMixin, BalancerTestCase):

    def setUp(self):
        super(PinningWMSRouterTestCase, self).setUp()
        self.router = PinningWMSRouter()
