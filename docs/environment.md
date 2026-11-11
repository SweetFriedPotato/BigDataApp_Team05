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
