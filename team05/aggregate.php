<?php
// Implementation: Codex. R10 complex grouping, independently checked against raw CSVs.
require __DIR__ . '/includes/bootstrap.php';
require __DIR__ . '/includes/queries.php';
[$f,$o,$error] = analysis_context('aggregate');
$rows = $error ? [] : run_query(db(), ...aggregate_query($f,$o));
page_header('Temperature Comparison', 'aggregate', 'Compare the same period across locations. Group daily records by year or month and see how often your conditions were met.');
alert_error($error);
filters_form('aggregate',$f,$o);
scope_note($f);
if (!$error): ?>
<div class="section-heading"><h2>Across places &amp; periods</h2><span><?=count($rows)?> groups · <?=e($o['group_mode'] === 'location_year' ? 'location × year' : 'location × year × month')?></span></div>
<p class="caption">Groups cover the selected dates only; an annual row may represent a partial year. Exceedance counts use daily maximum &gt; your limit. Daily range is the daily maximum minus the daily minimum.</p>
<?php stats_table($rows,$o['group_mode']==='location_year_month'); endif;
page_footer();
