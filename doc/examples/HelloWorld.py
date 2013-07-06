#! /usr/bin/env python

from cStringIO import StringIO
from twisted.internet import reactor, defer, protocol
# The "client" in the module name is a misnomer for this server-side use:
from twisted.web.client import FileBodyProducer
from txhttp import server


@server.RequestHandlerDelegate
def helloworld(method, path, version, headers, body):

    # The return value, which will fire with a response:
    d = defer.Deferred()

    # Ignore the body:
    ignorer = server.IgnoreBody()
    body.startProducing(ignorer)

    @ignorer.done.addCallback
    def bodyReceived(_):
        # When the request body is completely received, fire our response:
        response = server.Response(
            200, 'ok',
            {'content-type': 'text/plain'},
            FileBodyProducer(StringIO('Hello World!')))

        d.callback(response)

    return d

f = protocol.Factory()
f.protocol = server.HTTPServerProtocol(helloworld)

reactor.listenTCP(8080, f)
reactor.run()

