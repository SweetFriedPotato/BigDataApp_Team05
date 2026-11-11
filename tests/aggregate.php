<?php
require __DIR__ . '/support.php';
$oracle = json_decode(file_get_contents('/workspace/docs/evidence/oracle.json'),true,512,JSON_THROW_ON_ERROR);
$f = period_filters('2024-01-01','2024-02-29');
test_case('T05','Complex grouped statistics versus independent raw Decimal oracle',function() use($f,$oracle) {
    $rows=analysis_rows('aggregate',$f,['group_mode'=>'location_year_month']);
    check(count($rows)===10,'Expected 5 locations × 2 months');
    foreach($rows as $r) {
        $expected=array_values(array_filter($oracle['aggregate_jan_feb_2024'],fn($x)=>$x['location_id']==$r['location_id'] && $x['month_no']==$r['month_no']))[0];
        foreach(['valid_days','mean_temperature','mean_daily_max','mean_daily_min','mean_daily_range','period_high','period_low','matching_days','exceedance_days'] as $key) close_to($r[$key],$expected[$key],$key);
    }
    return ['groups'=>count($rows),'all_statistic_fields'=>'equal to oracle within 0.00001','first_group'=>$rows[0]];
});
test_case('T06','Annual partial-period mean is weighted by daily rows',function() use($f,$oracle) {
    $rows=analysis_rows('aggregate',$f,['group_mode'=>'location_year']);
    foreach($rows as $r){
        $expected=array_values(array_filter($oracle['aggregate_jan_feb_2024'],fn($x)=>$x['location_id']==$r['location_id'] && $x['month_no']===null))[0];
        close_to($r['mean_temperature'],$expected['mean_temperature']); check((int)$r['valid_days']===60,'January 31 + leap February 29');
    }
    return ['valid_days_each'=>60,'first_location_mean'=>$rows[0]['mean_temperature'],'source'=>'raw daily values, not unweighted monthly means'];
});
test_case('T07','Inclusive maximum/range limits and invalid-day exclusion',function(){
    $p=db();$p->beginTransaction();
    try{
        run_query($p,'DELETE FROM daily_temperatures WHERE location_id=1 AND weather_date BETWEEN ? AND ?',['2023-01-01','2023-01-04']);
        foreach([['2023-01-01',20,28,18],['2023-01-02',20,'28.01','18.01'],['2023-01-03',20,28,'17.99'],['2023-01-04',null,28,18]] as $r)run_query($p,'INSERT INTO daily_temperatures VALUES (?,?,?,?,?)',[1,...$r]);
        $r=analysis_rows('aggregate',period_filters('2023-01-01','2023-01-04',[1]),['group_mode'=>'location_year'])[0];
        check((int)$r['candidate_days']===4 && (int)$r['valid_days']===3 && (int)$r['matching_days']===1 && (int)$r['exceedance_days']===1,'Boundary counts');
        return $r;
    }finally{$p->rollBack();}
});
test_case('T08','Thresholds classify records without changing the valid-day denominator',function(){
    $f=period_filters('2024-08-01','2024-08-31');
    $low=analysis_rows('aggregate',array_replace($f,['max_temp_threshold'=>'-50.00']),['group_mode'=>'location_year']);
    $high=analysis_rows('aggregate',array_replace($f,['max_temp_threshold'=>'60.00','max_temp_range'=>'60.00']),['group_mode'=>'location_year']);
    foreach($low as $i=>$r){check((int)$r['valid_days']===31 && $r['valid_days']==$high[$i]['valid_days'],'Denominator invariant');check((int)$r['matching_days']===0 && (int)$high[$i]['matching_days']===31,'Classification changes');}
    return 'Each location remains 31 valid days; matches change from 0 to 31';
});
finish_tests();
