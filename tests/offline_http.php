<?php
// HTTP workflow helper. Network isolation is inspected by the outer verifier.
declare(strict_types=1);
function demand(bool $condition,string $message): void {if(!$condition)throw new RuntimeException($message);}
require_once dirname(__DIR__).'/team05/includes/db.php';
$runtime_database=run_query(db(),'SELECT VERSION() version,CURRENT_USER() account')[0];
$cookie=tempnam(sys_get_temp_dir(),'slg_cookie_');
$base=getenv('SLG_TEST_URL') ?: 'http://127.0.0.1/team05/';
function request_page(string $page,array $params=[],bool $post=false): array {
    global $cookie,$base;
    $c=curl_init($base.$page.(!$post && $params ? '?'.http_build_query($params):''));
    curl_setopt_array($c,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_FOLLOWLOCATION=>true,CURLOPT_COOKIEJAR=>$cookie,CURLOPT_COOKIEFILE=>$cookie,CURLOPT_TIMEOUT=>15]);
    if($post)curl_setopt($c,CURLOPT_POSTFIELDS,http_build_query($params));
    $body=curl_exec($c);$status=curl_getinfo($c,CURLINFO_HTTP_CODE);$error=curl_error($c);curl_close($c);
    demand(is_string($body),'HTTP client error: '.$error);return [$status,$body];
}
$id=null;$token='';
try {
    [$status,$body]=request_page('index.php');demand($status===200 && str_contains($body,'5,480'),'Home from fresh DB');
    $f=['apply_filters'=>1,'start_date'=>'2024-08-01','end_date'=>'2024-08-31','max_temp_threshold'=>'28.00','max_temp_range'=>'10.00','location_ids'=>[1,2,3,4,5]];
    foreach(['aggregate.php','ranking.php','window.php','olap.php'] as $page){[$status,$body]=request_page($page,$f);demand($status===200,'Analysis '.$page);}
    foreach(['year','month','day','month','year'] as $level){[$status,$body]=request_page('olap.php',['level'=>$level,'drill_year'=>2024,'drill_month'=>8]);demand($status===200,'OLAP '.$level);}
    [$status,$body]=request_page('ranking.php',['top_rank'=>1]);demand($status===200 && substr_count($body,'6.45%')===2,'Offline tied ranks');
    [$status,$body]=request_page('seasonal.php',['year'=>2024,'month'=>10]);demand($status===200 && str_contains($body,'한로') && str_contains($body,'새송이버섯'),'Seasonal sources from DB');
    [$status,$body]=request_page('plan_form.php');demand($status===200,'Plan form');
    preg_match('/name="csrf_token" value="([a-f0-9]{64})"/',$body,$match);$token=$match[1] ?? '';demand(strlen($token)===64,'CSRF token');
    $plan=$f;unset($plan['apply_filters']);$plan+=['action'=>'create','csrf_token'=>$token,'plan_name'=>'Offline verification','memo'=>'Original offline body'];
    [$status,$body]=request_page('plan_actions.php',$plan,true);demand($status===200 && str_contains($body,'Plan saved'),'Offline create');
    preg_match('/name="plan_id" value="(\d+)"/',$body,$match);$id=(int)($match[1] ?? 0);demand($id>0,'Created id');
    [$status,$body]=request_page('plans.php');demand($status===200 && str_contains($body,'Offline verification'),'List selects saved parent');
    [$status,$body]=request_page('plan_form.php',['id'=>$id]);demand($status===200,'Edit form');
    [$status,$body]=request_page('plan_actions.php',array_replace($plan,['action'=>'update','plan_id'=>$id,'plan_name'=>'Offline updated','location_ids'=>[2,3]]),true);demand($status===200 && str_contains($body,'Busan, Daegu'),'Update persisted children');
    [$status,$body]=request_page('plan_actions.php',['action'=>'apply','plan_id'=>$id,'csrf_token'=>$token,'target'=>'ranking'],true);demand($status===200 && str_contains($body,'Saved comparison conditions applied'),'Apply restored session');
    [$status,$body]=request_page('aggregate.php');demand($status===200 && str_contains($body,'value="2" checked') && !str_contains($body,'value="1" checked'),'Cross-page session');
    [$status,$body]=request_page('plan_actions.php',['action'=>'delete','plan_id'=>$id,'csrf_token'=>$token],true);demand($status===200,'Delete');
    [$status,$body]=request_page('plan_detail.php',['id'=>$id]);demand($status===404,'Deleted detail');$id=null;
    echo json_encode(['result'=>'PASS','pages'=>9,'analyses'=>'four independent dynamic DB menus','olap'=>'year/month/day/up','ranking'=>'two first-place ties','seasonal'=>'October 2024 sources and ingredient','crud'=>'HTTP create/read/list/edit/update/apply/delete','session'=>'saved common filters reused on another analysis','database'=>$runtime_database,'client_php'=>PHP_VERSION,'network_isolation'=>'not inspected by this HTTP helper','base_url'=>$base],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE),"\n";
} finally {
    if($id!==null)request_page('plan_actions.php',['action'=>'delete','plan_id'=>$id,'csrf_token'=>$token],true);
    unlink($cookie);
}
