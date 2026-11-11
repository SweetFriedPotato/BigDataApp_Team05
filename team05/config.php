<?php
// Implementation: Codex, one sequential session; human contributions are documented separately.
declare(strict_types=1);
$config = [
    'host' => '127.0.0.1', 'port' => 3306, 'database' => 'team05',
    'username' => 'team05', 'password' => 'team05', 'charset' => 'utf8mb4',
];
if (getenv('SLG_DB_HOST') !== false) {
    $config['host'] = getenv('SLG_DB_HOST');
}
if (is_file(__DIR__ . '/config.local.php')) {
    $local = require __DIR__ . '/config.local.php';
    if (!is_array($local) || array_diff(array_keys($local), array_keys($config))) {
        throw new RuntimeException('Invalid local configuration.');
    }
    $config = array_replace($config, $local);
}
foreach (['host', 'database', 'username', 'password', 'charset'] as $key) {
    if (!is_string($config[$key])) {
        throw new RuntimeException('Invalid configuration type.');
    }
}
if (!preg_match('/^[a-zA-Z0-9_.:-]+$/D', $config['host'])
    || !preg_match('/^[a-zA-Z0-9_]+$/D', $config['database'])
    || $config['charset'] !== 'utf8mb4'
    || filter_var($config['port'], FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 65535]]) === false) {
    throw new RuntimeException('Invalid database configuration.');
}
return $config;
