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


class GatherBodyStringTest(unittest.TestCase):
    def test_GatherBodyString(self):
        testVector = 'some test data'

        self.succeeded = False

        def checkResult(buf):
            self.assertEqual(testVector, buf)
            self.succeeded = True

        fakeProducer = None

        ib = server.GatherBodyString()
        ib.done.addCallback(checkResult)
        ib.registerProducer(fakeProducer, True)
        ib.write(testVector)
        ib.unregisterProducer()

        return succeed(self.succeeded)
