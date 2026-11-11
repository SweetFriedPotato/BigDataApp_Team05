<?php
require __DIR__ . '/support.php';
require '/workspace/team05/includes/plans.php';
function draft(array $ids=[1,2],string $name='CLI verification'): array {return array_merge(period_filters('2024-08-01','2024-08-31',$ids),['plan_name'=>$name,'memo'=>'한글 memo <script>alert(1)</script>']);}
function remove_if_exists(?int $id): void {if($id!==null && get_plan(db(),$id))delete_plan(db(),$id);}
test_case('T21','Committed create/read preserves all common fields and locations',function(){
    $id=null;try{$d=validate_plan(draft());$id=save_plan(db(),$d);$got=get_plan(db(),$id);foreach($d as $key=>$v)check($got[$key]==$v,$key);return ['id'=>$id,'locations'=>$got['location_ids'],'database_commit'=>true];}finally{remove_if_exists($id);}
});
test_case('T22','Update replaces body and locations; identical update is valid',function(){
    $id=null;try{$d=validate_plan(draft());$id=save_plan(db(),$d);save_plan(db(),$d,$id);$d=validate_plan(array_replace(draft([3,5],str_repeat('봄',100)),['max_temp_threshold'=>'29.12','memo'=>str_repeat('가',2000)]));save_plan(db(),$d,$id);$got=get_plan(db(),$id);foreach($d as $key=>$v)check($got[$key]==$v,$key);return ['id'=>$id,'replacement_locations'=>$got['location_ids'],'unicode_title_chars'=>text_length($got['plan_name']),'unicode_memo_chars'=>text_length($got['memo']),'identical_update'=>'accepted'];}finally{remove_if_exists($id);}
});
test_case('T23','Delete cascades selected locations while preserving another plan',function(){
    $a=$b=null;try{$a=save_plan(db(),validate_plan(draft([1,2])));$b=save_plan(db(),validate_plan(draft([3])));delete_plan(db(),$a);check(get_plan(db(),$a)===null,'Parent gone');check(!run_query(db(),'SELECT * FROM plan_locations WHERE plan_id=?',[$a]),'Links gone');check(get_plan(db(),$b)!==null,'Other parent remains');return ['deleted_parent'=>$a,'remaining_links'=>0,'other_plan'=>$b];}finally{remove_if_exists($a);remove_if_exists($b);}
});
test_case('T24','FK failure after successful parent INSERT leaves no parent or partial links',function(){
    $name='rollback-create-'.bin2hex(random_bytes(6));$d=draft([1,99],$name);
    $before=(int)db()->query("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='saved_plans'")->fetchColumn();
    try{save_plan(db(),$d);throw new RuntimeException('Expected actual FK failure');}catch(PDOException $e){check($e->getCode()==='23000' && str_contains($e->getMessage(),'fk_plan_location'),'Real child FK failure');}
    $after=(int)db()->query("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='saved_plans'")->fetchColumn();
    check($after>$before,'Auto increment proves parent insertion occurred');check(!run_query(db(),'SELECT * FROM saved_plans WHERE plan_name=?',[$name]),'No residual parent');check(!run_query(db(),'SELECT * FROM plan_locations WHERE plan_id=?',[$before]),'No residual first child');check(!db()->inTransaction(),'Transaction closed');
    return ['failure'=>'SQLSTATE 23000 fk_plan_location','auto_increment_before'=>$before,'auto_increment_after'=>$after,'residual_parent'=>0,'residual_links'=>0,'failure_boundary'=>'normalized repository call in CLI; never exposed on web'];
});
test_case('T25','FK failure after UPDATE and child DELETE restores original body and locations',function(){
    $id=null;try{$id=save_plan(db(),validate_plan(draft([1,3],'original rollback body')));$before=get_plan(db(),$id);
        try{save_plan(db(),draft([2,99],'changed body must roll back'),$id);throw new RuntimeException('Expected actual FK failure');}catch(PDOException $e){check($e->getCode()==='23000' && str_contains($e->getMessage(),'fk_plan_location'),'Child FK failed after update/delete');}
        $after=get_plan(db(),$id);check($before===$after,'Exact original parent and links restored');return ['plan_id'=>$id,'restored_name'=>$after['plan_name'],'restored_locations'=>$after['location_ids'],'exact_snapshot_match'=>true];
    }finally{remove_if_exists($id);}
});
finish_tests();
