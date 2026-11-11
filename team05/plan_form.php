<?php
// Implementation: Codex. P4 skeleton; completed in its feature milestone.
require __DIR__ . '/includes/bootstrap.php';
[$f,$o,$error] = analysis_context('plan_form');
page_header('Create / Edit Plan', 'plans');
alert_error($error);
echo '<p>This feature is being implemented in the next sequential milestone.</p>';
page_footer();
