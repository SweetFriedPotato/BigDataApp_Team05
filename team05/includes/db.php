<?php
// Implementation: Codex. All application input goes through native PDO prepared statements.
declare(strict_types=1);
function connect_db(?array $config = null): PDO {
    $c = $config ?? require dirname(__DIR__) . '/config.php';
    $pdo = new PDO('mysql:host=' . $c['host'] . ';port=' . $c['port'] . ';dbname=' . $c['database'] . ';charset=utf8mb4',
        $c['username'], $c['password'], [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC, PDO::ATTR_EMULATE_PREPARES => false]);
    $pdo->exec("SET SESSION sql_mode='STRICT_TRANS_TABLES,ONLY_FULL_GROUP_BY,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'");
    $pdo->exec("SET SESSION time_zone='+09:00'");
    return $pdo;
}
function db(): PDO {
    static $connection = null;
    return $connection ??= connect_db();
}
function run_query(PDO $pdo, string $sql, array $params = []): array {
    $statement = $pdo->prepare($sql);
    foreach (array_values($params) as $i => $value) {
        $statement->bindValue($i + 1, $value, is_int($value) ? PDO::PARAM_INT : ($value === null ? PDO::PARAM_NULL : PDO::PARAM_STR));
    }
    $statement->execute();
    return $statement->columnCount() ? $statement->fetchAll() : [];
}
