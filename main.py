import datetime
import logging
import subprocess
from pythonjsonlogger import jsonlogger
from ddtrace import patch_all, tracer
from flask import Flask, render_template

patch_all()
from ddtrace.appsec import enable as enable_appsec
enable_appsec()

# Set up JSON logger with Datadog trace correlation
logger = logging.getLogger(__name__)
formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
)

# Stream handler (stdout -> GCP Cloud Logging)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# File handler (file -> Datadog Agent)
file_handler = logging.FileHandler('/var/log/app/app.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)

# Inject Datadog trace context into logs
class DatadogTraceFilter(logging.Filter):
    def filter(self, record):
        span = tracer.current_span()
        if span:
            record.dd_trace_id = span.trace_id
            record.dd_span_id = span.span_id
            record.dd_service = "gae-flex-test"
            record.dd_env = "dev"
        else:
            record.dd_trace_id = 0
            record.dd_span_id = 0
        return True

logger.addFilter(DatadogTraceFilter())

app = Flask(__name__)

@app.route("/")
def root():
    logger.info("Root endpoint hit", extra={"page": "home"})
    
    dummy_times = [
        datetime.datetime(2018, 1, 1, 10, 0, 0),
        datetime.datetime(2018, 1, 2, 10, 30, 0),
        datetime.datetime(2018, 1, 3, 11, 0, 0),
    ]

    logger.info("Rendering template", extra={"times_count": len(dummy_times)})
    return render_template("index.html", times=dummy_times)

@app.route("/dd-status")
def dd_status():
    output = ""
    commands = {
        "PROCESSES": ["ps", "aux"],
        "AGENT BINARY": ["find", "/usr", "-name", "datadog-agent"],
        "PORTS": ["ss", "-tlnp"]
    }
    for label, cmd in commands.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            output += f"{label}:\n{result.stdout}\n{result.stderr}\n\n"
        except Exception as e:
            output += f"{label}: ERROR - {str(e)}\n\n"
    return f"<pre>{output}</pre>"

@app.route("/dd-trace-check")
def dd_trace_check():
    result = subprocess.run(
        ["env"],
        capture_output=True, text=True
    )
    return f"<pre>{result.stdout}</pre>"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)