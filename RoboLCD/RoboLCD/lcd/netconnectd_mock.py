import socket
from kivy.logger import Logger


class NetconnectdClient():
    def hostname(self):
        return socket.gethostname() + ".local"

    def get_ip(self):
        return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

    def _get_wifi_list(self, force=False):
        result = []
        result.append(dict(ssid="MockSSID1", address=None, quality=-40, encrypted=True))
        result.append(dict(ssid="MockSSID2", address=None, quality=-50, encrypted=True))
        result.append(dict(ssid="MockSSID3", address=None, quality=-60, encrypted=True))
        result.append(dict(ssid="MockSSID4", address=None, quality=-70, encrypted=True))
        return result

    def _get_status(self):
        status = {
                "connections": {
                    "wifi" : True,
                    "ap" : "AP01",
                    "wired" : True
                },
                "wifi": {
                    "current_ssid" : "MockSSIDCurrent"
                }
            }
        return status

    def command(self, command, data):
        if command == "list_wifi":
            return self._get_wifi_list(force=True)
        return
