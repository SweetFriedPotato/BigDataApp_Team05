<?php
// Implementation: Codex. Shared navigation keeps the four required analyses distinct.
$menus = ['index'=>['Home','index.php'],'aggregate'=>['Temperature Comparison','aggregate.php'],
    'olap'=>['Temperature Explorer','olap.php'],'ranking'=>['Find My Season','ranking.php'],
    'window'=>['Temperature Trends','window.php'],'seasonal'=>['Seasonal Information','seasonal.php'],
    'plans'=>['Saved Plans','plans.php']];
?>
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Compare historical temperatures across five Korean locations and explore seasonal reference information."><title><?=e($title)?> · Seasonal Living Guide</title><link rel="stylesheet" href="assets/css/app.css"><script src="assets/js/app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="masthead"><a class="brand" href="index.php"><span class="brand-mark" aria-hidden="true">✳</span><span>Seasonal<br><strong>Living Guide</strong></span></a><div class="masthead-note">A little perspective<br><strong>on the seasons we share.</strong></div><span class="edition">KOREA · 2023—2025<br>HISTORICAL TEMPERATURES</span></header>
<nav class="navigation" aria-label="Main navigation"><?php foreach ($menus as $key=>[$label,$href]): ?><a href="<?=e($href)?>"<?=$key===$page ? ' aria-current="page"' : ''?>><?=e($label)?></a><?php endforeach; ?></nav>
<main id="main" class="workspace"><div class="page-heading"><div><p class="eyebrow">SEASONAL LIVING GUIDE <span>/ <?=e($page === 'index' ? 'OVERVIEW' : strtoupper($page))?></span></p><h1><?=e($title)?></h1><?php if ($intro): ?><p class="intro"><?=e($intro)?></p><?php endif; ?></div><span class="archive-badge">PAST WEATHER<br><strong>Future perspective</strong></span></div>
<?php if ($message = take_flash()): ?><div class="notice" role="status"><?=e($message)?></div><?php endif; ?>
