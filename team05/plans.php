<?php
// Implementation: Codex. Shared demonstration records stored in MariaDB.
require __DIR__ . '/includes/bootstrap.php';
require __DIR__ . '/includes/plans.php';
$rows=list_plans(db());
page_header('Saved Plans','plans','Keep a set of comparison conditions and return to it later. This is a shared demonstration space; every visitor can view and edit these plans.');
?>
<div class="section-heading"><h2>Conditions worth keeping</h2><a class="button" href="plan_form.php">Create a plan <span aria-hidden="true">+</span></a></div>
<?php if (!$rows): empty_state('No plans have been saved yet. Create a plan using your dates, locations and temperature limits.'); else: ?>
<div class="table-wrap"><table><caption class="sr-only">Saved comparison plans</caption><thead><tr><th>Plan</th><th>Period · LST</th><th>Locations</th><th>Maximum / range °C</th><th>Updated · KST</th><th>Actions</th></tr></thead><tbody>
<?php foreach($rows as $r): ?><tr><th scope="row"><a href="<?=e(url('plan_detail.php',['id'=>$r['plan_id']]))?>"><?=e($r['plan_name'])?></a></th><td><?=e($r['start_date'])?> → <?=e($r['end_date'])?></td><td><?=e($r['location_names'])?></td><td><?=e($r['max_temp_threshold'])?> / <?=e($r['max_temp_range'])?></td><td><?=e($r['updated_at'])?></td><td><div class="actions"><a href="<?=e(url('plan_form.php',['id'=>$r['plan_id']]))?>">Edit</a><form method="post" action="plan_actions.php" data-confirm="Delete this plan and its selected locations?"><input type="hidden" name="csrf_token" value="<?=e(csrf_token())?>"><input type="hidden" name="action" value="delete"><input type="hidden" name="plan_id" value="<?=e($r['plan_id'])?>"><button class="text-button">Delete</button></form></div></td></tr><?php endforeach; ?></tbody></table></div>
<?php endif; ?>
<p class="caption">Plans save the title, memo, common dates, locations and two temperature limits. Grouping, ranking display and moving average focus remain page settings.</p>
<?php page_footer(); ?>
