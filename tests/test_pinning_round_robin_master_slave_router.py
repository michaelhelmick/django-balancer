from balancer.routers import PinningRRMSRouter

from . import BalancerTestCase, PinningRouterTestMixin


class PinningRRMSRouterTestCase(PinningRouterTestMixin, BalancerTestCase):

    def setUp(self):
        super(PinningRRMSRouterTestCase, self).setUp()
        self.router = PinningRRMSRouter()
