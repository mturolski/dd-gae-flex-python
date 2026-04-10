Datadog on Google App Engine Flexible (Python)

A sample Flask app demonstrating how to run the Datadog Agent on Google App Engine Flexible environment, with APM tracing, log collection, trace-log correlation, and App & API Protection (AppSec).
Features

✅ Infrastructure metrics
✅ APM tracing via ddtrace
✅ Log collection with trace-log correlation
✅ App & API Protection (AppSec / IAST)
✅ SBOM / Software Composition Analysis

Prerequisites

Google Cloud SDK installed and authenticated
A Datadog account with an API key
A GCP project with App Engine enabled

Project Structure
.
├── app.yaml              # GAE Flex configuration
├── Dockerfile            # Custom runtime container definition
├── entrypoint.sh         # Container startup script
├── logs.yaml             # Datadog logs agent configuration
├── main.py               # Flask application
└── requirements.txt      # Python dependencies

Setup
1. Clone the repo
bashgit clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
2. Set your Datadog API key
In app.yaml, add your Datadog API key:
yamlenv_variables:
  DD_API_KEY: "your_api_key_here"

⚠️ Do not commit your API key to source control. Consider using GCP Secret Manager for production. This guide is purely for demonstartion purposes.

3. Deploy to App Engine
gcloud app deploy
4. Verify the deployment
Visit your app URL:
gcloud app browse

How It Works
Dockerfile
The container uses a custom runtime (runtime: custom in app.yaml) based on python:3.11. During the build:

The Datadog Agent v7 is installed via the official install script
APM is enabled by appending apm_config to datadog.yaml
A log directory /var/log/app is created for the logs agent to tail

entrypoint.sh
On container startup:

The Datadog main agent starts in the background
The trace agent is started separately with the correct config path (required on GAE Flex as the binaries are under /opt/datadog-agent/embedded/bin/)
The Flask app is started via ddtrace-run gunicorn for automatic APM instrumentation


Note: The trace agent binary on GAE Flex is located at /opt/datadog-agent/embedded/bin/trace-agent and must be started manually with --config /etc/datadog-agent/datadog.yaml. The main agent does not automatically start it in this environment.

Logging
Logs are written to both stdout (for GCP Cloud Logging) and /var/log/app/app.log (for the Datadog logs agent). The DatadogTraceFilter in main.py injects dd_trace_id and dd_span_id into every log entry, enabling trace-log correlation in Datadog.

APM
ddtrace is used with patch_all() for automatic instrumentation of Flask, and ddtrace-run wraps gunicorn to ensure all requests are traced.

App & API Protection
AppSec is enabled via DD_APPSEC_ENABLED=true in app.yaml and enable_appsec() in main.py. IAST is also enabled for code-level vulnerability detection.

Verifying in Datadog
FeatureWhere to lookInfrastructureInfrastructure → Host MapAPM tracesAPM → Traces, filter by service:flex-serviceLogsLogs, filter by service:flex-serviceTrace-log correlationClick a trace → Logs tabAppSecSecurity → Application SecurityVulnerabilities (IAST)Security → VulnerabilitiesSCA / SBOMSecurity → Software Composition Analysis
Testing AppSec
You can trigger a test AppSec signal by sending a suspicious request:
bashcurl "https://YOUR_APP_URL/?q=<script>alert(1)</script>"
Check Security → Signals in Datadog within a few minutes.

Known Limitations

GAE Flex containers are ephemeral — each deploy or scale event creates a new host in Datadog. This is expected behaviour.
The trace agent must be started manually in entrypoint.sh — it cannot be auto-started by the main agent in this environment.
type: stdout in the logs config does not work on GAE Flex (at least during my testing). Use type: file instead.