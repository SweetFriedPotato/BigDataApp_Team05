<?php
// Implementation: Codex. P4 skeleton; completed in its feature milestone.
require __DIR__ . '/includes/bootstrap.php';
[$f,$o,$error] = analysis_context('ranking');
page_header('Find My Season', 'ranking');
alert_error($error);
filters_form('ranking',$f,$o);
scope_note($f);
echo '<p>This feature is being implemented in the next sequential milestone.</p>';
page_footer();
