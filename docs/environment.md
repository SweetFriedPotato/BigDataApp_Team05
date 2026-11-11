# Execution environment

Host: Ubuntu 24.04.4 LTS, x86_64; user jiheechoi0102. Docker 29.6.2. Python 3 from `/home/jiheechoi0102/miniconda3/bin/python3`. PHP/Apache/MariaDB host executables were not found. No XAMPP directory found at `/opt/lampp`.

Installed runtime versions, executable paths, CLI/Apache extensions and database identity will be recorded after the isolated runtime starts. The actual professor XAMPP/Windows environment is not available and must be distinguished from Docker Apache verification.

## Isolated runtime actually executed

- Web: `seasonal-team05-web-1`; PHP 8.2.35 CLI at `/usr/local/bin/php`; Apache 2.4.69 at `/usr/sbin/apache2` (see apache.txt for authoritative build details).
- MariaDB: `seasonal-team05-db-1`, 10.4.34, MySQL client `/usr/bin/mysql`, dump `/usr/bin/mysqldump`; data only in the project named volume.
- PHP configuration: `/usr/local/etc/php/conf.d/seasonal.ini`, native `pdo_mysql` extension enabled. CLI evidence: evidence/php-cli.txt. Apache SAPI verification follows in P4.
- DB connection: database team05, account team05@%, password team05 (public evaluation defaults). Session SQL mode includes ONLY_FULL_GROUP_BY; no global server modes changed.
- Application path inside Apache: `/var/www/html/team05`; local URL `http://127.0.0.1:8055/team05/`. XAMPP copy target remains `htdocs/team05`.
- Docker 29 internal-only networks do not expose published ports. Added a separate web access bridge for localhost access; database remains on the internal network. Offline proof will use a new web container attached only to an internal network.
- Host XAMPP/Windows and the professor's specific client remain unavailable; these are not claimed as tested.

Apache SAPI confirmed as `apache2handler`, PHP 8.2.35, pdo_mysql and session enabled: `evidence/php-apache.json`. Temporary probe removed. CLI and Apache load the same application ini files.

## Additional actual official XAMPP compatibility run

Official XAMPP Linux 8.2.12 was installed in a new Ubuntu 22.04 container. Its installer completed with code 0; no host XAMPP/system files were changed. The installed image was used for a fresh container with Docker network mode `none`.

- php: PHP 8.2.12 (cli) (built: Nov 25 2023 08:09:53) (NTS); Copyright (c) The PHP Group; Zend Engine v4.2.12, Copyright (c) Zend Technologies
- apache: Server version: Apache/2.4.58 (Unix); Server built:   Nov 25 2023 07:37:35
- mysql_client: /opt/lampp/bin/mysql  Ver 15.1 Distrib 10.4.32-MariaDB, for Linux (x86_64) using readline 5.1
- mysqldump: mysqldump  Ver 10.19 Distrib 10.4.32-MariaDB, for Linux (x86_64)

Apache PHP probe: {'sapi': 'apache2handler', 'version': '8.2.12', 'pdo_mysql': True, 'ini': '/opt/lampp/etc/php.ini'}. CLI loaded `/opt/lampp/etc/php.ini`. Temporary probe removed. Actual htdocs path `/opt/lampp/htdocs/team05`; default config 127.0.0.1:3306 and team05/team05/team05, no environment override. Separate local override to localhost also passed.

Create/insert, all nine user screens, HTTP CRUD/Session, every calculation/rollback test, drop/create/insert and actual XAMPP mysql-client dump restoration passed. Windows/macOS and the professor’s physical server remain NOT_RUN. See evidence/xampp-install.json and xampp-installer-log.txt.

## Revision verification — 2026-11-12 Asia/Seoul

The existing prepared Compose volume was backed up privately and kept intact. Mutation tests used new isolated DBs. Final capture server was a separate Apache container serving a read-only ZIP extraction at /var/www/html/team05, URL http://127.0.0.1:8057/team05/. Actual serving file hashes, HTTP static asset bytes and media identity were checked; it was not inferred from a working-directory comparison.

Rerun environments: PHP8.2.35 / Apache2.4.69 / MariaDB10.4.34; separately official Linux XAMPP PHP8.2.12 / Apache2.4.58 / MariaDB10.4.32 at /opt/lampp/htdocs/team05 with network=none. Both fresh installation families reran SQL calculation/transaction/HTTP and restoration checks. Exact actual versions and commands appear in revision JSON metadata. PHP8.0 runtime, Windows/macOS and professor physical host remain NOT_RUN.

Optional artifacts: Chromium141.0.7390.37 for browser/screenshots/PDF/video; LibreOffice7.3.7.2 for actual PPT rendering; PyMuPDF for per-page PNGs and geometric/text checks. Host DNS prevented the first document-render image installation attempts; only the isolated image build used a verified Ubuntu archive host mapping and signed Ubuntu packages. No host resolver or global package configuration was changed. The generated image is a developer tool, not part of the offline PHP runtime.

Original review-2026-11-11 and all existing commits remain intact. Current successful GitHub synchronization is recorded by observed SHA snapshots; original missing-credential failures are historical. Existing server ports and unrelated containers/databases were preserved.
