<?php
// CLI developer tests only. Never deployed below the Apache document root.
declare(strict_types=1);
require_once '/workspace/team05/includes/db.php';
require_once '/workspace/team05/includes/filters.php';
require_once '/workspace/team05/includes/queries.php';
$test_results = [];
function check(bool $condition, string $message): void { if (!$condition) throw new RuntimeException($message); }
function close_to(mixed $actual, mixed $expected, string $message = '', float $tolerance = 0.00001): void {
    check($actual !== null && abs((float)$actual - (float)$expected) <= $tolerance, $message . ': actual=' . var_export($actual,true) . ', expected=' . var_export($expected,true));
}
function test_case(string $id, string $description, callable $fn): void {
    global $test_results;
    try { $details = $fn(); $test_results[] = ['id'=>$id,'test'=>$description,'status'=>'PASS','actual'=>$details]; }
    catch (Throwable $e) { $test_results[] = ['id'=>$id,'test'=>$description,'status'=>'FAIL','actual'=>$e->getMessage()]; }
}
function finish_tests(): void {
    global $test_results;
    echo json_encode(['environment'=>run_query(db(),'SELECT VERSION() version,CURRENT_USER() account,@@sql_mode sql_mode')[0], 'tests'=>$test_results],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE),"\n";
    exit(count(array_filter($test_results,fn($r)=>$r['status']==='FAIL')) ? 1 : 0);
}
function analysis_rows(string $kind, array $f, array $o): array {
    $builder = $kind . '_query';
    return run_query(db(), ...$builder($f,$o));
}
function period_filters(string $start, string $end, array $ids = [1,2,3,4,5]): array {
    return array_replace(default_filters(),['start_date'=>$start,'end_date'=>$end,'location_ids'=>$ids]);
}
