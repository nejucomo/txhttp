from twisted.trial import unittest
from twisted.internet.defer import succeed
from txhttp import server


class RequestHandlerDelegateTest(unittest.TestCase):
    def setUp(self):
        @server.RequestHandlerDelegate
        def echo(*a):
            return a

        self.echo = echo

    def test_providedBy(self):
        self.assertTrue(server.IRequestHandler.providedBy(self.echo))

    def test_call(self):
        args = ('GET', 'fake-url', 'HTTP/1.1', 'fake headers', 'fakeBodyProducer')
        self.assertEqual(args, self.echo.requestReceived(*args))


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
