<?php
require __DIR__ . '/support.php';
require '/workspace/team05/includes/chart.php';
require '/workspace/team05/includes/view.php';
test_case('T41','Chart geometry uses SQL values and respects single-day, NULL, gaps and calendar spacing',function(){
    $row=fn($date,$daily,$a,$b)=>['weather_date'=>$date,'metric_value'=>$daily,'ma7'=>$a,'ma30'=>$b];
    $one=trend_geometry([$row('2024-01-01',1.72,'1.141429','0.301333')]);
    check($one['day_span']===0,'Single date has zero span');foreach($one['series'] as $segments)check(is_finite($segments[0][0]['x']) && is_finite($segments[0][0]['y']),'Finite single-day coordinates');
    ob_start();render_plot_svg($one,'Seoul',1,['window_days'=>7]);$svg=ob_get_clean();
    $document=new DOMDocument();check($document->loadXML($svg),'Rendered single-day SVG is valid XML');
    check(!str_contains($svg,'NaN') && !str_contains($svg,'INF'),'Finite rendered SVG');
    $g=trend_geometry([$row('2023-01-01',1,1,null),$row('2023-01-02',null,2,null),$row('2023-01-04',4,4,null)]);
    check(count($g['series']['metric_value'])===2,'NULL daily value breaks line');check($g['series']['ma30']===[],'NULL average not plotted as zero');check(count($g['series']['ma7'])===2,'Missing calendar date breaks average line');
    $x1=$g['series']['ma7'][0][0]['x'];$x2=$g['series']['ma7'][0][1]['x'];$x4=$g['series']['ma7'][1][0]['x'];close_to($x4-$x2,2*($x2-$x1),'Calendar spacing');
    check(trend_geometry([$row('2023-01-01',null,null,null)])['empty'],'All NULL produces empty plot');
    $rows=analysis_rows('window',period_filters('2024-01-01','2024-01-03',[1]),['metric'=>'mean','window_days'=>30]);$plot=trend_geometry($rows);
    foreach(['metric_value','ma7','ma30'] as $key)foreach($plot['series'][$key] as $segment)foreach($segment as $i=>$point){$matches=array_values(array_filter($rows,fn($r)=>$r['weather_date']===$point['date']));close_to($point['value'],$matches[0][$key],'Exact SQL value');}
    return ['single_day'=>'finite point per available series','null_and_gaps'=>'segments broken; no fabricated zero','equal_calendar_intervals'=>true,'sql_source_values_preserved'=>true];
});finish_tests();
