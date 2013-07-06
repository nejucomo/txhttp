"""
An alternative HTTP server stack for twisted.

This differs from C{twisted.web.http} in these ways:

1. It is only server side.  (There may be C{txhttp.client} in the future.)

2. It is a minimal layer separate from request processing, so it lacks features such as:
  - Request body processing / parsing, such as:
    - C{twisted.web.http.Request.args} from POST bodies.
    - Transfer-Encoding support.
  - built in timeout support.
  - log file management.

3. It uses a "staged" interface rather than monolithic classes.
"""

# TODO: Persistent connections, pipelining, and 100-continue as per
# RFC2616 section 8:
# http://www.w3.org/Protocols/rfc2616/rfc2616-sec8.html


from abc import ABCMeta, abstractmethod
from cStringIO import StringIO
from twisted.internet import defer
from twisted.protocols import basic
from twisted.internet.interfaces import IConsumer
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from zope.interface import Interface, implements



class HTTPServerProtocol(basic.LineReceiver):

    def __init__(self, handleRequest):
        """
        @type handleRequest: C{IRequestHandler}
        @param handleRequest: The request handler for all requests.
        """
        self._handleRequest = IRequestHandler(handleRequest)

        # Note: Only self.lineReceived should touch this:
        self._pendingHead = None


    def lineReceived(self, line):

        if self._pendingHead is None:
            try:
                [method, urlpath, version] = line.split()
            except ValueError:
                self._send400()
                return

            headers = Headers()

            self._pendingHead = (method, urlpath, version, headers)

        elif line == '':
            (method, urlpath, version, headers) = self._pendingHead
            self._pendingHead = None

            self._dispatchRequestHead(method, urlpath, version, headers)

        else:
            headers = self._pendingHead[3]
            self._headerLineReceived(headers, line)


    def _headerLineReceived(self, headers, line):
        # BUG: This does not handle multiline headers; see RFC 822 and
        # twisted.web.http.HTTPChannel.lineReceived.

        header, data = line.split(':', 1)
        header = header.lower()
        data = data.strip()

    def _disaptchRequestHead(self, method, urlpath, version, headers):
        raise NotImplementedError(repr((self._dispatchRequestHead, method, urlpath, version, headers)))



### Interfaces for HTTP serverside request handling:
class IRequestHandler(Interface):
    """
    I handle HTTP requests.
    """
    def requestReceived(method, url, version, headers, body):
        """
        @type method: C{bytes}
        @type url: C{urlparse.ParseResult}
        @type version: C{bytes}
        @type headers: C{twisted.web.http_headers.Headers}
        @type body: C{IBodyProducer}

        @return: A C{Deferred} C{Response}.
        """



class Response(object):
    def __init__(self, code, status, headers, bodyProducer):
        if not isinstance(headers, Headers):
            raise TypeError('Expected Headers instance; found %r' % (headers,))

        self.code = code
        self.status = status
        self.headers = headers
        self.bodyProducer = IBodyProducer(bodyProducer)



### Utilities for defining HTTP server side request handling:
class RequestHandlerDelegate(object):
    """
    I implement IRequestHandler by delegating to a function.

    Useful as a decorator.
    """
    implements(IRequestHandler)

    def __init__(self, f):
        """
        @type f: a function with the same interface as IRequestHandler.requestReceived
        """
        self.delegate = f

    def requestReceived(self, method, path, version, headers, body):
        return self.delegate(method, path, version, headers, body)


### Common body consumers:
class GatherConsumer(object):
    """
    I am an IConsumer which gathers the input and fires done with some result.
    """
    __metaclass__ = ABCMeta
    implements(IConsumer)

    def __init__(self):
        self.done = defer.Deferred()

    def registerProducer(self, producer, streaming):
        assert streaming == True, 'Only IPushProducer is supported, not %r' % (producer,)

    def unregisterProducer(self):
        self.done.callback(self._gatherResult())

    def write(self, data):
        pass

    @abstractmethod
    def _gatherResult(self):
        """Return the result of consuming the input."""


class IgnoreBody(GatherConsumer):
    def _gatherResult(self):
        return None


class GatherBodyString(GatherConsumer):
    def __init__(self):
        GatherConsumer.__init__(self)
        self._f = StringIO()

    def write(self, data):
        self._f.write(data)

    def _gatherResult(self):
        return self._f.getvalue()
