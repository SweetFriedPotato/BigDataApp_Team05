<?php
// Implementation: Codex. SQL alone computes grouping, rollups, ranks and moving averages.
declare(strict_types=1);
// Team responsibility: Koo Daon (2476009) — Shared analysis helpers are reviewed by Koo Daon and Jihee Choi.
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
// Team responsibility: Koo Daon (2476009) — Assigned module responsibility; implementation history remains unchanged.
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
// Team responsibility: Koo Daon (2476009) — Assigned module responsibility; implementation history remains unchanged.
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
// Team responsibility: Koo Daon (2476009) — Assigned module responsibility; implementation history remains unchanged.
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
// Team responsibility: Koo Daon (2476009) — Assigned module responsibility; implementation history remains unchanged.
function olap_query(array $f, array $o): array {
    [$start,$end] = olap_bounds($f,$o);
    if ($o['level'] !== 'day') {
        return aggregate_query(array_replace($f,['start_date'=>$start,'end_date'=>$end]),
            ['group_mode'=>$o['level']==='year' ? 'location_year' : 'location_year_month']);
    }
    [$sql,$params] = base_cte($f,$start,$end);
    return [$sql.' SELECT b.*,l.name_en FROM base b JOIN locations l ON l.location_id=b.location_id ORDER BY b.location_id,b.weather_date',$params];
}
// Team responsibility: Koo Daon (2476009) — Assigned module responsibility; implementation history remains unchanged.
function rollup_query(array $f, array $o): array {
    [$start,$end] = olap_bounds($f,$o);
    [$sql,$params] = base_cte($f,$start,$end);
    $sql .= ', totals AS (SELECT location_id,year_no,month_no,' . statistics_sql() . '
        FROM base GROUP BY location_id,year_no,month_no WITH ROLLUP)
        SELECT t.*,l.name_en FROM totals t LEFT JOIN locations l ON l.location_id=t.location_id
        ORDER BY (t.location_id IS NULL),t.location_id,(t.year_no IS NULL),t.year_no,(t.month_no IS NULL),t.month_no';
    return [$sql,$params];
}
// Team responsibility: Jihee Choi (2276337) — Assigned module responsibility; implementation history remains unchanged.
function ranking_query(array $f, array $o): array {
    $minDays = integer_input($o,'min_valid_days',1,1096);
    $topRank = integer_input($o,'top_rank',1,5);
    [$sql,$params] = base_cte($f);
    $sql .= ', counts AS (
        SELECT location_id,SUM(valid_flag) valid_days,SUM(matching_flag) matching_days
        FROM base GROUP BY location_id
    ), rates AS (
        SELECT c.*,100*CAST(matching_days AS DECIMAL(30,16))/valid_days matching_rate
        FROM counts c WHERE valid_days>=? AND valid_days>0
    ), ranked AS (
        SELECT r.*,DENSE_RANK() OVER (ORDER BY matching_rate DESC) rank_no FROM rates r
    ) SELECT r.*,l.name_en FROM ranked r JOIN locations l ON l.location_id=r.location_id
      WHERE r.rank_no<=? ORDER BY r.rank_no,r.location_id';
    return [$sql,[...$params,$minDays,$topRank]];
}
// Team responsibility: Jihee Choi (2276337) — Assigned module responsibility; implementation history remains unchanged.
function window_query(array $f, array $o): array {
    $metric = match ($o['metric']) {
        'mean' => 'tmean', 'max' => 'tmax', 'min' => 'tmin', 'range' => 'dtr',
        default => throw new InvalidArgumentException('Unknown temperature metric.'),
    };
    if (!in_array($o['window_days'],[7,30],true)) throw new InvalidArgumentException('Unknown window.');
    $scan = max(DATA_START, (new DateTimeImmutable($f['start_date']))->modify('-29 days')->format('Y-m-d'));
    [$sql,$params] = base_cte($f,$scan,$f['end_date']);
    $sql .= ', metrics AS (SELECT b.*,CASE WHEN valid_flag=1 THEN ' . $metric . ' END metric_value FROM base b),
    framed AS (
        SELECT m.*,AVG(metric_value) OVER w7 mean7,COUNT(metric_value) OVER w7 n7,
        AVG(metric_value) OVER w30 mean30,COUNT(metric_value) OVER w30 n30,
        MIN(weather_date) OVER w7 first7,MIN(weather_date) OVER w30 first30
        FROM metrics m WINDOW
        w7 AS (PARTITION BY location_id ORDER BY weather_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),
        w30 AS (PARTITION BY location_id ORDER BY weather_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
    )
    SELECT w.*,l.name_en,
        CASE WHEN n7=7 AND DATEDIFF(weather_date,first7)=6 THEN mean7 END ma7,
        CASE WHEN n30=30 AND DATEDIFF(weather_date,first30)=29 THEN mean30 END ma30,
        SUM(valid_flag) OVER (PARTITION BY w.location_id) display_valid_days
    FROM framed w JOIN locations l ON l.location_id=w.location_id
    WHERE weather_date BETWEEN ? AND ? ORDER BY w.location_id,weather_date';
    return [$sql,[...$params,$f['start_date'],$f['end_date']]];
}
// Team responsibility: Jieun Hwang (2376329) — Assigned module responsibility; implementation history remains unchanged.
function seasonal_data(PDO $p,array $o): array {
    $year = integer_input($o,'year',2023,2025);
    $month = integer_input($o,'month',1,12);
    $first = new DateTimeImmutable(sprintf('%04d-%02d-01',$year,$month));
    $terms = run_query($p,'SELECT term_date,term_name,source_url FROM solar_terms WHERE term_date>=? AND term_date<? ORDER BY term_date',
        [$first->format('Y-m-d'),$first->modify('+1 month')->format('Y-m-d')]);
    $foods = run_query($p,'SELECT month_no,food_name,source_url FROM monthly_food_guides WHERE month_no=? ORDER BY guide_id',[$month]);
    return ['terms'=>$terms,'foods'=>$foods];
}
