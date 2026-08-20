from pathlib import Path
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

LAYER_DIR = PROJECT_ROOT / "lambda_layer"
TARGET_DIR = LAYER_DIR / "python"
REQUIREMENTS_FILE = LAYER_DIR / "requirements.txt"


def build_layer():
    print("Building psycopg2 Lambda layer...")

    if TARGET_DIR.exists():
        print("Removing old layer...")
        shutil.rmtree(TARGET_DIR)

    TARGET_DIR.mkdir(parents=True)

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--platform",
        "manylinux2014_x86_64",
        "--implementation",
        "cp",
        "--python-version",
        "3.13",
        "--abi",
        "cp313",
        "--only-binary=:all:",
        "--upgrade",
        "--target",
        str(TARGET_DIR),
        "-r",
        str(REQUIREMENTS_FILE),
    ]

    subprocess.run(
        command,
        check=True,
    )

    for cache_directory in TARGET_DIR.rglob("__pycache__"):
        shutil.rmtree(
            cache_directory,
            ignore_errors=True,
        )

    for pyc_file in TARGET_DIR.rglob("*.pyc"):
        pyc_file.unlink()

    print()
    print("Lambda layer built successfully.")
    print(f"Location: {TARGET_DIR}")


if __name__ == "__main__":
    build_layer()
