<?php
// Implementation: Codex. Dated calendar reference and independent monthly editorial guide.
require __DIR__ . '/includes/bootstrap.php';
require __DIR__ . '/includes/queries.php';
[$f,$o,$error] = analysis_context('seasonal');
$data=$error ? ['terms'=>[],'foods'=>[]] : seasonal_data(db(),$o);
$monthName=(new DateTimeImmutable(sprintf('%04d-%02d-01',$o['year'],$o['month'])))->format('F');
page_header('Seasonal Information','seasonal','A calendar companion to your temperature comparisons. Explore solar term dates and a monthly ingredient guide, each with its own source.');
if($error): ?><div class="notice error" role="alert"><?=e($error)?> No reference query was run.</div><?php endif; ?>
<form method="get" class="panel options-row"><?php select_control('year','Calendar year',[2023=>2023,2024=>2024,2025=>2025],$o['year']);select_control('month','Month',array_combine(range(1,12),array_map(fn($m)=>(new DateTimeImmutable('2025-'.$m.'-01'))->format('F'),range(1,12))),$o['month']); ?><button class="button">Explore month ↗</button></form>
<?php if(!$error): ?>
<div class="section-heading"><h2><?=e($monthName)?> <?=e($o['year'])?></h2><span>CALENDAR &amp; MONTHLY GUIDE</span></div>
<div class="two-column"><section class="panel"><p class="eyebrow">01 / SOLAR TERMS</p><div class="season-marker" aria-hidden="true">◷</div><h2>A moment in the season</h2><p class="caption">KASI calendar reference dates. Dates vary by year. Exact transition times are outside this guide.</p>
<?php if(!$data['terms']): empty_state('No solar terms are stored for this month.'); else: ?><ul class="term-list"><?php foreach($data['terms'] as $term): ?><li><div><strong lang="ko"><?=e($term['term_name'])?></strong><br><time datetime="<?=e($term['term_date'])?>"><?=e($term['term_date'])?></time></div><a href="<?=e($term['source_url'])?>" target="_blank" rel="noopener noreferrer">KASI reference ↗</a></li><?php endforeach; ?></ul><?php endif; ?>
<p class="caption">This is the public calendar reference, with no final official almanac cross-check. Calendar dates and NASA LST daily averages are separate references.</p></section>
<section class="panel"><p class="eyebrow">02 / MONTHLY INGREDIENT GUIDE</p><div class="season-marker" aria-hidden="true">✳</div><h2>A note for your table</h2>
<?php if(!$data['foods']): empty_state('No verified monthly ingredient guide is stored for this month.'); else: foreach($data['foods'] as $food): ?><p class="food-name" lang="ko"><?=e($food['food_name'])?></p><a href="<?=e($food['source_url'])?>" target="_blank" rel="noopener noreferrer">RDA monthly feature ↗</a><?php endforeach; endif; ?>
<p class="caption">A historical RDA “ingredient of the month” editorial selection. This guide is independent of location temperatures and does not establish local harvest timing or food availability in <?=e($o['year'])?>. It contains month, ingredient and source only.</p></section></div>
<section class="panel"><p class="eyebrow">KEEP EXPLORING</p><h2>See the same month in temperature.</h2><p>Use the analysis filters to compare the dates and locations that interest you. This calendar does not change your saved temperature conditions.</p><div class="actions"><a class="button secondary" href="aggregate.php">Compare temperatures ↗</a><a href="window.php">Follow daily trends ↗</a></div></section>
<?php endif; page_footer(); ?>
