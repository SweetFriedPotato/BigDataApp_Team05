<?php
// Team responsibility: Sumin Cho (2376274) — Plan CRUD, saved_plans/plan_locations; transactions, rollback and saving UX.
// Implementation: Codex. Used for GET form display and validation-error redisplay.
require_once __DIR__ . '/includes/bootstrap.php';
require_once __DIR__ . '/includes/plans.php';
$id=$form_id ?? null;
try {
    if ($id===null && isset($_GET['id'])) $id=plan_id($_GET,'id');
    $existing=$id===null ? null : get_plan(db(),$id);
    if ($id!==null && !$existing) throw new OutOfBoundsException('Plan not found.');
} catch (InvalidArgumentException|OutOfBoundsException $e) {
    http_response_code(404);page_header('Plan not found','plans');echo '<p>The requested plan does not exist.</p>';page_footer();exit;
}
$draft=$existing ?? array_merge($_SESSION['analysis_filters'] ?? default_filters(),['plan_name'=>'','memo'=>'']);
if (isset($form_input)) $draft=display_draft($form_input,$draft);
page_header($id===null ? 'Create a Plan' : 'Edit Plan','plans','Save your comparison conditions in this shared demonstration space.');
if(isset($form_error)): ?><div class="notice error" role="alert"><?=e($form_error)?> Nothing was saved.</div><?php endif; ?>
<form method="post" action="plan_actions.php" class="panel plan-form">
<input type="hidden" name="csrf_token" value="<?=e(csrf_token())?>"><input type="hidden" name="action" value="<?= $id===null ? 'create' : 'update' ?>">
<?php if($id!==null): ?><input type="hidden" name="plan_id" value="<?=e($id)?>"><?php endif; ?>
<label class="field"><span>Plan name · 1–100 characters</span><input type="text" name="plan_name"<?=field_attrs('plan_name')?> maxlength="100" value="<?=e($draft['plan_name'])?>" required><?php field_error_view('plan_name'); ?></label>
<?php filter_fields($draft); ?>
<label class="field"><span>Memo · optional · up to 2,000 characters</span><textarea name="memo"<?=field_attrs('memo')?> maxlength="2000" rows="5"><?=e($draft['memo'])?></textarea><?php field_error_view('memo'); ?></label>
<div class="actions"><button class="button"><?= $id===null ? 'Save plan' : 'Save changes' ?> ↗</button><a class="button secondary" href="<?=e($id===null ? 'plans.php' : url('plan_detail.php',['id'=>$id]))?>">Cancel</a></div></form>
<p class="caption">This stores your common conditions. Page settings such as grouping level, Top N rank and moving average focus are not part of a saved plan.</p>
<?php page_footer(); ?>
