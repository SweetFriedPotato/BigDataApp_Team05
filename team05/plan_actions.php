<?php
// Implementation: Codex. POST-only actions, validated input, atomic writes and PRG redirects.
require __DIR__ . '/includes/bootstrap.php';
require __DIR__ . '/includes/plans.php';
function action_error(int $status,string $message): void {
    http_response_code($status);page_header('Request could not be completed','plans');
    echo '<div class="notice error" role="alert">'.e($message).'</div><a href="plans.php">Return to saved plans</a>';
    page_footer();exit;
}
if (($_SERVER['REQUEST_METHOD'] ?? '')!=='POST') {header('Allow: POST');action_error(405,'Use a plan form to make changes.');}
try {check_csrf($_POST);}catch(InvalidArgumentException $e){action_error(403,$e->getMessage());}
try {
    $action=scalar_input($_POST,'action');
    if(!in_array($action,['create','update','delete','apply'],true))throw new InvalidArgumentException('Unknown plan action.');
    $id=$action==='create' ? null : plan_id($_POST);
    if($action==='create' || $action==='update') {
        $plan=validate_plan($_POST);$id=save_plan(db(),$plan,$id);
        flash($action==='create' ? 'Plan saved with its selected locations.' : 'Plan and selected locations updated.');
        header('Location: '.url('plan_detail.php',['id'=>$id]),true,303);exit;
    }
    if($action==='delete') {
        delete_plan(db(),$id);flash('Plan and its selected locations deleted.');
        header('Location: plans.php',true,303);exit;
    }
    $target=scalar_input($_POST,'target');
    if(!in_array($target,['aggregate','olap','ranking','window'],true))throw new InvalidArgumentException('Choose an analysis from the list.');
    $plan=get_plan(db(),$id);if(!$plan)throw new OutOfBoundsException('Plan no longer exists.');
    $_SESSION['analysis_filters']=validate_filters($plan);
    flash('Saved comparison conditions applied.');header('Location: '.$target.'.php',true,303);exit;
} catch (InvalidArgumentException $e) {
    if(isset($action) && in_array($action,['create','update'],true)) {
        http_response_code(422);$GLOBALS['validation_errors']=$e instanceof InputValidationException ? [$e->field=>$e->getMessage()] : []; $form_input=$_POST;$form_error=$e->getMessage();$form_id=$id ?? null;
        require __DIR__ . '/plan_form.php';exit;
    }
    action_error(422,$e->getMessage());
} catch (OutOfBoundsException $e) {action_error(404,'The requested plan does not exist.');}
catch (PDOException $e) {error_log('Plan transaction: '.$e->getMessage());action_error(503,'The plan could not be saved. No partial changes were kept. Please try again.');}
