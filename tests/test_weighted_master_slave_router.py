from balancer.routers import WeightedMasterSlaveRouter

from . import BalancerTestCase, MasterSlaveTestMixin


class WMSRouterTestCase(MasterSlaveTestMixin, BalancerTestCase):
    """Tests for the WeightedMasterSlaveRouter."""

    def setUp(self):
        super(WMSRouterTestCase, self).setUp()
        self.router = WeightedMasterSlaveRouter()
