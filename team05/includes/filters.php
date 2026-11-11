<?php
// Implementation: Codex. Common input contract used by every analysis and saved plan.
declare(strict_types=1);
class InputValidationException extends InvalidArgumentException {
    public string $field;
    public function __construct(string $field, string $message) {
        parent::__construct($message); $this->field = $field;
    }
}
const DATA_START = '2023-01-01';
const DATA_END = '2025-12-31';
function default_filters(): array {
    return ['location_ids' => [1,2,3,4,5], 'start_date' => '2025-01-01',
        'end_date' => '2025-12-31', 'max_temp_threshold' => '28.00', 'max_temp_range' => '10.00'];
}
function scalar_input(array $input, string $key): string {
    if (!array_key_exists($key, $input) || !is_scalar($input[$key]) || is_bool($input[$key])) {
        throw new InputValidationException($key,'Missing or invalid ' . $key . '.');
    }
    return trim((string)$input[$key]);
}
function strict_date(string $value, string $field = 'start_date'): string {
    $date = DateTimeImmutable::createFromFormat('!Y-m-d', $value);
    if (!$date || $date->format('Y-m-d') !== $value || $value < DATA_START || $value > DATA_END) {
        throw new InputValidationException($field,'Dates must be real dates between 2023-01-01 and 2025-12-31.');
    }
    return $value;
}
function decimal_input(array $input, string $key, float $min, float $max): string {
    $v = scalar_input($input, $key);
    if (!preg_match('/^-?\d{1,3}(?:\.\d{1,2})?$/D', $v) || !is_finite((float)$v) || (float)$v < $min || (float)$v > $max) {
        throw new InputValidationException($key,$key . ' is outside the allowed range or has more than two decimal places.');
    }
    return number_format((float)$v, 2, '.', '');
}
function integer_input(array $input, string $key, int $min, int $max): int {
    $v = scalar_input($input, $key);
    if (!preg_match('/^(0|[1-9]\d*)$/D', $v) || strlen($v) > 18 || (float)$v > $max || (int)$v < $min) {
        throw new InputValidationException($key,'Invalid ' . $key . '.');
    }
    return (int)$v;
}
function validate_filters(array $input): array {
    $ids = $input['location_ids'] ?? null;
    if (!is_array($ids) || !$ids) {
        throw new InputValidationException('location_ids','Select at least one location.');
    }
    $selected = [];
    foreach ($ids as $id) {
        $selected[] = integer_input(['location_ids' => $id], 'location_ids', 1, 5);
    }
    $selected = array_values(array_unique($selected));
    sort($selected, SORT_NUMERIC);
    $start = strict_date(scalar_input($input, 'start_date'),'start_date');
    $end = strict_date(scalar_input($input, 'end_date'),'end_date');
    if ($start > $end) {
        throw new InputValidationException('end_date','Start date must not be after end date.');
    }
    return ['location_ids' => $selected, 'start_date' => $start, 'end_date' => $end,
        'max_temp_threshold' => decimal_input($input, 'max_temp_threshold', -50, 60),
        'max_temp_range' => decimal_input($input, 'max_temp_range', 0, 60)];
}
function default_options(string $page): array {
    return match ($page) {
        'aggregate' => ['group_mode' => 'location_year_month'],
        'olap' => ['level' => 'year', 'drill_year' => 2025, 'drill_month' => 1],
        'ranking' => ['top_rank' => 5, 'min_valid_days' => 1],
        'window' => ['metric' => 'mean', 'window_days' => 7, 'chart_location' => 1],
        'seasonal' => ['year' => 2025, 'month' => 1],
        default => [],
    };
}
function validate_options(string $page, array $input, array $previous): array {
    $o = array_replace(default_options($page), $previous);
    $enums = ['group_mode' => ['location_year', 'location_year_month'],
        'level' => ['year','month','day'], 'metric' => ['mean','max','min','range']];
    $ranges = ['drill_year' => [2023,2025], 'drill_month' => [1,12], 'top_rank' => [1,5],
        'min_valid_days' => [1,1096], 'chart_location' => [1,5], 'window_days' => [7,30], 'year' => [2023,2025], 'month' => [1,12]];
    foreach ($o as $key => $value) {
        if (!array_key_exists($key, $input)) continue;
        if (isset($enums[$key])) {
            $v = scalar_input($input, $key);
            if (!in_array($v, $enums[$key], true)) throw new InputValidationException($key,'Unknown ' . $key . '.');
            $o[$key] = $v;
        } else {
            $o[$key] = integer_input($input, $key, ...$ranges[$key]);
            if ($key === 'window_days' && !in_array($o[$key], [7,30], true)) {
                throw new InputValidationException($key,'Choose a 7 or 30 day window.');
            }
        }
    }
    return $o;
}
