from lib_unifi_controller import UnificontrollerHelper
from charmhelpers.core import hookenv
from charms.reactive import set_flag, when_not

helper = UnificontrollerHelper()


@when_not('unifi-controller.installed')
def install_unifi_controller():
    # Do your setup here.
    #
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview
    #
    hookenv.status_set('active', '')
    set_flag('unifi-controller.installed')
