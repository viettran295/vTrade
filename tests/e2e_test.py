import pytest
import time
from playwright.sync_api import expect
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

@pytest.fixture(scope="session")
def docker_app_url():
    vtrade = (
        DockerContainer("viettrann/vtrade:x86_64")
        .with_kwargs(network_mode="host")
    )
    fundamental = (
        DockerContainer("viettrann/fundamental:latest")
        .with_kwargs(network_mode="host")
    )
    strategy_processor = (
        DockerContainer("viettrann/str-proc:x86_64")
        .with_kwargs(network_mode="host")
    )
    with vtrade, fundamental, strategy_processor:
        host = "localhost"
        port = "8050"
        time.sleep(5)
        yield f"http://{host}:{port}"


def test_fundamental_graph(page, docker_app_url):
    page.goto(docker_app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("COIN")
    page.get_by_role("button", name="Search").click()
    # Click Fundamental tab and verify the graph exists
    page.locator("#fa-id").click()
    expect(page.locator("rect").nth(4)).to_be_visible()
