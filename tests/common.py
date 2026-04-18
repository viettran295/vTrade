import pytest
import time
import subprocess
import docker
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