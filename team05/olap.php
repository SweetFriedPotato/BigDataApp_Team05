<?php
// Implementation: Codex. Real hierarchical queries and MariaDB WITH ROLLUP totals.
require __DIR__ . '/includes/bootstrap.php';
require __DIR__ . '/includes/queries.php';
[$f,$o,$error] = analysis_context('olap');
$rows = $error ? [] : run_query(db(),...olap_query($f,$o));
$totals = $error ? [] : run_query(db(),...rollup_query($f,$o));
page_header('Temperature Explorer','olap','Follow the data from a year to a month to a day. Move back up to see how each detail fits into the selected period.');
alert_error($error); filters_form('olap',$f,$o); scope_note($f);
if (!$error):
[$scanStart,$scanEnd] = olap_bounds($f,$o); ?>
<nav class="breadcrumb" aria-label="Exploration path"><a href="olap.php?level=year">All selected years</a><?php if ($o['level']!=='year'): ?><span aria-hidden="true">/</span><a href="<?=e(url('olap.php',['level'=>'month','drill_year'=>$o['drill_year']]))?>"><?=e($o['drill_year'])?></a><?php endif; ?><?php if ($o['level']==='day'): ?><span aria-hidden="true">/</span><span><?=e(sprintf('%02d',$o['drill_month']))?></span><?php endif; ?></nav>
<p class="caption">Drill selections intersect your common date range. <?= $scanStart <= $scanEnd ? 'Current intersection: '.e($scanStart).' → '.e($scanEnd).'.' : 'The drill selection has no overlap with your date range.' ?></p>
<div class="section-heading"><h2><?=e(ucfirst($o['level']))?> view</h2><span><?=count($rows)?> records or groups</span></div>
<?php if ($o['level'] !== 'day' && $rows): ?>
<div class="panel"><p class="eyebrow">DRILL DOWN · CHOOSE A PERIOD</p><div class="actions">
<?php $links=[]; foreach($rows as $r){$key=$r['year_no'].($o['level']==='month' ? '-'.$r['month_no'] : '');if(isset($links[$key]))continue;$links[$key]=true;
$args=['level'=>$o['level']==='year' ? 'month':'day','drill_year'=>$r['year_no']];if($o['level']==='month')$args['drill_month']=$r['month_no']; ?>
<a class="button secondary" href="<?=e(url('olap.php',$args))?>"><?=e($key)?> ↘</a><?php } ?></div></div>
<?php stats_table($rows,$o['level']==='month');
elseif ($o['level']==='day' && $rows): ?>
<div class="table-wrap"><table><caption class="sr-only">Daily records for the selected month</caption><thead><tr><th>Location</th><th>Date · LST</th><th>Mean °C</th><th>Maximum °C</th><th>Minimum °C</th><th>Daily range °C</th><th>Valid</th><th>Matches limits</th></tr></thead><tbody>
<?php foreach($rows as $r): ?><tr><th scope="row"><?=e($r['name_en'])?></th><td><?=e($r['weather_date'])?></td><td><?=num($r['tmean'])?></td><td><?=num($r['tmax'])?></td><td><?=num($r['tmin'])?></td><td><?=num($r['dtr'])?></td><td><?= $r['valid_flag'] ? 'Yes' : 'No' ?></td><td><?= $r['valid_flag'] ? ($r['matching_flag'] ? 'Yes':'No') : '—' ?></td></tr><?php endforeach; ?></tbody></table></div>
<?php else: empty_state('This drill selection does not overlap the selected data. Use the exploration path to return to a wider level.'); endif; ?>
<div class="section-heading"><h2>The bigger picture</h2><span>SQL WITH ROLLUP</span></div>
<p class="caption">Annual and location subtotals are recomputed from daily records. All selected locations totals count location-days; one date in five locations contributes five records. NULL dimensions identify subtotals.</p>
<details open><summary>Monthly groups, annual subtotals, location subtotals &amp; all selected locations</summary><?php stats_table($totals,true,true); ?></details>
<?php endif; page_footer(); ?>
