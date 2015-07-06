from balancer.routers import RoundRobinMasterSlaveRouter

from . import BalancerTestCase, MasterSlaveTestMixin


class RRMSRouterTestCase(MasterSlaveTestMixin, BalancerTestCase):
    """Tests for the RoundRobinMasterSlaveRouter."""

    def setUp(self):
        super(RRMSRouterTestCase, self).setUp()
        self.router = RoundRobinMasterSlaveRouter()
