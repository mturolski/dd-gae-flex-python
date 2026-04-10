FROM python:3.11

# Install dependencies
RUN apt-get update && apt-get install -y curl

# Install Datadog Agent
RUN DD_AGENT_MAJOR_VERSION=7 \
    DD_API_KEY=<Your API key here> \
    DD_INSTALL_ONLY=true \
    bash -c "$(curl -L https://install.datadoghq.com/scripts/install_script_agent7.sh)"

# Configure Datadog Agent
RUN printf "\napm_config:\n  enabled: true\n  apm_non_local_traffic: true\nlogs_enabled: true\n" \
    >> /etc/datadog-agent/datadog.yaml

# Copy and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Add Datadog logs config
RUN mkdir -p /etc/datadog-agent/conf.d/python.d
COPY logs.yaml /etc/datadog-agent/conf.d/python.d/conf.yaml

# Create app log directory
RUN mkdir -p /var/log/app

# Copy app code
COPY . /app
WORKDIR /app

# Copy and set entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]