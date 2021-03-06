from ws4py.client.threadedclient import WebSocketClient


class EchoClient(WebSocketClient):
    def opened(self):
        def data_provider():
            for i in range(1, 200, 25):
                yield "#" * i

        self.send(data_provider())

        for i in range(0, 200, 25):
            print(i)
            self.send("*" * i)

    def closed(self, code, reason):
        print(("Closed down", code, reason))

    def received_message(self, m):
        print("=> %d %s" % (len(m), str(m)))
        # if len(m) == 175:
        #     self.close(reason='Bye bye')


def main():
    try:
        ws = EchoClient('ws://localhost:8081/94838d9f5a114f5', protocols=['http-only', 'chat'])
        ws.daemon = False
        ws.connect()
    except KeyboardInterrupt:
        ws.close()


if __name__ == '__main__':
    main()