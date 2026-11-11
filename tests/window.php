<?php
require __DIR__ . '/support.php';
function window_fixture(): void {
    $p=db();run_query($p,'DELETE FROM daily_temperatures WHERE location_id IN (1,2) AND weather_date BETWEEN ? AND ?',['2023-01-01','2023-02-04']);
    $day=new DateTimeImmutable('2023-01-01');
    foreach([1=>0,2=>100] as $id=>$offset)for($n=1;$n<=35;$n++){
        $d=$day->modify('+'.($n-1).' days')->format('Y-m-d');
        run_query($p,'INSERT INTO daily_temperatures VALUES (?,?,?,?,?)',[$id,$d,$n+$offset,$n+$offset+2,$n+$offset-2]);
    }
}
function window_fixture_test(callable $fn): mixed {
    $p=db();$p->beginTransaction();try{window_fixture();return $fn();}finally{$p->rollBack();}
}
test_case('T14','Known sequence 1..35 has day7 mean4 and day30 mean15.5',fn()=>window_fixture_test(function(){
    $r=analysis_rows('window',period_filters('2023-01-01','2023-02-04',[1]),['metric'=>'mean','window_days'=>7]);
    close_to($r[6]['ma7'],4);close_to($r[29]['ma30'],15.5);
    return ['day7_ma7'=>$r[6]['ma7'],'day30_ma30'=>$r[29]['ma30']];
}));
test_case('T15','Changing display start preserves the same-day historical window',fn()=>window_fixture_test(function(){
    $o=['metric'=>'mean','window_days'=>30];
    $all=analysis_rows('window',period_filters('2023-01-01','2023-02-04',[1]),$o);
    $part=analysis_rows('window',period_filters('2023-01-31','2023-02-04',[1]),$o);
    close_to($part[0]['ma7'],28);close_to($part[0]['ma30'],16.5);
    close_to($part[0]['ma7'],$all[30]['ma7']);close_to($part[0]['ma30'],$all[30]['ma30']);
    return ['day31_ma7'=>$part[0]['ma7'],'day31_ma30'=>$part[0]['ma30']];
}));
test_case('T16','All four metrics across year/month boundaries versus raw Decimal oracle',function(){
    $expected=json_decode(file_get_contents('/workspace/docs/evidence/oracle.json'),true)['windows'];
    foreach($expected as $x){$r=analysis_rows('window',period_filters($x['weather_date'],$x['weather_date'],[$x['location_id']]),['metric'=>$x['metric'],'window_days'=>7])[0];close_to($r['ma7'],$x['ma7']);close_to($r['ma30'],$x['ma30']);}
    return ['cases'=>count($expected),'seoul_2024_01_01'=>$expected[0],'all_metrics'=>'mean/max/min/range','month_boundary'=>'2024-03-01 includes leap February'];
});
test_case('T17','First 6/29 rows lack full windows; missing date/invalid day do not masquerade as complete history',fn()=>window_fixture_test(function(){
    $o=['metric'=>'mean','window_days'=>7];$f=period_filters('2023-01-01','2023-02-04',[1]);$r=analysis_rows('window',$f,$o);
    foreach($r as $i=>$x){if($i<6)check($x['ma7']===null,'First6');if($i<29)check($x['ma30']===null,'First29');}
    run_query(db(),'DELETE FROM daily_temperatures WHERE location_id=1 AND weather_date=?',['2023-01-10']);
    $gap=analysis_rows('window',period_filters('2023-01-11','2023-01-11',[1]),$o)[0];
    check($gap['ma7']===null,'Seven rows spanning eight dates must not be a 7-day mean');
    run_query(db(),'UPDATE daily_temperatures SET tmean=NULL WHERE location_id=1 AND weather_date=?',['2023-01-20']);
    $invalid=analysis_rows('window',period_filters('2023-01-21','2023-01-21',[1]),$o)[0];check($invalid['ma7']===null && (int)$invalid['n7']===6,'Invalid day excluded from count');
    return ['first6and29'=>'NULL','date_gap'=>'NULL','invalid_metric_count'=>$invalid['n7']];
}));
test_case('T18','Location partitions do not mix; thresholds do not filter windows',fn()=>window_fixture_test(function(){
    $f=period_filters('2023-01-31','2023-01-31',[1,2]);$f['max_temp_threshold']='-50.00';
    $r=analysis_rows('window',$f,['metric'=>'mean','window_days'=>30]);
    close_to($r[0]['ma7'],28);close_to($r[1]['ma7'],128);close_to($r[1]['ma30'],116.5);
    check((int)$r[0]['matching_flag']===0 && (int)$r[1]['matching_flag']===0,'Threshold classifies only');
    return ['location1_ma7'=>$r[0]['ma7'],'location2_ma7'=>$r[1]['ma7'],'location2_ma30'=>$r[1]['ma30'],'zero_matches'=>'both averages still computed'];
}));
finish_tests();
