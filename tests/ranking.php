<?php
require __DIR__ . '/support.php';
function tied_fixture(): void {
    $p=db();run_query($p,'DELETE FROM daily_temperatures WHERE location_id IN (1,2,3) AND weather_date BETWEEN ? AND ?',['2023-01-01','2023-01-06']);
    foreach([1=>4,2=>6,3=>6] as $id=>$count)for($n=1;$n<=$count;$n++){
        $mean=$id===3 ? null : 20;$high=$n<=$count/2 ? 28 : 29;
        run_query($p,'INSERT INTO daily_temperatures VALUES (?,?,?,?,?)',[$id,sprintf('2023-01-%02d',$n),$mean,$high,19]);
    }
}
test_case('T11','Equal ratios 2/4 and 3/6 tie; zero-valid region excluded; unrounded rates distinguish close values',function(){
    $p=db();$p->beginTransaction();
    try{
        tied_fixture();$rows=analysis_rows('ranking',period_filters('2023-01-01','2023-01-06',[1,2,3]),['top_rank'=>5,'min_valid_days'=>1]);
        check(count($rows)===2 && (int)$rows[0]['rank_no']===1 && (int)$rows[1]['rank_no']===1,'Same 50% rank, exclude NULL denominator');
        close_to($rows[0]['matching_rate'],50);close_to($rows[1]['matching_rate'],50);
        $p->exec('UPDATE daily_temperatures SET tmean=20,tmax=30,tmin=19 WHERE location_id IN (4,5)');
        $p->exec("UPDATE daily_temperatures SET tmax=28 WHERE location_id IN (4,5) AND weather_date='2023-01-01'");
        $p->exec("UPDATE daily_temperatures SET tmean=NULL WHERE location_id=4 AND weather_date='2023-01-02'");
        $near=analysis_rows('ranking',period_filters(DATA_START,DATA_END,[4,5]),['top_rank'=>5,'min_valid_days'=>1]);
        check(number_format((float)$near[0]['matching_rate'],2)===number_format((float)$near[1]['matching_rate'],2),'Display percentages should round equal');
        check((int)$near[0]['location_id']===4 && (int)$near[0]['rank_no']===1 && (int)$near[1]['rank_no']===2,'Unrounded rates must have distinct ranks');
        return ['ties'=>$rows,'same_display_distinct_ranks'=>$near];
    }finally{$p->rollBack();}
});
test_case('T12','Top 1 returns every tied first-place location; minimum days applied',function(){
    $p=db();$p->beginTransaction();
    try{
        tied_fixture();$f=period_filters('2023-01-01','2023-01-06',[1,2,3]);
        $rows=analysis_rows('ranking',$f,['top_rank'=>1,'min_valid_days'=>1]);check(count($rows)===2,'Top 1 contains both ties');
        $qualified=analysis_rows('ranking',$f,['top_rank'=>1,'min_valid_days'=>5]);check(count($qualified)===1 && (int)$qualified[0]['location_id']===2,'Minimum valid days before ranking');
        return ['top1_rows'=>count($rows),'min5_rows'=>count($qualified)];
    }finally{$p->rollBack();}
});
test_case('T13','Actual August 2024 ranks versus independent raw Decimal oracle',function(){
    $oracle=json_decode(file_get_contents('/workspace/docs/evidence/oracle.json'),true)['ranking_august_2024'];
    $rows=analysis_rows('ranking',period_filters('2024-08-01','2024-08-31'),['top_rank'=>5,'min_valid_days'=>1]);
    check(count($rows)===5,'All locations');
    foreach($rows as $i=>$r){foreach(['location_id','matching_days','valid_days','rank_no'] as $k)check((int)$r[$k]===$oracle[$i][$k],$k);close_to($r['matching_rate'],$oracle[$i]['matching_rate']);}
    return $rows;
});
finish_tests();
