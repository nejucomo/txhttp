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
#from twisted.web.http_headers import Headers
from zope.interface import Interface, Attribute



class HTTPServerProtocol(basic.LineReceiver):

    def __init__(self, handleRequest):
        """
        @type handleRequest: C{IRequestHandler}
        @param handleRequest: The request handler for all requests.
        """
        self._handleRequest = IRequestHandler(handleRequest)





class IRequestHandler(Interface):
    """
    Implementations respond to HTTP requests.
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
    Implementations are used to respond to a single HTTP request.
    """
    def sendResponseHead(statusCode, statusMessage, headers):
        """
        @type responseHead: C{ResponseHead}
        @param responseHead: The ResponseHead that resulted from a request.

        @return: A C{Deferred} which fires to an C{IConsumer} to consume
                 the raw response body bytes.
        """
