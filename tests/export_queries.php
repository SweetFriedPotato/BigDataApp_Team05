<?php
require '/workspace/team05/includes/filters.php';
require '/workspace/team05/includes/queries.php';
$f=default_filters();$f['start_date']='2024-08-01';$f['end_date']='2024-08-31';
$out=[];
foreach(['aggregate','olap','ranking','window'] as $kind){[$sql,$params]=($kind.'_query')($f,default_options($kind));$out[$kind]=['sql'=>$sql,'bound_values'=>$params];}
[$sql,$params]=rollup_query($f,['level'=>'year','drill_year'=>2024,'drill_month'=>8]);$out['rollup']=['sql'=>$sql,'bound_values'=>$params];
echo json_encode($out,JSON_PRETTY_PRINT),"\n";
