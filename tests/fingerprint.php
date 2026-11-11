<?php
// Semantic fingerprint excludes volatile AUTO_INCREMENT counters and includes all table rows and keys.
require '/workspace/team05/includes/db.php';
$p=db();$tables=['daily_temperatures'=>'location_id,weather_date','locations'=>'location_id','monthly_food_guides'=>'guide_id','plan_locations'=>'plan_id,location_id','saved_plans'=>'plan_id','solar_terms'=>'term_date'];
$out=[];
foreach($tables as $table=>$order){$rows=run_query($p,"SELECT * FROM $table ORDER BY $order");$out[$table]=['rows'=>count($rows),'sha256'=>hash('sha256',json_encode($rows,JSON_UNESCAPED_UNICODE))];}
$out['constraints']=run_query($p,'SELECT TABLE_NAME,CONSTRAINT_NAME,CONSTRAINT_TYPE FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() ORDER BY TABLE_NAME,CONSTRAINT_NAME');
$out['indexes']=run_query($p,'SELECT TABLE_NAME,INDEX_NAME,NON_UNIQUE,SEQ_IN_INDEX,COLUMN_NAME FROM information_schema.STATISTICS WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME,INDEX_NAME,SEQ_IN_INDEX');
$out['columns']=run_query($p,'SELECT TABLE_NAME,COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLLATION_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME,ORDINAL_POSITION');
echo json_encode($out,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE),"\n";
