import socket

from charmhelpers.core import hookenv


class UnificontrollerHelper:
    def __init__(self):
        self.charm_config = hookenv.config()

    def action_function(self):
        """ An example function for calling from an action """
        return

    def configure_proxy(self, proxy):
        """Configure Unificontroller for operation behind a reverse proxy."""
        proxy_config = [
            {
                "mode": "http",
                "external_port": self.charm_config["proxy-external-port"],
                "internal_host": socket.getfqdn(),
                "internal_port": 8443,
                "ssl": True,
                "ssl-verify": False,
                "subdomain": self.charm_config["proxy-subdomain"],
                "acl-local": self.charm_config["proxy-local"],
            }
        ]
        proxy.configure(proxy_config)
