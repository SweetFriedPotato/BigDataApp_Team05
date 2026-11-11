<?php
// Implementation: Codex. All changes require POST and a session-bound CSRF token.
declare(strict_types=1);
function csrf_token(): string {
    return $_SESSION['csrf_token'] ??= bin2hex(random_bytes(32));
}
function check_csrf(array $input): void {
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
        throw new InvalidArgumentException('This action requires POST.');
    }
    $token = $input['csrf_token'] ?? null;
    if (!is_string($token) || !hash_equals(csrf_token(), $token)) {
        throw new InvalidArgumentException('The form expired. Reload the page and try again.');
    }
}
