<?php
// Team responsibility: Jieun Hwang (2376329) — Common PHP/config/PDO, Session/input/UI; solar-term and monthly-guide pages/queries.
// Implementation: Codex; one sequential implementation session. See docs/contributions.md.
declare(strict_types=1);
ini_set('display_errors', '0');
error_reporting(E_ALL);
date_default_timezone_set('Asia/Seoul');
set_exception_handler(function(Throwable $e): void {
    error_log(get_class($e) . ': ' . $e->getMessage());
    http_response_code(503);
    echo '<!doctype html><html lang="en"><meta charset="utf-8"><title>Service unavailable</title><h1>Service unavailable</h1><p>The request could not be completed. Please check the database connection or try again.</p><p><a href="index.php">Return home</a></p></html>';
});
if (session_status() !== PHP_SESSION_ACTIVE) {
    session_start(['use_strict_mode' => true, 'cookie_httponly' => true, 'cookie_samesite' => 'Lax',
        'cookie_secure' => !empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off']);
}
header("Content-Security-Policy: default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'self'; form-action 'self'; frame-ancestors 'none'");
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: strict-origin-when-cross-origin');
header('Cache-Control: no-store');
require_once __DIR__ . '/db.php';
require_once __DIR__ . '/filters.php';
require_once __DIR__ . '/csrf.php';
require_once __DIR__ . '/session.php';
require_once __DIR__ . '/view.php';
