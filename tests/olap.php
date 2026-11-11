<?php
require __DIR__ . '/support.php';
$oracle=json_decode(file_get_contents('/workspace/docs/evidence/oracle.json'),true);
fwrite(STDERR,'OLAP and ROLLUP under ONLY_FULL_GROUP_BY'.PHP_EOL);
test_case('T09','Year/month/day drills and upward return; common period intersection',function(){
    $f=period_filters('2024-01-01','2024-02-29');
    $o=['level'=>'year','drill_year'=>2024,'drill_month'=>1];
    $years=analysis_rows('olap',$f,$o);check(count($years)===5,'Year groups');
    $months=analysis_rows('olap',$f,array_replace($o,['level'=>'month']));check(count($months)===10,'Month groups');
    $days=analysis_rows('olap',$f,array_replace($o,['level'=>'day']));check(count($days)===155,'5 × 31 daily records');
    check($years===analysis_rows('olap',$f,$o),'Returning to year recomputes same result');
    $partial=analysis_rows('olap',period_filters('2024-01-15','2024-02-10',[1]),array_replace($o,['level'=>'day']));
    check(count($partial)===17 && $partial[0]['weather_date']==='2024-01-15' && end($partial)['weather_date']==='2024-01-31','Intersection must not widen common range');
    check(analysis_rows('olap',$f,array_replace($o,['level'=>'day','drill_year'=>2025]))===[],'Disjoint period empty');
    return ['year_groups'=>count($years),'month_groups'=>count($months),'january_location_days'=>count($days),'partial_january_days'=>count($partial),'disjoint'=>'empty'];
});
test_case('T10','WITH ROLLUP subtotals use daily weights and location-days',function() use($oracle){
    $f=period_filters('2024-01-01','2024-02-29');$o=['level'=>'year','drill_year'=>2024,'drill_month'=>1];
    $rows=run_query(db(),...rollup_query($f,$o));
    $grand=array_values(array_filter($rows,fn($r)=>$r['location_id']===null));check(count($grand)===1,'One grand total');
    check((int)$grand[0]['valid_days']===300,'5 × 60 location-days');
    $whole=array_values(array_filter($oracle['aggregate_jan_feb_2024'],fn($r)=>$r['month_no']===null));
    close_to($grand[0]['mean_temperature'],array_sum(array_column($whole,'mean_temperature'))/5);
    foreach($rows as $r)if($r['location_id']!==null && $r['month_no']===null) {
        check((int)$r['valid_days']===60,'Each annual/location subtotal 60 days');
        $x=array_values(array_filter($whole,fn($x)=>$x['location_id']==$r['location_id']))[0];close_to($r['mean_temperature'],$x['mean_temperature']);
    }
    return ['rollup_rows'=>count($rows),'grand_total'=>$grand[0],'unit'=>'location-days for combined locations'];
});
finish_tests();
