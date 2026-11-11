<?php
// Implementation: Codex. Home values are read from the installed database.
require __DIR__ . '/includes/bootstrap.php';
$counts = run_query(db(), 'SELECT (SELECT COUNT(*) FROM daily_temperatures) weather_rows,(SELECT COUNT(*) FROM locations) locations,(SELECT COUNT(*) FROM solar_terms) terms,(SELECT COUNT(*) FROM monthly_food_guides) foods')[0];
page_header('Compare temperatures across Korea.','index','Explore daily temperatures for five locations, 2023–2025. Choose the dates and limits that matter to you.');
?>
<div class="home-actions"><a class="button" href="aggregate.php">Start comparison</a><a class="button secondary" href="plans.php">Open saved plans</a></div>
<div class="metrics"><div class="metric"><strong><?=num($counts['weather_rows'],0)?></strong><span>Daily temperature records</span></div><div class="metric"><strong><?=num($counts['locations'],0)?></strong><span>Locations to compare</span></div><div class="metric"><strong><?=num($counts['terms'],0)?></strong><span>Solar term dates</span></div></div>
<div class="section-heading"><h2>Choose an analysis</h2><span>Four questions. One set of conditions.</span></div>
<div class="cards">
<?php foreach ([['01 · GROUPING','Temperature Comparison','Compare temperatures, daily ranges and matching rates by location and period.','aggregate.php'],['02 · OLAP','Temperature Explorer','Move from a year to a month to individual days, then return to the totals.','olap.php'],['03 · RANKING','Find My Season','Rank locations by the share of valid days that met both of your limits.','ranking.php'],['04 · WINDOWING','Temperature Trends','Compare daily values with continuous 7 and 30 day moving averages.','window.php']] as [$n,$t,$d,$link]): ?><a class="card" href="<?=e($link)?>"><span class="card-index"><?=e($n)?></span><h3><?=e($t)?></h3><p><?=e($d)?></p><span class="card-link">Open analysis →</span></a><?php endforeach; ?>
</div>
<div class="secondary-links"><a href="seasonal.php">Seasonal information →</a><a href="plan_form.php">Create a comparison plan →</a></div>
<details class="method-note"><summary>About these records</summary><p>NASA POWER historical gridded reanalysis at five requested points, January 2023–December 2025. Dates use Local Solar Time (LST). These are historical grid values rather than station observations or forecasts. Matching rates describe your chosen limits. Calendar dates use KASI references; <?=num($counts['foods'],0)?> RDA monthly ingredient items are independent editorial guides.</p><p><a href="https://power.larc.nasa.gov/docs/services/api/temporal/daily/" target="_blank" rel="noopener noreferrer">NASA POWER source documentation</a></p></details>
<?php page_footer(); ?>
