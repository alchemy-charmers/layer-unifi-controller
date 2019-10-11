import os
import stat
import subprocess

import pytest

# import urllib.request

# Treat all tests as coroutines
pytestmark = pytest.mark.asyncio

juju_repository = os.getenv("JUJU_REPOSITORY", ".").rstrip("/")
series = [
    "xenial",
    "bionic",
    # pytest.param("cosmic", marks=pytest.mark.xfail(reason="canary")),
]
sources = [
    ("local", "{}/builds/unifi-controller".format(juju_repository)),
    # ('jujucharms', 'cs:...'),
]


# Custom fixtures
@pytest.fixture(params=series)
def series(request):
    return request.param


@pytest.fixture(params=sources, ids=[s[0] for s in sources])
def source(request):
    return request.param


@pytest.fixture
async def app(model, series, source):
    app_name = "unifi-controller-{}-{}".format(series, source[0])
    return await model._wait_for_new("application", app_name)


@pytest.mark.deploy
async def test_unificontroller_deploy(model, series, source, request):
    # Starts a deploy for each series
    # Using subprocess b/c libjuju fails with JAAS
    # https://github.com/juju/python-libjuju/issues/221
    application_name = "unifi-controller-{}-{}".format(series, source[0])

    cmd = [
        "juju",
        "deploy",
        source[1],
        "-m",
        model.info.name,
        "--series",
        series,
        application_name,
    ]
    if request.node.get_closest_marker("xfail"):
        # If series is 'xfail' force install to allow testing against versions not in
        # metadata.yaml
        cmd.append("--force")
    subprocess.check_call(cmd)


@pytest.mark.deploy
async def test_haproxy_deploy(model):
    await model.deploy("cs:~pirate-charmers/haproxy", series="xenial")


@pytest.mark.deploy
@pytest.mark.timeout(300)
async def test_charm_upgrade(model, app):
    if app.name.endswith("local"):
        pytest.skip()  # No need to upgrade local deploy
    unit = app.units[0]
    await model.block_until(lambda: unit.agent_status == "idle")
    subprocess.check_call(
        [
            "juju",
            "upgrade-charm",
            "--switch={}".format(sources[0][1]),
            "-m",
            model.info.name,
            app.name,
        ]
    )
    await model.block_until(lambda: unit.agent_status == "executing")


@pytest.mark.deploy
@pytest.mark.timeout(300)
async def test_unificontroller_status(model, app):
    # Verifies status for all deployed series of the charm
    await model.block_until(lambda: app.status == "active")
    unit = app.units[0]
    await model.block_until(lambda: unit.agent_status == "idle")


# Tests
async def test_example_action(app):
    unit = app.units[0]
    action = await unit.run_action("example-action")
    action = await action.wait()
    assert action.status == "completed"


async def test_run_command(app, jujutools):
    unit = app.units[0]
    cmd = "hostname --all-ip-addresses"
    results = await jujutools.run_command(cmd, unit)
    assert results["Code"] == "0"
    assert unit.public_address in results["Stdout"]


async def test_file_stat(app, jujutools):
    unit = app.units[0]
    path = "/var/lib/juju/agents/unit-{}/charm/metadata.yaml".format(
        unit.entity_id.replace("/", "-")
    )
    fstat = await jujutools.file_stat(path, unit)
    assert stat.filemode(fstat.st_mode) == "-rw-r--r--"
    assert fstat.st_uid == 0
    assert fstat.st_gid == 0


@pytest.mark.timeout(45)
async def test_add_relation(model, app):
    haproxy = model.applications["haproxy"]
    unifi = app
    subdomain = app.name.split("-", 2)[2]
    config = {"proxy-external-port": 80, "proxy-subdomain": subdomain}
    await unifi.set_config(config)
    await model.block_until(lambda: haproxy.status == "active")
    await model.block_until(lambda: unifi.status == "active")
    await unifi.add_relation("reverseproxy", "haproxy:reverseproxy")
    await model.block_until(lambda: haproxy.status == "maintenance")
    await model.block_until(lambda: haproxy.status == "active")


# async def test_relation(model, app):
#     haproxy = model.applications["haproxy"]
#     unifi_unit = app.units[0]
#     haproxy_unit = haproxy.units[0]
#
#     return_code = urllib.request.urlopen(
#         f"https://unifi.{haproxy_unit.public_address}"
#     ).getcode()
#     assert return_code == 200
