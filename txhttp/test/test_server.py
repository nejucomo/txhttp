from twisted.trial import unittest
from twisted.internet.defer import succeed
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from txhttp import server
from zope.interface import implements


class ResponseTests(unittest.TestCase):

    class FakeBodyProducer(object):
        implements(IBodyProducer)


    def test_validResponseConstruction(self):
        # Succeeds if no exception is raised:
        server.Response(200, 'ok', Headers(), self.FakeBodyProducer())

    def test_invalidResponseConstructionWithNonHeaders(self):
        # This may be a common bug when "headers" is misinterpreted to
        # be a dict:
        self.assertRaises(
            TypeError,
            server.Response, 200, 'ok', {}, self.FakeBodyProducer())

    def test_invalidResponseConstructionWithNonProducer(self):
        # Succeeds if no exception is raised:
        self.assertRaises(
            TypeError,
            server.Response, 200, 'ok', Headers(),
            'a banana does not provide IBodyProducer')


class RequestHandlerDelegateTests(unittest.TestCase):
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


class ConsumerTests(unittest.TestCase):
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
