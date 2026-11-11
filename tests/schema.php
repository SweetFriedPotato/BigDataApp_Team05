<?php
// CLI only; uses the newly created project DB, rolls back all constraint probes.
declare(strict_types=1);
require '/workspace/team05/includes/db.php';
$p = db();
$tables = run_query($p, "SELECT TABLE_NAME, ENGINE, TABLE_COLLATION FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME");
if (count($tables) !== 6) throw new RuntimeException('Expected six base tables');
$counts = [];
foreach ($tables as $t) {
    if ($t['ENGINE'] !== 'InnoDB' || $t['TABLE_COLLATION'] !== 'utf8mb4_unicode_ci') throw new RuntimeException('Engine/collation mismatch');
    $name = $t['TABLE_NAME'];
    $counts[$name] = (int)$p->query('SELECT COUNT(*) FROM `' . $name . '`')->fetchColumn();
}
$expected = ['daily_temperatures'=>5480,'locations'=>5,'monthly_food_guides'=>12,'plan_locations'=>0,'saved_plans'=>0,'solar_terms'=>72];
if ($counts !== $expected) throw new RuntimeException('Seed row counts mismatch');
$constraints = run_query($p, 'SELECT TABLE_NAME,CONSTRAINT_NAME,CONSTRAINT_TYPE FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() ORDER BY TABLE_NAME,CONSTRAINT_NAME');
$indexes = run_query($p, 'SELECT TABLE_NAME,INDEX_NAME,SEQ_IN_INDEX,COLUMN_NAME FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME,INDEX_NAME,SEQ_IN_INDEX');
$expectFailure = function(string $sql, array $params) use ($p): void {
    try { run_query($p,$sql,$params); } catch (PDOException $e) { return; }
    throw new RuntimeException('Constraint did not reject invalid record');
};
$p->beginTransaction();
try {
    $expectFailure('INSERT INTO daily_temperatures VALUES (?,?,?,?,?)',[1,'2023-01-01',0,1,-1]);
    $expectFailure('INSERT INTO daily_temperatures VALUES (?,?,?,?,?)',[99,'2023-01-01',0,1,-1]);
    run_query($p,'DELETE FROM daily_temperatures WHERE location_id=1 AND weather_date=?',['2023-01-01']);
    $expectFailure('INSERT INTO daily_temperatures VALUES (?,?,?,?,?)',[1,'2023-01-01',null,0,1]);
    $expectFailure('INSERT INTO monthly_food_guides (month_no,food_name,source_url) VALUES (?,?,?)',[13,'invalid','https://example.invalid/']);
    $expectFailure('INSERT INTO saved_plans (plan_name,start_date,end_date,max_temp_threshold,max_temp_range) VALUES (?,?,?,?,?)',['invalid','2025-02-01','2025-01-01',28,10]);
} finally { $p->rollBack(); }
echo json_encode(['result'=>'PASS','identity'=>run_query($p,'SELECT VERSION() version,DATABASE() db,CURRENT_USER() account,@@sql_mode sql_mode')[0], 'tables'=>$tables,'counts'=>$counts,'constraints'=>$constraints,'indexes'=>$indexes,'constraint_probes'=>'duplicate PK, bad FK, null-mean inverted temperatures, invalid month and reversed plan dates rejected'],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE),"\n";
