#!/usr/bin/env bash
# Optional developer compatibility test; all installation occurs inside Docker.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .local/xampp
installer=.local/xampp/installer.run
if [ ! -f "$installer" ]; then
  curl -fL --retry 1 --max-time 180 -o "$installer" 'https://downloads.sourceforge.net/project/xampp/XAMPP%20Linux/8.2.12/xampp-linux-x64-8.2.12-0-installer.run'
fi
# Pin the bytes actually used by this project's compatibility run.
printf '%s  %s\n' 'df0774e7a6d0d0754a5f0132015411234b5f953df2365b693d3758fc35a30374' "$installer" | sha256sum -c -
chmod u+x "$installer"
docker build --target base -f infra/Dockerfile.xampp -t seasonal-team05-xampp-base:22.04 .local/xampp
setup_name="slg-xampp-setup-$(date +%s)-$$"
trap 'docker rm -f "$setup_name" >/dev/null 2>&1 || true' EXIT
docker run -d --name "$setup_name" --network none -v "$PWD/$installer:/installer.run:ro" seasonal-team05-xampp-base:22.04 sleep infinity
# The vendor installer creates thousands of manual-page links. It can be slow;
# the log is inside this project-only container at /tmp/installbuilder_installer.log.
docker exec "$setup_name" /installer.run --mode unattended --unattendedmodeui none
docker exec "$setup_name" /opt/lampp/lampp stop
docker commit "$setup_name" seasonal-team05-xampp:8.2.12

