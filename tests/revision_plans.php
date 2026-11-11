<?php
// CLI-only revision fixture. Execute exclusively in a disposable test DB.
require __DIR__ . '/support.php';
require '/workspace/team05/includes/plans.php';
test_case('T35','Regions-only/body-only/identical updates advance timestamp/order; FK failure restores timestamp',function(){
    $a=$b=null;$p=db();
    $plan=array_merge(period_filters('2024-08-01','2024-08-31',[1]),['plan_name'=>'T35 A','memo'=>'unchanged body']);
    try {
        $a=save_plan($p,validate_plan($plan));$b=save_plan($p,validate_plan(array_replace($plan,['plan_name'=>'T35 B'])));
        run_query($p,'UPDATE saved_plans SET updated_at=? WHERE plan_id=?',['2023-01-01 00:00:00',$a]);
        run_query($p,'UPDATE saved_plans SET updated_at=? WHERE plan_id=?',['2024-01-01 00:00:00',$b]);
        $before=get_plan($p,$a);$plan['location_ids']=[2,3];save_plan($p,validate_plan($plan),$a);$after=get_plan($p,$a);
        check($after['updated_at']>$before['updated_at'],'Regions-only save must advance parent updated_at');
        check((int)list_plans($p)[0]['plan_id']===$a,'Regions-only save must move plan to newest position');
        check($after['location_ids']===[2,3] && $after['plan_name']===$before['plan_name'],'Only selected regions changed');
        foreach(['body-only','identical'] as $mode){
            run_query($p,'UPDATE saved_plans SET updated_at=? WHERE plan_id=?',['2023-01-01 00:00:00',$a]);
            if($mode==='body-only')$plan['plan_name']='T35 changed body';
            save_plan($p,validate_plan($plan),$a);check(get_plan($p,$a)['updated_at']>'2023-01-01 00:00:00',$mode.' save advances timestamp');
        }
        run_query($p,'UPDATE saved_plans SET updated_at=? WHERE plan_id=?',['2023-01-01 00:00:00',$a]);$original=get_plan($p,$a);
        try{save_plan($p,array_replace($plan,['plan_name'=>'must rollback','location_ids'=>[2,99]]),$a);throw new RuntimeException('Expected child FK failure');}
        catch(PDOException $e){check($e->getCode()==='23000','Actual FK failure');}
        check(get_plan($p,$a)===$original,'Body/children/timestamp all restored');
        return ['regions_only_updated_at'=>$after['updated_at'],'old_timestamp'=>$before['updated_at'],'newest_plan'=>$a,'body_only'=>'PASS','identical'=>'PASS','failed_save_snapshot_restored'=>true];
    }finally{foreach([$a,$b] as $id)if($id!==null && get_plan($p,$id))delete_plan($p,$id);}
});
finish_tests();
