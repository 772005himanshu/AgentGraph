import docker
import os
import tempfile
import uuid

def run_tests_in_sandbox(patch_code: str, test_code: str) -> dict:
    """
    Runs the generated patch and test code inside an isolated Docker container.
    Returns the test output and pass/fail status.
    """
    client = docker.from_env()
    container_name = f"sandbox-{uuid.uuid4().hex[:8]}"
    
    # Create a temporary directory to mount into the container
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write the patch and tests
        with open(os.path.join(temp_dir, "patched_code.py"), "w") as f:
            f.write(patch_code)
            
        with open(os.path.join(temp_dir, "test_patched_code.py"), "w") as f:
            # Inject import of patched_code into test if needed, assuming the LLM does it
            f.write(test_code)
            
        try:
            # Run the container
            container = client.containers.run(
                "python:3.11-slim",
                command="pip install pytest && pytest test_patched_code.py",
                volumes={temp_dir: {'bind': '/app', 'mode': 'rw'}},
                working_dir="/app",
                name=container_name,
                detach=True,
                network_disabled=True, # NO NETWORK ACCESS
                mem_limit="256m",      # Memory limit
                cpu_period=100000,
                cpu_quota=50000,       # 0.5 CPU limit
                auto_remove=False      # Keep around just long enough to get logs
            )
            
            # Wait for completion (with timeout)
            result = container.wait(timeout=30)
            logs = container.logs().decode("utf-8")
            
            container.remove(force=True)
            
            passed = result["StatusCode"] == 0
            return {
                "passed": passed,
                "output": logs
            }
            
        except Exception as e:
            # Cleanup in case of error
            try:
                container = client.containers.get(container_name)
                container.remove(force=True)
            except:
                pass
                
            return {
                "passed": False,
                "output": str(e)
            }
