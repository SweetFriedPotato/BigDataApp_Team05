<?php
// Implementation: Codex. SQL alone computes grouping, rollups, ranks and moving averages.
declare(strict_types=1);
function base_cte(array $f, ?string $start = null, ?string $end = null): array {
    $marks = implode(',', array_fill(0, count($f['location_ids']), '?'));
    $sql = "WITH params AS (SELECT CAST(? AS DECIMAL(6,2)) max_limit, CAST(? AS DECIMAL(6,2)) range_limit),
    source AS (
        SELECT d.*, tmax-tmin AS dtr,
        CASE WHEN tmean IS NOT NULL AND tmax IS NOT NULL AND tmin IS NOT NULL THEN 1 ELSE 0 END AS valid_flag
        FROM daily_temperatures d
        WHERE weather_date BETWEEN ? AND ? AND location_id IN ($marks)
    ), base AS (
        SELECT s.*, YEAR(weather_date) year_no, MONTH(weather_date) month_no,
        CASE WHEN valid_flag=1 AND tmax<=p.max_limit AND dtr<=p.range_limit THEN 1 ELSE 0 END matching_flag,
        CASE WHEN valid_flag=1 AND tmax>p.max_limit THEN 1 ELSE 0 END exceedance_flag
        FROM source s CROSS JOIN params p
    )";
    return [$sql, [$f['max_temp_threshold'], $f['max_temp_range'], $start ?? $f['start_date'], $end ?? $f['end_date'], ...$f['location_ids']]];
}
function statistics_sql(): string {
    return 'COUNT(*) candidate_days, SUM(valid_flag) valid_days,
        AVG(CASE WHEN valid_flag=1 THEN tmean END) mean_temperature,
        AVG(CASE WHEN valid_flag=1 THEN tmax END) mean_daily_max,
        AVG(CASE WHEN valid_flag=1 THEN tmin END) mean_daily_min,
        AVG(CASE WHEN valid_flag=1 THEN dtr END) mean_daily_range,
        MAX(CASE WHEN valid_flag=1 THEN tmax END) period_high,
        MIN(CASE WHEN valid_flag=1 THEN tmin END) period_low,
        SUM(exceedance_flag) exceedance_days, SUM(matching_flag) matching_days,
        100.0*SUM(matching_flag)/NULLIF(SUM(valid_flag),0) matching_rate';
}
function aggregate_query(array $f, array $o): array {
    [$sql,$params] = base_cte($f);
    $month = match ($o['group_mode']) {
        'location_year_month' => true, 'location_year' => false,
        default => throw new InvalidArgumentException('Unknown grouping.'),
    };
    $dimensions = 'location_id, year_no' . ($month ? ', month_no' : '');
    $sql .= ', grouped AS (SELECT ' . $dimensions . ', ' . statistics_sql() . ' FROM base GROUP BY ' . $dimensions . ')
        SELECT g.*, l.name_en FROM grouped g JOIN locations l ON l.location_id=g.location_id
        ORDER BY g.location_id, g.year_no' . ($month ? ', g.month_no' : '');
    return [$sql,$params];
}
function olap_bounds(array $f, array $o): array {
    $start = $f['start_date']; $end = $f['end_date'];
    if ($o['level'] !== 'year') {
        $year = integer_input($o,'drill_year',2023,2025);
        if ($o['level'] === 'month') {
            $start = max($start, sprintf('%04d-01-01',$year));
            $end = min($end, sprintf('%04d-12-31',$year));
        } elseif ($o['level'] === 'day') {
            $month = integer_input($o,'drill_month',1,12);
            $first = new DateTimeImmutable(sprintf('%04d-%02d-01',$year,$month));
            $start = max($start,$first->format('Y-m-d'));
            $end = min($end,$first->modify('last day of this month')->format('Y-m-d'));
        } else throw new InvalidArgumentException('Unknown OLAP level.');
    }
    return [$start,$end];
}
function olap_query(array $f, array $o): array {
    [$start,$end] = olap_bounds($f,$o);
    if ($o['level'] !== 'day') {
        return aggregate_query(array_replace($f,['start_date'=>$start,'end_date'=>$end]),
            ['group_mode'=>$o['level']==='year' ? 'location_year' : 'location_year_month']);
    }
    [$sql,$params] = base_cte($f,$start,$end);
    return [$sql.' SELECT b.*,l.name_en FROM base b JOIN locations l ON l.location_id=b.location_id ORDER BY b.location_id,b.weather_date',$params];
}
function rollup_query(array $f, array $o): array {
    [$start,$end] = olap_bounds($f,$o);
    [$sql,$params] = base_cte($f,$start,$end);
    $sql .= ', totals AS (SELECT location_id,year_no,month_no,' . statistics_sql() . '
        FROM base GROUP BY location_id,year_no,month_no WITH ROLLUP)
        SELECT t.*,l.name_en FROM totals t LEFT JOIN locations l ON l.location_id=t.location_id
        ORDER BY (t.location_id IS NULL),t.location_id,(t.year_no IS NULL),t.year_no,(t.month_no IS NULL),t.month_no';
    return [$sql,$params];
}
