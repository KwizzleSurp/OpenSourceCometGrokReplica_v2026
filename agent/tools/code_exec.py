"""Safe local code execution via subprocess with timeout."""
import subprocess, sys, tempfile, os

def run_python(code: str, timeout: int = 30) -> dict:
    """Run Python code string in a subprocess. Returns stdout/stderr/returncode."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(code)
        fname = f.name
    try:
        result = subprocess.run(
            [sys.executable, fname],
            capture_output=True, text=True, timeout=timeout
        )
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": f"Timeout after {timeout}s", "returncode": -1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "returncode": -1}
    finally:
        os.unlink(fname)
