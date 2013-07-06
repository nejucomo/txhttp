from twisted.trial import unittest
from twisted.internet.defer import succeed
from txhttp import server


class ConsumerTest(unittest.TestCase):
    def _testConsumer(self, cls, input, expected):
        self.succeeded = False

        def checkResult(result):
            self.assertEqual(expected, result)
            self.succeeded = True

        fakeProducer = None

        ib = cls()
        ib.done.addCallback(checkResult)
        ib.registerProducer(fakeProducer, True)
        ib.write(input)
        ib.unregisterProducer()

        return succeed(self.succeeded)

    def test_IgnoreBody(self):
        return self._testConsumer(server.IgnoreBody, 'blah blah', None)

    def test_GatherBodyString(self):
        testVector = 'some test data'
        return self._testConsumer(server.GatherBodyString, testVector, testVector)
