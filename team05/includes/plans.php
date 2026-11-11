<?php
// Implementation: Codex. Web callers validate first; repository writes are atomic.
declare(strict_types=1);
function text_length(string $value): int {
    $length = preg_match_all('/./us',$value);
    if ($length === false) throw new InvalidArgumentException('Text must be valid UTF-8.');
    return $length;
}
function validate_plan(array $input): array {
    $f = validate_filters($input);
    $name = scalar_input($input,'plan_name');
    $memo = isset($input['memo']) ? scalar_input($input,'memo') : '';
    if (text_length($name)<1 || text_length($name)>100) throw new InvalidArgumentException('Plan name must contain 1–100 characters.');
    if (text_length($memo)>2000) throw new InvalidArgumentException('Memo must contain at most 2,000 characters.');
    return array_merge($f,['plan_name'=>$name,'memo'=>$memo]);
}
function plan_id(array $input, string $key = 'plan_id'): int {
    return integer_input($input,$key,1,PHP_INT_MAX);
}
function get_plan(PDO $p,int $id): ?array {
    $rows=run_query($p,'SELECT * FROM saved_plans WHERE plan_id=?',[$id]);
    if (!$rows) return null;
    $plan=$rows[0];
    $plan['locations']=run_query($p,'SELECT l.* FROM plan_locations pl JOIN locations l ON l.location_id=pl.location_id WHERE pl.plan_id=? ORDER BY pl.location_id',[$id]);
    $plan['location_ids']=array_map('intval',array_column($plan['locations'],'location_id'));
    return $plan;
}
function list_plans(PDO $p): array {
    return run_query($p,"SELECT s.*,COALESCE(p.location_count,0) location_count,p.location_names
        FROM saved_plans s LEFT JOIN (
            SELECT pl.plan_id,COUNT(*) location_count,GROUP_CONCAT(l.name_en ORDER BY l.location_id SEPARATOR ', ') location_names
            FROM plan_locations pl JOIN locations l ON l.location_id=pl.location_id GROUP BY pl.plan_id
        ) p ON p.plan_id=s.plan_id ORDER BY s.updated_at DESC,s.plan_id DESC");
}
function save_plan(PDO $p,array $plan,?int $id = null): int {
    // Internal repository boundary accepts normalized data. Database FK/CHECK failures propagate after rollback.
    $p->beginTransaction();
    try {
        $values=[$plan['plan_name'],$plan['start_date'],$plan['end_date'],$plan['max_temp_threshold'],$plan['max_temp_range'],$plan['memo']];
        if ($id === null) {
            run_query($p,'INSERT INTO saved_plans (plan_name,start_date,end_date,max_temp_threshold,max_temp_range,memo) VALUES (?,?,?,?,?,?)',$values);
            $id=(int)$p->lastInsertId();
        } else {
            if (!run_query($p,'SELECT plan_id FROM saved_plans WHERE plan_id=? FOR UPDATE',[$id])) throw new OutOfBoundsException('Plan no longer exists.');
            run_query($p,'UPDATE saved_plans SET plan_name=?,start_date=?,end_date=?,max_temp_threshold=?,max_temp_range=?,memo=?,updated_at=CURRENT_TIMESTAMP WHERE plan_id=?',[...$values,$id]);
            run_query($p,'DELETE FROM plan_locations WHERE plan_id=?',[$id]);
        }
        foreach($plan['location_ids'] as $location) run_query($p,'INSERT INTO plan_locations (plan_id,location_id) VALUES (?,?)',[$id,$location]);
        $p->commit();
        return $id;
    } catch (Throwable $e) {
        if ($p->inTransaction()) $p->rollBack();
        throw $e;
    }
}
function delete_plan(PDO $p,int $id): void {
    $p->beginTransaction();
    try {
        if (!run_query($p,'SELECT plan_id FROM saved_plans WHERE plan_id=? FOR UPDATE',[$id])) throw new OutOfBoundsException('Plan no longer exists.');
        run_query($p,'DELETE FROM saved_plans WHERE plan_id=?',[$id]);
        $p->commit();
    } catch (Throwable $e) { if ($p->inTransaction()) $p->rollBack(); throw $e; }
}
function display_draft(array $input,array $fallback): array {
    foreach(['plan_name','memo','start_date','end_date','max_temp_threshold','max_temp_range'] as $key) {
        if (isset($input[$key]) && is_scalar($input[$key]) && !is_bool($input[$key])) $fallback[$key]=(string)$input[$key];
    }
    if (isset($input['location_ids']) && is_array($input['location_ids'])) {
        $fallback['location_ids']=[];
        foreach($input['location_ids'] as $id) if(is_scalar($id) && preg_match('/^[1-5]$/D',(string)$id)) $fallback['location_ids'][]=(int)$id;
    } else $fallback['location_ids']=[];
    return $fallback;
}
