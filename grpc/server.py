"""gRPC server setup and configuration"""

import asyncio
import logging
from concurrent import futures

try:
    import grpc
    from grpc.aio import server as grpc_server
    from grpc_reflection.v1alpha import reflection
except ImportError:
    grpc = None
    grpc_server = None
    reflection = None

from app.config import settings

logger = logging.getLogger(__name__)


class GrpcServer:
    """gRPC server for x-maqina"""

    def __init__(self, host: str = "0.0.0.0", port: int = 50051):
        """Initialize gRPC server"""
        self.host = host
        self.port = port
        self.server = None

    async def start(self) -> None:
        """Start gRPC server"""
        if not grpc_server:
            logger.warning("gRPC not available")
            return

        try:
            from grpc.aio import server as create_server
            from grpc_reflection.v1alpha import reflection

            # Create server with options
            options = [
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.keepalive_time_ms", 30000),
                ("grpc.keepalive_timeout_ms", 10000),
            ]

            self.server = await create_server(
                futures.ThreadPoolExecutor(max_workers=10),
                options=options,
            )

            # TODO: Add service implementations
            # add_SecurityServiceServicer_to_server(SecurityServicer(), server)
            # add_FinancialServiceServicer_to_server(FinancialServicer(), server)
            # etc.

            # Enable reflection
            if reflection:
                service_names = [
                    "xmaqina.v1.SecurityService",
                    "xmaqina.v1.FinancialService",
                    "xmaqina.v1.DiagnosticsService",
                    "xmaqina.v1.AgentService",
                    "xmaqina.v1.AutonomousService",
                    "grpc.reflection.v1alpha.ServerReflection",
                ]
                reflection.enable_server_reflection(service_names, self.server)

            # Bind to address
            await self.server.add_insecure_port(f"{self.host}:{self.port}")

            # Start server
            await self.server.start()
            logger.info(f"gRPC server started on {self.host}:{self.port}")

            # Keep server running
            await self.server.wait_for_termination()

        except Exception as e:
            logger.error(f"Failed to start gRPC server: {str(e)}")
            raise

    async def stop(self) -> None:
        """Stop gRPC server"""
        if self.server:
            await self.server.stop(0)
            logger.info("gRPC server stopped")

    async def run(self) -> None:
        """Run gRPC server (blocking)"""
        await self.start()


async def main():
    """Main entry point for gRPC server"""
    server = GrpcServer(port=50051)
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server")
        await server.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
