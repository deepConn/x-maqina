#!/usr/bin/env python
"""Start gRPC server for x-maqina"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from grpc.server import GrpcServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main():
    """Main entry point"""
    server = GrpcServer(port=50051)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
