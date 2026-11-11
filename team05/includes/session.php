<?php
// Team responsibility: Jieun Hwang (2376329) — Common PHP/config/PDO, Session/input/UI; solar-term and monthly-guide pages/queries.
// Implementation: Codex. Filters persist across pages; permanent plans live in MariaDB.
declare(strict_types=1);
function analysis_context(string $page): array {
    $GLOBALS['analysis_page'] = $page;
    $f = $_SESSION['analysis_filters'] ?? default_filters();
    $o = $_SESSION['analysis_options'][$page] ?? default_options($page);
    try {
        if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'POST' && isset($_POST['reset_filters'])) {
            check_csrf($_POST);
            unset($_SESSION['analysis_filters'], $_SESSION['analysis_options']);
            $f = default_filters(); $o = default_options($page);
        } else {
            $candidate = $f;
            $intent = array_key_exists('intent',$_GET) ? scalar_input($_GET,'intent') : 'apply';
            if (!in_array($intent,['apply','save'],true)) throw new InvalidArgumentException('Unknown filter action.');
            if ($intent === 'save' && !array_key_exists('apply_filters',$_GET)) throw new InvalidArgumentException('Submit the current comparison conditions first.');
            if (array_key_exists('apply_filters', $_GET)) {
                if (scalar_input($_GET,'apply_filters') !== '1') throw new InvalidArgumentException('Invalid filter submission.');
                $candidate = validate_filters($_GET);
            }
            $options = validate_options($page, $_GET, $o);
            if ($page === 'window' && !in_array($options['chart_location'],$candidate['location_ids'],true)) {
                if (array_key_exists('chart_location',$_GET)) throw new InputValidationException('chart_location','Choose a graph location from the selected comparison locations.');
                $options['chart_location']=$candidate['location_ids'][0];
            }
            // Nothing is written to the session until both common and page options validate.
            $_SESSION['analysis_filters'] = $candidate;
            $_SESSION['analysis_options'][$page] = $options;
            $f = $candidate; $o = $options;
            if ($intent === 'save') {
                header('Location: plan_form.php',true,303);
                exit;
            }
        }
        return [$f, $o, null];
    } catch (InvalidArgumentException $e) {
        http_response_code(422);
        $GLOBALS['validation_errors'] = $e instanceof InputValidationException ? [$e->field => $e->getMessage()] : [];
        $GLOBALS['filter_draft'] = $_GET;
        return [$f, $o, $e->getMessage()];
    }
}
function flash(string $message): void { $_SESSION['flash'] = $message; }
function take_flash(): ?string {
    $message = $_SESSION['flash'] ?? null;
    unset($_SESSION['flash']);
    return $message;
}
