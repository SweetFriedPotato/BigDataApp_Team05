<?php
// Original interface by Codex. The four analysis menus remain separate.
$menus = ['index'=>['Home','index.php'],'aggregate'=>['Temperature Comparison','aggregate.php'],
    'olap'=>['Temperature Explorer','olap.php'],'ranking'=>['Find My Season','ranking.php'],
    'window'=>['Temperature Trends','window.php'],'seasonal'=>['Seasonal Information','seasonal.php'],
    'plans'=>['Saved Plans','plans.php']];
?>
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Compare historical temperatures across five Korean locations and explore seasonal references."><title><?=e($title)?> · Seasonal Living Guide</title><link rel="icon" href="assets/img/weather-mark.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/css/app.css"><script src="assets/js/app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="masthead"><a class="brand" href="index.php" aria-label="Seasonal Living Guide"><img src="assets/img/weather-mark.svg" width="40" height="40" alt="" aria-hidden="true"><span>Seasonal Living Guide</span></a><span class="edition">5 locations · 2023–2025 <span class="lst-label">LST</span></span></header>
<nav class="navigation" aria-label="Main navigation"><?php foreach ($menus as $key=>[$label,$href]): ?><a href="<?=e($href)?>"<?=$key===$page ? ' aria-current="page"' : ''?>><?=e($label)?></a><?php endforeach; ?></nav>
<main id="main" class="workspace"><div class="page-heading"><h1><?=e($title)?></h1><?php if ($intro): ?><p class="intro"><?=e($intro)?></p><?php endif; ?></div>
<?php if ($message = take_flash()): ?><div class="notice" role="status"><?=e($message)?></div><?php endif; ?>
