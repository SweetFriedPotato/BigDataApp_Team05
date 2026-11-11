# Optional developer PDF rendering; never part of the PHP/MariaDB runtime.
FROM ubuntu:22.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates libreoffice-impress fonts-liberation && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["libreoffice", "--headless", "-env:UserInstallation=file:///tmp/slg-lo-profile"]
