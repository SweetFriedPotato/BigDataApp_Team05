<?php
// Implementation: Codex. Unrounded rates determine dense ranks; Top N includes every tie.
require __DIR__ . '/includes/bootstrap.php';
require __DIR__ . '/includes/queries.php';
[$f,$o,$error] = analysis_context('ranking');
$rows = $error ? [] : run_query(db(),...ranking_query($f,$o));
page_header('Find My Season','ranking','Which places met your temperature limits most often? Compare the share of valid days, with equal rates sharing the same rank.');
alert_error($error); filters_form('ranking',$f,$o); scope_note($f);
if (!$error): ?>
<div class="section-heading"><h2>A match for your conditions</h2><span>Top <?=e($o['top_rank'])?> ranks · ties included</span></div>
<p class="caption">Matching rate = matching days ÷ valid days × 100. At least <?=e($o['min_valid_days'])?> valid days required. Places with zero or insufficient valid days are excluded. Dense ranks use full precision; displayed percentages are rounded to two decimal places.</p>
<?php if (!$rows): empty_state(); else: ?>
<div class="table-wrap"><table><caption class="sr-only">Locations ranked by the matching rate for your selected dates</caption><thead><tr><th>Rank</th><th>Location</th><th>Matching days</th><th>Valid days</th><th>Matching rate</th><th>Selected period · LST</th></tr></thead><tbody>
<?php foreach($rows as $r): ?><tr><td><span class="rank-badge <?= (int)$r['rank_no']===1 ? 'rank-first' : '' ?>"><?=e($r['rank_no'])?></span></td><th scope="row"><?=e($r['name_en'])?></th><td><?=num($r['matching_days'],0)?></td><td><?=num($r['valid_days'],0)?></td><td><strong><?=num($r['matching_rate'])?>%</strong></td><td><?=e($f['start_date'])?> → <?=e($f['end_date'])?></td></tr><?php endforeach; ?></tbody></table></div>
<p class="caption">These limits are your preferences. This comparison describes historical temperatures; it does not establish travel safety, health benefits, or overall comfort.</p>
<?php endif; endif; page_footer(); ?>
