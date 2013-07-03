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


from twisted.internet import basic
from twisted.web.http_headers import Headers
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
    def requestHeadReceived(responder, method, path, version, headers):
        """
        @type responder: C{IResponder}
        @param responder: The facet for responding to this request.

        @type method: C{str}
        @type path: C{str}
        @type version: C{str}
        @type headers: C{twisted.web.http_headers.Headers}

        @return: A C{Deferred} which fires to an C{IConsumer} to consume
                 the raw request body bytes.

        Note: Either the caller or callee may determine that a
        request body is complete.  The caller signifies this by
        calling C{IConsumer.unregisterProducer} on the returned
        body consumer.  The callee signifies this by invoking
        C{responder.sendResponseHead}.
        """



class IResponder(Interface):
    """
    I respond to a single HTTP request.
    """
    def sendResponseHead(statusCode, statusMessage, headers):
        """
        @type responseHead: C{ResponseHead}
        @param responseHead: The ResponseHead that resulted from a request.

        @return: A C{Deferred} which fires to an C{IConsumer} to consume
                 the raw response body bytes.
        """



### Utilities for defining HTTP server side request handling:
class RequestHandlerDelegate(object):
    """
    I implement IRequestHandler by delegating to a function.

    Useful as a decorator.
    """
    implements(IRequestHandler)

    def __init__(self, f):
        """
        @type f: a function with the same interface as IRequestHandler.requestHeadReceived
        """
        self.delegate = f

    def requestHeadReceived(self, responder, method, path, version, headers):
        return self.delegate(responder, method, path, version, headers)



class ResponderDelegate(object):
    """
    I implement IResponder by delegating to a function.

    Useful as a decorator.
    """
    implements(IResponder)

    def __init__(self, f):
        """
        @type f: a function with the same interface as IResponder.sendResponseHead
        """
        self.delegate = f

    def sendResponseHead(self, statusCode, statusMessage, headers):
        return self.delegate(statusCode, statusMessage, headers)



