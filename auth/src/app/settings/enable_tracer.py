from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from app.settings.base import Settings


class JaegerSettings(Settings):
    JAEGER_AGENT_HOST: str = "localhost"
    JAEGER_AGENT_PORT: int = 6831


def configure_tracer() -> None:
    settings = JaegerSettings()

    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.JAEGER_AGENT_HOST,
                agent_port=settings.JAEGER_AGENT_PORT,
            )
        )
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
