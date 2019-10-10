#!/usr/bin/python3


class TestLib():
    def test_pytest(self):
        assert True

    def test_unificontroller(self, unificontroller):
        ''' See if the helper fixture works to load charm configs '''
        assert isinstance(unificontroller.charm_config, dict)

    # Include tests for functions in lib_unifi_controller
