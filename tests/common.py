import pytest
import time
import subprocess
import os
import docker
import urllib.request
from dotenv import load_dotenv
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

load_dotenv()

CACHE_DB_PORT = 6379
FUNMENTAL_PORT = 8001
STRATEGY_PROCESSOR_PORT = 8000

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

def wait_for_cache_db(container: DockerContainer):
    """Executes 'redis-cli ping' inside the container and checks for PONG."""
    exit_code, output = container.exec(["redis-cli", "ping"])
    if exit_code != 0 or b"PONG" not in output:
        raise Exception(
            f"Dragonfly healthcheck failed: exit_code={exit_code}, output={output}"
        )

@pytest.fixture(scope="session")
def app_url():
    host = "localhost"
    vtrade_port = "8050"
    twel_key = os.environ.get("TWEL_DATA_KEY")
    cache_db_img = "docker.dragonflydb.io/dragonflydb/dragonfly:latest"
    fundamental_img = "viettrann/fundamental:x86_64"
    strategy_processor_img = "viettrann/strategy-processor:x86_64"
    ensure_docker_img_exists(cache_db_img)
    ensure_docker_img_exists(fundamental_img)
    ensure_docker_img_exists(strategy_processor_img)
    network = Network()
    with network:
        cache_db = (
            DockerContainer(cache_db_img)
            .with_network(network)
            .with_network_aliases("cache-db")
            .with_exposed_ports(CACHE_DB_PORT)
            .with_kwargs(ulimits=[{"name": "memlock", "hard": -1, "soft": -1}])
            .with_command("--maxmemory=2gb --cache_mode=true")
        )
        with cache_db:
            wait_for_cache_db(cache_db)
            # The fundamental container connects to cache-db via the shared
            # Docker network using the internal port (6379), not the host-mapped port.
            cache_db_internal_uri = f"redis://cache-db:{CACHE_DB_PORT}"
            fundamental = (
                DockerContainer(fundamental_img)
                .with_network(network)
                .with_env("CACHE_DB_URI", cache_db_internal_uri)
                .with_exposed_ports(FUNMENTAL_PORT)
            )
            strategy_processor = (
                DockerContainer(strategy_processor_img)
                .with_env("TWEL_DATA_KEY", twel_key)
                .with_exposed_ports(STRATEGY_PROCESSOR_PORT)
            )
            with fundamental, strategy_processor:
                f_port = fundamental.get_exposed_port(FUNMENTAL_PORT)
                s_port = strategy_processor.get_exposed_port(STRATEGY_PROCESSOR_PORT)
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
