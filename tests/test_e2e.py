import pytest
import time
import subprocess
import docker
from playwright.sync_api import expect
from testcontainers.core.container import DockerContainer

def ensure_docker_img_exists(img: str):
    """
    Pull docker image if not exists
    """
    client = docker.from_env()
    try:
        client.images.get(img)
    except Exception:
        client.images.pull(img)

@pytest.fixture(scope="session")
def app_url():
    fundamental_img = "viettrann/fundamental:latest"
    strategy_processor_img = "viettrann/str-proc:x86_64"
    ensure_docker_img_exists(fundamental_img)
    ensure_docker_img_exists(strategy_processor_img)
    fundamental = (
        DockerContainer(fundamental_img)
        .with_kwargs(network_mode="host")
    )
    strategy_processor = (
        DockerContainer(strategy_processor_img)
        .with_kwargs(network_mode="host")
    )
    with fundamental, strategy_processor:
        process = subprocess.Popen(
            ["python", "app.py"],  
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        host = "localhost"
        port = "8050"
        time.sleep(5)
        yield f"http://{host}:{port}"
        process.terminate()
        process.wait()

def test_crossing_ma_graph(page, app_url):
    """
    Test end to end Crossing MA graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("COIN")
    page.get_by_role("button", name="Search").click()
    # Verify the crossing MA graph exists
    expect(page.get_by_text("Crossing MA")).to_be_visible(timeout=20000)
    expect(page.get_by_role("checkbox", name="Crossing MA")).to_be_visible(timeout=20000)
    expect(page.get_by_text("Short moving average")).to_be_visible(timeout=20000)
    expect(page.locator("#short-ma-input")).to_be_visible(timeout=20000)
    expect(page.get_by_text("Long moving average")).to_be_visible(timeout=20000)
    expect(page.locator("#long-ma-input")).to_be_visible(timeout=20000)
    expect(page.get_by_text("SMA", exact=True)).to_be_visible(timeout=20000)
    expect(page.get_by_role("radio", name="SMA")).to_be_visible(timeout=20000)
    expect(page.get_by_text("EWMA")).to_be_visible(timeout=20000)
    expect(page.get_by_role("radio", name="EWMA")).to_be_visible(timeout=20000)
    expect(page.get_by_role("button", name="Apply")).to_be_visible(timeout=20000)
    expect(page.locator("rect").nth(4)).to_be_visible(timeout=20000)
    expect(page.locator(".bg")).to_be_visible(timeout=20000)

def test_bollingerbands_graph(page, app_url):
    """
    Test end to end Bollinger bands graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("NVDA")
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_text("Bollinger bands")).to_be_visible(timeout=20000)
    expect(page.get_by_role("checkbox", name="Bollinger bands")).to_be_visible(timeout=20000)
    page.get_by_role("checkbox", name="Bollinger bands").check()
    # Verify the Bollinger bands graph exists
    expect(page.locator("#bb-graph > .js-plotly-plot > .plot-container > .user-select-none > svg > .draglayer > .xy > .nsewdrag")).to_be_visible(timeout=20000)

def test_rsi_graph(page, app_url):
    """
    Test end to end fundamental graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("GOOG")
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_text("RSI")).to_be_visible(timeout=20000)
    expect(page.get_by_role("checkbox", name="RSI")).to_be_visible(timeout=20000)
    page.get_by_role("checkbox", name="RSI").check()
    # Verify the Bollinger bands graph exists
    expect(page.locator("#rsi-graph > .js-plotly-plot > .plot-container > .user-select-none > svg > .draglayer > .xy > .nsewdrag")).to_be_visible(timeout=20000)

def test_fundamental_graph(page, app_url):
    """
    Test end to end fundamental graph
    """
    page.goto(app_url)
    page.reload()
    # Click to find stock info
    page.get_by_role("textbox", name="Stock symbol").click()
    page.get_by_role("textbox", name="Stock symbol").fill("TSLA")
    page.get_by_role("button", name="Search").click()
    # Click Fundamental tab and verify the graph exists
    page.locator("#fa-id").click()
    expect(page.locator("rect").nth(4)).to_be_visible(timeout=20000)
