import sys, getopt
from ws4py.client.threadedclient import WebSocketClient


class EchoClient(WebSocketClient):
    def opened(self):
        print('Connection made')

    def closed(self, code, reason):
        print(("Closed down", code, reason))

    def received_message(self, m):
        print("=> %d %s" % (len(m), str(m)))


def main(argv):
    host = 'localhost'
    uri = ''
    port = 8081

    try:
        opts, args = getopt.getopt(argv, "hu:a:p:", ["uri=", "addr=", "port="])
    except getopt.GetoptError:
        print('test.py -u <chat session uri> -a <web server address> -p <web server port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -u <session_uri>')
            sys.exit()
        elif opt in ("-u", "--uri"):
            print('uri : '+arg)
            uri = arg
        elif opt in ("-a", "--addr"):
            print('host : '+arg)
            host = arg
        elif opt in ("-p", "--port"):
            print('port : '+arg)
            port = arg

    ws_uri = 'ws://'+host+':'+str(port)+'/'+uri
    print('Accessing '+ws_uri)
    try:
        ws = EchoClient(ws_uri, protocols=['http-only', 'chat'])
        ws.daemon = False
        ws.connect()
    except KeyboardInterrupt:
        ws.close()


if __name__ == '__main__':
    main(sys.argv[1:])