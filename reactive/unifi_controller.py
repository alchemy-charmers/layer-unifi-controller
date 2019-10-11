from lib_unifi_controller import UnificontrollerHelper
from charmhelpers.core import hookenv
from charms.reactive import set_flag, when, when_not, clear_flag, endpoint_from_name

helper = UnificontrollerHelper()
HEALTHY = "Unifi installed and configured"


@when("apt.installed.unifi")
def install_unifi():
    """ Install handled by layer:apt """
    hookenv.status_set("active", "")


@when("reverseproxy.ready")
@when_not("reverseproxy.configured")
def setup_proxy():
    """Configure reverse proxy settings when haproxy is related."""
    hookenv.status_set("maintenance", "Applying reverse proxy configuration")
    hookenv.log("Configuring reverse proxy via: {}".format(hookenv.remote_unit()))

    interface = endpoint_from_name("reverseproxy")
    hookenv.log("Using interface: {}".format(interface))
    hookenv.log("Interface: {}".format(dir(interface)))
    helper.configure_proxy(interface)

    hookenv.status_set("active", HEALTHY)
    set_flag("reverseproxy.configured")


@when("reverseproxy.departed")
def remove_proxy():
    """Remove the haproxy configuration when the relation is removed."""
    hookenv.status_set("maintenance", "Removing reverse proxy relation")
    hookenv.log("Removing config for: {}".format(hookenv.remote_unit()))

    hookenv.status_set("active", HEALTHY)
    clear_flag("reverseproxy.configured")
