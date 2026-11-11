<?php
// Implementation: Codex. Presentation only; numerical analysis is performed by MariaDB.
declare(strict_types=1);
function e(mixed $value): string { return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function num(mixed $value, int $places = 2): string { return $value === null ? '—' : number_format((float)$value, $places); }
function locations(): array { return run_query(db(), 'SELECT * FROM locations ORDER BY location_id'); }
function url(string $file, array $args = []): string { return $file . ($args ? '?' . http_build_query($args) : ''); }
function page_header(string $title, string $page, string $intro = ''): void {
    require __DIR__ . '/header.php';
}
function page_footer(): void { require __DIR__ . '/footer.php'; }
function alert_error(?string $error): void {
    if ($error !== null) echo '<div class="notice error" role="alert">' . e($error) . ' No analysis was run. Your saved session filters were kept.</div>';
}
function select_control(string $name, string $label, array $choices, mixed $value): void {
    echo '<label class="field"><span>' . e($label) . '</span><select name="' . e($name) . '">';
    foreach ($choices as $key => $text) echo '<option value="' . e($key) . '"' . ((string)$key === (string)$value ? ' selected' : '') . '>' . e($text) . '</option>';
    echo '</select></label>';
}
function filter_fields(array $f): void { ?>
    <div class="field-row">
        <label class="field"><span>From · LST</span><input type="date" name="start_date" min="2023-01-01" max="2025-12-31" value="<?=e($f['start_date'])?>" required></label>
        <label class="field"><span>To · LST</span><input type="date" name="end_date" min="2023-01-01" max="2025-12-31" value="<?=e($f['end_date'])?>" required></label>
        <label class="field"><span>Daily maximum ≤ °C</span><input type="number" name="max_temp_threshold" min="-50" max="60" step="0.01" value="<?=e($f['max_temp_threshold'])?>" required></label>
        <label class="field"><span>Daily range ≤ °C</span><input type="number" name="max_temp_range" min="0" max="60" step="0.01" value="<?=e($f['max_temp_range'])?>" required></label>
    </div>
    <fieldset class="regions"><legend>Compare locations <span>Select one or more requested points</span></legend>
    <?php foreach (locations() as $l): ?><label class="region"><input type="checkbox" name="location_ids[]" value="<?=e($l['location_id'])?>"<?=in_array((int)$l['location_id'], $f['location_ids'], true) ? ' checked' : ''?>><span><?=e($l['name_en'])?> <small lang="ko"><?=e($l['name_ko'])?></small></span></label><?php endforeach; ?>
    </fieldset>
<?php }
function filters_form(string $page, array $f, array $o): void { ?>
<section class="panel filters" aria-label="Analysis filters"><form method="get">
<input type="hidden" name="apply_filters" value="1">
<?php filter_fields($f); ?>
<div class="options-row">
<?php
switch ($page) {
    case 'aggregate': select_control('group_mode','Group records by',['location_year_month'=>'Location · year · month','location_year'=>'Location · year'],$o['group_mode']); break;
    case 'olap':
        select_control('level','Explore level',['year'=>'Year','month'=>'Month','day'=>'Day'],$o['level']);
        select_control('drill_year','Drill year',[2023=>2023,2024=>2024,2025=>2025],$o['drill_year']);
        select_control('drill_month','Drill month',array_combine(range(1,12),range(1,12)),$o['drill_month']); break;
    case 'ranking':
        select_control('top_rank','Show ranks',[1=>'Top 1 · includes ties',2=>'Top 2 · includes ties',3=>'Top 3 · includes ties',4=>'Top 4 · includes ties',5=>'All 5 ranks'],$o['top_rank']);
        echo '<label class="field"><span>Minimum valid days</span><input type="number" name="min_valid_days" min="1" max="1096" value="'.e($o['min_valid_days']).'" required></label>'; break;
    case 'window':
        select_control('metric','Temperature metric',['mean'=>'Daily mean','max'=>'Daily maximum','min'=>'Daily minimum','range'=>'Daily range'],$o['metric']);
        select_control('window_days','Highlight moving average',[7=>'7 days',30=>'30 days'],$o['window_days']); break;
}
?>
<button class="button" type="submit">Apply filters <span aria-hidden="true">↗</span></button>
<button class="button secondary" type="submit" name="intent" value="save">Save conditions</button>
</div></form>
<form class="reset-form" method="post"><input type="hidden" name="csrf_token" value="<?=e(csrf_token())?>"><button class="text-button" name="reset_filters" value="1">Reset analysis filters</button></form>
</section>
<?php }
function scope_note(array $f, array $o = []): void {
    $names = array_column(array_filter(locations(), fn($l) => in_array((int)$l['location_id'], $f['location_ids'], true)), 'name_en'); ?>
<div class="scope"><span class="dot"></span><strong><?=e($f['start_date'])?> → <?=e($f['end_date'])?></strong><span><?=e(implode(' · ', $names))?></span><span>Maximum ≤ <?=e($f['max_temp_threshold'])?>°C · range ≤ <?=e($f['max_temp_range'])?>°C</span></div>
<p class="caption">Valid day = all three temperatures present. Match = both limits satisfied. Means use all valid days, including days that do not match. Dates use Local Solar Time (LST).</p>
<?php }
function empty_state(string $message = 'No records match this selection. Try another period or a lower minimum day count.'): void {
    echo '<div class="empty"><span aria-hidden="true">○</span><h2>No results for these conditions</h2><p>'.e($message).'</p></div>';
}
function stats_table(array $rows, bool $show_month = true, bool $rollup = false): void {
    if (!$rows) { empty_state(); return; }
    echo '<div class="table-wrap"><table><caption class="sr-only">Temperature statistics computed by MariaDB</caption><thead><tr><th scope="col">Location</th><th scope="col">Year</th>';
    if ($show_month) echo '<th scope="col">Month</th>';
    foreach (['Valid days','Mean °C','Mean max °C','Mean min °C','Mean range °C','Period high °C','Period low °C','Exceedance days','Matching days','Match %'] as $label) echo '<th scope="col">'.e($label).'</th>';
    echo '</tr></thead><tbody>';
    foreach ($rows as $r) {
        $subtotal = $rollup && ($r['location_id'] === null || $r['year_no'] === null || $r['month_no'] === null);
        $label = $r['name_en'] ?? 'All selected locations';
        if ($subtotal && $r['location_id'] !== null) $label .= $r['year_no'] === null ? ' · Location subtotal' : ' · Annual subtotal';
        echo '<tr'.($subtotal ? ' class="subtotal"' : '').'><th scope="row">'.e($label).'</th><td>'.e($r['year_no'] ?? 'All years').'</td>';
        if ($show_month) echo '<td>'.e($r['month_no'] ?? 'All months').'</td>';
        foreach (['valid_days','mean_temperature','mean_daily_max','mean_daily_min','mean_daily_range','period_high','period_low','exceedance_days','matching_days','matching_rate'] as $key) echo '<td>'.num($r[$key],in_array($key,['valid_days','exceedance_days','matching_days']) ? 0 : 2).'</td>';
        echo '</tr>';
    }
    echo '</tbody></table></div>';
}
