from twisted.trial import unittest
from twisted.internet.defer import succeed
from txhttp import server


class IgnoreBodyTest(unittest.TestCase):
    def test_IgnoreBody(self):
        self.succeeded = False

        def checkResult(nothing):
            self.assertIsNone(nothing)
            self.succeeded = True

        fakeProducer = None

        ib = server.IgnoreBody()
        ib.done.addCallback(checkResult)
        ib.registerProducer(fakeProducer, True)
        ib.write('ignored')
        ib.unregisterProducer()

        return succeed(self.succeeded)
