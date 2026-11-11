<?php
// Team responsibility: Jihee Choi (2276337) — Ranking/Windowing; ties, denominators, continuous dates and line-chart verification.
// Presentation geometry only: every plotted value is a returned SQL field.
declare(strict_types=1);
function trend_geometry(array $rows, int $width = 1030): array {
    $keys=['metric_value','ma7','ma30'];$values=[];
    foreach($rows as $row)foreach($keys as $key)if($row[$key]!==null && is_numeric($row[$key]) && is_finite((float)$row[$key]))$values[]=(float)$row[$key];
    if(!$rows || !$values)return ['empty'=>true,'series'=>[]];
    $first=new DateTimeImmutable($rows[0]['weather_date']);$last=new DateTimeImmutable($rows[count($rows)-1]['weather_date']);
    $days=(int)$first->diff($last)->format('%a');$low=min($values);$high=max($values);$padding=$high===$low ? 1:($high-$low)*.08;$low-=$padding;$high+=$padding;
    $series=[];
    foreach($keys as $key){
        $segments=[];$segment=[];$previous=null;
        foreach($rows as $row){
            $day=new DateTimeImmutable($row['weather_date']);
            $gap=$previous!==null && (int)$previous->diff($day)->format('%a')!==1;
            $value=$row[$key];
            if($gap || $value===null || !is_numeric($value) || !is_finite((float)$value)){
                if($segment)$segments[]=$segment;$segment=[];
            }
            if($value!==null && is_numeric($value) && is_finite((float)$value)){
                $offset=(int)$first->diff($day)->format('%a');
                $segment[]=['date'=>$row['weather_date'],'value'=>(float)$value,
                    'x'=>$days===0 ? (62+$width-32)/2:62+($width-94)*$offset/$days,'y'=>210-174*((float)$value-$low)/($high-$low)];
            }
            $previous=$day;
        }
        if($segment)$segments[]=$segment;$series[$key]=$segments;
    }
    return ['empty'=>false,'series'=>$series,'minimum'=>$low,'maximum'=>$high,'first_date'=>$first->format('Y-m-d'),'last_date'=>$last->format('Y-m-d'),'day_span'=>$days,'svg_width'=>$width,'row_count'=>count($rows)];
}
function render_plot_svg(array $geometry,string $name,int $location,array $options,bool $mobile = false): void {
    $suffix=$mobile ? '-mobile':'';
    ?>
<svg class="trend-chart <?= $mobile ? 'chart-mobile':'chart-desktop' ?>" viewBox="0 0 <?=e($geometry['svg_width'])?> 260" role="img" aria-labelledby="chart-label<?=e($suffix)?> chart-description<?=e($suffix)?>" data-location-id="<?=e($location)?>" data-value-source="MariaDB query results"><title id="chart-label<?=e($suffix)?>"><?=e($name)?> temperature trend</title><desc id="chart-description<?=e($suffix)?>">Daily values and SQL-calculated 7 and 30 day averages in degrees Celsius. Gaps and missing values break the lines. The complete values are in the table below.</desc>
<?php for($n=0;$n<=4;$n++):$y=36+$n*43.5;$value=$geometry['maximum']-($geometry['maximum']-$geometry['minimum'])*$n/4; ?><line class="chart-grid" x1="62" x2="<?=e($geometry['svg_width']-32)?>" y1="<?=e($y)?>" y2="<?=e($y)?>"/><text class="chart-tick" x="52" y="<?=e($y+5)?>" text-anchor="end"><?=num($value,1)?></text><?php endfor; ?>
<text class="chart-tick" x="22" y="17">°C</text><text class="chart-tick" x="62" y="240"><?=e($geometry['first_date'])?></text><text class="chart-tick" x="<?=e($geometry['svg_width']-32)?>" y="240" text-anchor="end"><?=e($geometry['last_date'])?></text>
<?php foreach($geometry['series'] as $key=>$segments):$class=$key==='metric_value' ? 'daily':($key==='ma7' ? 'seven':'thirty');$focus=($key==='ma7' && $options['window_days']===7)||($key==='ma30' && $options['window_days']===30); ?>
<g class="series-<?=e($class)?><?= $focus ? ' focus-series':'' ?>" data-series="<?=e($key)?>">
<?php foreach($segments as $segment):if(count($segment)>1){$commands=[];foreach($segment as $i=>$point)$commands[]=($i===0 ? 'M':'L').number_format($point['x'],3,'.','').','.number_format($point['y'],3,'.',''); ?><path d="<?=e(implode(' ',$commands))?>"/><?php }foreach($segment as $point): ?><circle cx="<?=e(number_format($point['x'],3,'.',''))?>" cy="<?=e(number_format($point['y'],3,'.',''))?>" r="<?=$geometry['row_count']<=31 || count($segment)===1 ? '2.6':'0'?>" data-date="<?=e($point['date'])?>" data-value="<?=e($point['value'])?>"/><?php endforeach;endforeach; ?></g><?php endforeach; ?>
</svg>
<?php }

function render_trend_chart(array $rows,array $filters,array $options): void {
    $choices=[];foreach($rows as $r)$choices[(int)$r['location_id']]=$r['name_en'];
    $location=(int)$options['chart_location'];$selected=array_values(array_filter($rows,fn($r)=>(int)$r['location_id']===$location));
    $geometry=trend_geometry($selected);
    ?>
<section class="panel trend-panel" aria-labelledby="trend-title"><div class="chart-heading"><div><h2 id="trend-title">Temperature over time</h2><p class="caption"><?=e($choices[$location] ?? 'Selected location')?> · <?=e($filters['start_date'])?> to <?=e($filters['end_date'])?> · <?=e(ucfirst($options['metric']))?> °C</p></div>
<form method="get" class="chart-select"><?php select_control('chart_location','Graph location',$choices,$location); ?><button class="button secondary">Show graph</button></form></div>
<?php if($geometry['empty']): ?><p class="caption">No valid values to plot for this selection.</p><?php else: ?>
<div class="chart-legend" aria-label="Graph legend"><span class="legend-daily">Daily value</span><span class="legend-seven<?= $options['window_days']===7 ? ' focused':'' ?>">7 day average<?= $options['window_days']===7 ? ' · focused':'' ?></span><span class="legend-thirty<?= $options['window_days']===30 ? ' focused':'' ?>">30 day average<?= $options['window_days']===30 ? ' · focused':'' ?></span></div>
<?php render_plot_svg($geometry,$choices[$location],$location,$options); render_plot_svg(trend_geometry($selected,480),$choices[$location],$location,$options,true); ?>
<?php endif; ?><p class="caption">Graphing one location keeps all selected locations in the comparison table. Missing averages are left blank.</p></section>
<?php }
