<?php
// Implementation: Codex. P4 skeleton; completed in its feature milestone.
require __DIR__ . '/includes/bootstrap.php';
[$f,$o,$error] = analysis_context('aggregate');
page_header('Temperature Comparison', 'aggregate');
alert_error($error);
filters_form('aggregate',$f,$o);
scope_note($f);
echo '<p>This feature is being implemented in the next sequential milestone.</p>';
page_footer();
