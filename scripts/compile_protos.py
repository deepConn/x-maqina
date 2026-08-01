"""Generate gRPC Python files from proto definitions"""

import subprocess
import sys
from pathlib import Path


def compile_protos():
    """Compile Protocol Buffer definitions"""
    proto_dir = Path("grpc/proto")
    output_dir = Path("grpc/gen")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Compile each proto file
    for proto_file in proto_dir.glob("*.proto"):
        print(f"Compiling {proto_file}...")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "grpc_tools.protoc",
                f"-I{proto_dir}",
                f"--python_out={output_dir}",
                f"--grpc_python_out={output_dir}",
                f"--pyi_out={output_dir}",
                str(proto_file),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"Error compiling {proto_file}:")
            print(result.stderr)
            return False

        print(f"✓ Generated {proto_file.stem}_pb2.py and {proto_file.stem}_pb2_grpc.py")

    print("\nAll proto files compiled successfully!")
    return True


if __name__ == "__main__":
    success = compile_protos()
    sys.exit(0 if success else 1)
