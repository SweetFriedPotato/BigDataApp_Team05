<?php
// Team responsibility: Jihee Choi (2276337) — Ranking/Windowing; ties, denominators, continuous dates and line-chart verification.
// Implementation: Codex. Windows scan continuous history before filtering the displayed dates.
require __DIR__ . '/includes/bootstrap.php';
require __DIR__ . '/includes/queries.php';
require __DIR__ . '/includes/chart.php';
[$f,$o,$error] = analysis_context('window');
$rows = $error ? [] : run_query(db(),...window_query($f,$o));
page_header('Temperature Trends','window','Compare daily values with continuous 7 and 30 day averages.');
alert_error($error); filters_form('window',$f,$o); scope_note($f);
if ($error && field_error('chart_location')): ?>
<form method="get" class="panel options-row"><?php $choices=[];foreach(locations() as $l)if(in_array((int)$l['location_id'],$f['location_ids'],true))$choices[$l['location_id']]=$l['name_en'];select_control('chart_location','Graph location',$choices,$o['chart_location']); ?><button class="button secondary">Show graph</button></form>
<?php endif;
if (!$error): ?>
<div class="section-heading"><h2>Daily values &amp; averages</h2><span><?=e(ucfirst($o['metric']))?> temperature · <?=e($o['window_days'])?> day focus</span></div>
<p class="caption">Averages include earlier history. Insufficient or missing history stays blank.</p>
<?php if (!$rows): empty_state(); else: ?>
<div class="scope"><?php $seen=[]; foreach($rows as $r): if(isset($seen[$r['location_id']]))continue;$seen[$r['location_id']]=true; ?><span><?=e($r['name_en'])?>: <strong><?=num($r['display_valid_days'],0)?> valid display days</strong></span><?php endforeach; ?></div>
<?php render_trend_chart($rows,$f,$o); ?>
<div class="table-wrap"><table><caption class="sr-only">Daily temperature and continuous moving averages, in degrees Celsius</caption><thead><tr><th>Location</th><th>Date · LST</th><th><?=e(ucfirst($o['metric']))?> °C</th><th>7 day mean °C</th><th>Valid / 7</th><th>30 day mean °C</th><th>Valid / 30</th><th>Matches limits</th></tr></thead><tbody>
<?php foreach($rows as $r): ?><tr><th scope="row"><?=e($r['name_en'])?></th><td><?=e($r['weather_date'])?></td><td><?=num($r['metric_value'])?></td><td<?= $o['window_days']===7 ? ' class="highlight"' : '' ?>><?= $r['ma7']===null ? 'Insufficient history' : num($r['ma7']) ?></td><td><?=e($r['n7'])?> / 7</td><td<?= $o['window_days']===30 ? ' class="highlight"' : '' ?>><?= $r['ma30']===null ? 'Insufficient history' : num($r['ma30']) ?></td><td><?=e($r['n30'])?> / 30</td><td><?= $r['valid_flag'] ? ($r['matching_flag'] ? 'Yes' : 'No') : '—' ?></td></tr><?php endforeach; ?></tbody></table></div>
<p class="caption">Insufficient history also covers a gap in the daily date sequence. The source begins on 2023-01-01; its first 6 and 29 days cannot have complete 7 and 30 day averages respectively.</p>
<?php endif; endif; page_footer(); ?>
