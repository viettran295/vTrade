import pytest
import time
import subprocess
import os
import docker
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

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
    twel_key = os.environ.get("TWEL_DATA_KEY")
    fundamental_img = "viettrann/fundamental:x86_64"
    strategy_processor_img = "viettrann/strategy-processor:x86_64"
    ensure_docker_img_exists(fundamental_img)
    ensure_docker_img_exists(strategy_processor_img)
    fundamental = (
        DockerContainer(fundamental_img)
        .with_exposed_ports(3000)
        .waiting_for(LogMessageWaitStrategy(""))
    )
    strategy_processor = (
        DockerContainer(strategy_processor_img)
        .with_env("TWEL_DATA_KEY", twel_key)
        .with_exposed_ports(8000)
        .waiting_for(LogMessageWaitStrategy(""))
    )
    with fundamental, strategy_processor:
        # Get dynamic testing containers port
        f_port = fundamental.get_exposed_port(3000)
        s_port = strategy_processor.get_exposed_port(8000)
        # Assign testing containers port to env variable url
        env = {
            **os.environ,
            "FUNDAMENTAL_URL": f"http://localhost:{f_port}",
            "STRATEGY_PROCESSOR_URL": f"http://localhost:{s_port}",
        }
        process = subprocess.Popen(
            ["python", "app.py"],  
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        host = "localhost"
        port = "8050"
        time.sleep(5)
        yield f"http://{host}:{port}"
        process.terminate()
        process.wait()