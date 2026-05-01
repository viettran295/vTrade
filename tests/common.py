import pytest
import time
import subprocess
import os
import docker
import urllib.request
from dotenv import load_dotenv
from testcontainers.core.container import DockerContainer

load_dotenv()


def ensure_docker_img_exists(img: str):
    """
    Pull docker image if not exists
    """
    client = docker.from_env()
    try:
        client.images.get(img)
    except Exception:
        client.images.pull(img)


def wait_for_http(host: str, port: int, path: str = "/", timeout: float = 60.0):
    """Block until an HTTP endpoint returns a non-5xx response."""
    url = f"http://{host}:{port}{path}"
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status < 500:
                    return
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise TimeoutError(f"{url} not ready after {timeout}s — last error: {last_err}")


@pytest.fixture(scope="session")
def app_url():
    host = "localhost"
    vtrade_port = "8050"
    twel_key = os.environ.get("TWEL_DATA_KEY")
    fundamental_img = "viettrann/fundamental:x86_64"
    strategy_processor_img = "viettrann/strategy-processor:x86_64"
    ensure_docker_img_exists(fundamental_img)
    ensure_docker_img_exists(strategy_processor_img)
    fundamental = DockerContainer(fundamental_img).with_exposed_ports(3000)
    strategy_processor = (
        DockerContainer(strategy_processor_img)
        .with_env("TWEL_DATA_KEY", twel_key)
        .with_exposed_ports(8000)
    )
    with fundamental, strategy_processor:
        f_port = fundamental.get_exposed_port(3000)
        s_port = strategy_processor.get_exposed_port(8000)
        # Assign testing containers port to env variable url
        env = {
            **os.environ,
            "FUNDAMENTAL_URL": f"http://{host}:{f_port}",
            "STRATEGY_PROCESSOR_URL": f"http://{host}:{s_port}",
        }
        process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        wait_for_http(host, vtrade_port)
        yield f"http://{host}:{vtrade_port}"
        process.terminate()
        process.wait()
