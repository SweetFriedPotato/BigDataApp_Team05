#!/usr/bin/env bash
# Project-local convenience only; XAMPP requires neither Docker nor this script.
set -euo pipefail
cd "$(dirname "$0")/.."
case "${1:-help}" in
  up) docker compose up -d --build ;;
  init)
    count=$(docker compose exec -T -e MYSQL_PWD=team05 db mysql -uteam05 -Nse "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA='team05'")
    if [ "$count" != 0 ]; then echo 'Refusing initialization: team05 already contains tables. Back up first. Use verify_install.py for isolated reset checks.' >&2; exit 1; fi
    cat sql/dbcreate.sql sql/dbinsert.sql | docker compose exec -T -e MYSQL_PWD=team05 db mysql -uteam05 --default-character-set=utf8mb4 team05
    ;;
  lint) docker compose exec -T web sh -c 'find /var/www/html/team05 -name "*.php" -exec php -l {} \;' ;;
  test) python3 tools/verify_install.py ;;
  dump)
    mkdir -p .local
    docker compose exec -T -e MYSQL_PWD=team05 db mysqldump -uteam05 --default-character-set=utf8mb4 --single-transaction --skip-lock-tables --skip-comments --skip-dump-date team05 > .local/dbdump.sql
    mv .local/dbdump.sql sql/dbdump.sql
    ;;
  status) docker compose ps ;;
  down) docker compose down ;;
  *) echo 'Usage: tools/dev.sh up | init | lint | test | dump | status | down'; exit 0 ;;
esac
