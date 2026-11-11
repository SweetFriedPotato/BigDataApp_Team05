<?php
// Team responsibility: Koo Daon (2476009) — Complex Grouping, OLAP and ROLLUP; valid-day/weighted summaries and hierarchy verification.
// Implementation: Codex. R10 complex grouping, independently checked against raw CSVs.
require __DIR__ . '/includes/bootstrap.php';
require __DIR__ . '/includes/queries.php';
[$f,$o,$error] = analysis_context('aggregate');
$rows = $error ? [] : run_query(db(), ...aggregate_query($f,$o));
page_header('Temperature Comparison', 'aggregate', 'Compare the same dates by location and period.');
alert_error($error);
filters_form('aggregate',$f,$o);
scope_note($f);
if (!$error): ?>
<div class="section-heading"><h2>Comparison results</h2><span><?=count($rows)?> groups · <?=e($o['group_mode'] === 'location_year' ? 'location × year' : 'location × year × month')?></span></div>
<p class="caption">Only selected dates are included. Year groups may cover a partial year.</p>
<?php stats_table($rows,$o['group_mode']==='location_year_month'); endif;
page_footer();
