<?php
require __DIR__ . '/support.php';
test_case('T03','KASI 24 dates/year and source-backed guide for every month',function(){
    $years=run_query(db(),'SELECT YEAR(term_date) year_no,COUNT(*) n FROM solar_terms GROUP BY YEAR(term_date) ORDER BY year_no');
    check(array_column($years,'n')==[24,24,24],'24 terms per year');
    $terms=0;$foods=0;
    foreach(range(2023,2025) as $year)foreach(range(1,12) as $month){$d=seasonal_data(db(),['year'=>$year,'month'=>$month]);$terms+=count($d['terms']);$foods+=count($d['foods']);check(count($d['foods'])>=1,'At least one guide item');foreach([...$d['terms'],...$d['foods']] as $r)check(str_starts_with($r['source_url'],'https://'),'Source URL');}
    check($terms===72 && $foods===36,'72 date occurrences; 12 monthly guides reused in 3 years');
    $d24=seasonal_data(db(),['year'=>2024,'month'=>2]);$d25=seasonal_data(db(),['year'=>2025,'month'=>2]);
    check($d24['terms'][0]['term_date']==='2024-02-04' && $d25['terms'][0]['term_date']==='2025-02-03','Year-specific dates');
    return ['year_counts'=>$years,'terms_across36_months'=>$terms,'monthly_items'=>12,'February_first_term_2024'=>$d24['terms'][0],'February_first_term_2025'=>$d25['terms'][0]];
});
test_case('T28','Extra monthly food guides cannot multiply weather statistics',function(){
    $f=period_filters('2024-08-01','2024-08-31');
    $a=analysis_rows('aggregate',$f,['group_mode'=>'location_year_month']);$r=analysis_rows('ranking',$f,['top_rank'=>5,'min_valid_days'=>1]);$w=analysis_rows('window',$f,['metric'=>'mean','window_days'=>7]);
    $p=db();$p->beginTransaction();try{
        run_query($p,'INSERT INTO monthly_food_guides (month_no,food_name,source_url) VALUES (?,?,?)',[8,'CLI-only extra guide','https://example.invalid/test-fixture']);
        check($a===analysis_rows('aggregate',$f,['group_mode'=>'location_year_month']),'Aggregate unchanged');check($r===analysis_rows('ranking',$f,['top_rank'=>5,'min_valid_days'=>1]),'Ranks unchanged');check($w===analysis_rows('window',$f,['metric'=>'mean','window_days'=>7]),'Windows unchanged');
        return ['food_guides_august_before'=>1,'during_test'=>count(seasonal_data($p,['year'=>2024,'month'=>8])['foods']),'aggregate_ranking_window'=>'exactly unchanged'];
    }finally{$p->rollBack();}
});
finish_tests();
