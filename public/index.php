<?php
declare(strict_types=1);

function h(mixed $v): string
{
    return htmlspecialchars((string) $v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function load_json(string $path): array
{
    $raw = is_file($path) ? file_get_contents($path) : false;
    $data = is_string($raw) ? json_decode($raw, true) : null;
    return is_array($data) ? $data : [];
}

$root = dirname(__DIR__);
$profile = load_json($root . '/content/profile.json');
$projects = load_json($root . '/content/projects.json');
$links = is_array($profile['links'] ?? null) ? $profile['links'] : [];
$skills = is_array($profile['skills'] ?? null) ? $profile['skills'] : [];
$skillLabels = [
    'ops' => 'Linux / Ops',
    'cloud' => 'Cloud / IaC',
    'data' => 'Data',
    'backend' => 'Backend',
    'languages' => 'Languages',
];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= h((string) ($profile['name'] ?? 'Ettiene Wium')) ?> — <?= h((string) ($profile['headline'] ?? 'Profile')) ?></title>
    <link rel="stylesheet" href="/assets/css/app.css">
</head>
<body>
<header class="top">
    <p class="brand"><?= h((string) ($profile['name'] ?? 'Ettiene Wium')) ?></p>
    <nav>
        <a href="#about">About</a>
        <a href="#skills">Skills</a>
        <a href="#experience">Experience</a>
        <a href="#work">Work</a>
        <a href="#contact">Contact</a>
    </nav>
</header>
<main>
    <section class="hero" id="about">
        <p class="eyebrow"><?= h((string) ($profile['location'] ?? '')) ?></p>
        <h1><?= h((string) ($profile['headline'] ?? '')) ?></h1>
        <div class="prose"><?= nl2br(h((string) ($profile['summary'] ?? '')), false) ?></div>
        <p class="actions">
            <?php if (!empty($links['github'])): ?><a class="btn" href="<?= h((string) $links['github']) ?>">GitHub</a><?php endif; ?>
            <?php if (!empty($links['linkedin'])): ?><a class="btn" href="<?= h((string) $links['linkedin']) ?>">LinkedIn</a><?php endif; ?>
            <a class="btn ghost" href="mailto:<?= h((string) ($profile['email'] ?? '')) ?>">Email</a>
        </p>
    </section>

    <section id="skills">
        <h2>Skills</h2>
        <div class="grid">
            <?php foreach ($skillLabels as $key => $label): ?>
                <?php $list = is_array($skills[$key] ?? null) ? $skills[$key] : []; ?>
                <?php if ($list === []) { continue; } ?>
                <article>
                    <h3><?= h($label) ?></h3>
                    <ul><?php foreach ($list as $item): ?><li><?= h((string) $item) ?></li><?php endforeach; ?></ul>
                </article>
            <?php endforeach; ?>
        </div>
    </section>

    <section id="experience">
        <h2>Experience</h2>
        <?php foreach (is_array($profile['experience'] ?? null) ? $profile['experience'] : [] as $job): ?>
            <?php if (!is_array($job)) { continue; } ?>
            <article class="job">
                <h3><?= h((string) ($job['title'] ?? '')) ?> — <?= h((string) ($job['company'] ?? '')) ?></h3>
                <p class="meta"><?= h((string) ($job['dates'] ?? '')) ?> · <?= h((string) ($job['location'] ?? '')) ?></p>
                <ul>
                    <?php foreach (is_array($job['bullets'] ?? null) ? $job['bullets'] : [] as $b): ?>
                        <li><?= h((string) $b) ?></li>
                    <?php endforeach; ?>
                </ul>
            </article>
        <?php endforeach; ?>
    </section>

    <section id="certs">
        <h2>Certifications</h2>
        <ul class="plain">
            <?php foreach (is_array($profile['certs'] ?? null) ? $profile['certs'] : [] as $c): ?>
                <li><?= h((string) $c) ?></li>
            <?php endforeach; ?>
        </ul>
        <h2>Education</h2>
        <ul class="plain">
            <?php foreach (is_array($profile['education'] ?? null) ? $profile['education'] : [] as $e): ?>
                <li><?= h((string) $e) ?></li>
            <?php endforeach; ?>
        </ul>
    </section>

    <section id="work">
        <h2>Selected work</h2>
        <p class="lede"><?= h((string) ($projects['lede'] ?? '')) ?></p>
        <div class="grid">
            <?php foreach (is_array($projects['items'] ?? null) ? $projects['items'] : [] as $p): ?>
                <?php if (!is_array($p)) { continue; } ?>
                <article>
                    <p class="meta"><?= h((string) ($p['status'] ?? '')) ?> · <?= h((string) ($p['role'] ?? '')) ?></p>
                    <h3><?= h((string) ($p['name'] ?? '')) ?></h3>
                    <p><?= h((string) ($p['blurb'] ?? '')) ?></p>
                    <?php if (!empty($p['url'])): ?><p><a href="<?= h((string) $p['url']) ?>">Open</a></p><?php endif; ?>
                </article>
            <?php endforeach; ?>
        </div>
    </section>

    <section id="contact">
        <h2>Contact</h2>
        <p><?= h((string) ($profile['email'] ?? '')) ?><?php if (!empty($profile['phone'])): ?> · <?= h((string) $profile['phone']) ?><?php endif; ?></p>
        <p class="muted">Cape Town · globally remote · SAST (UTC+2)</p>
    </section>
</main>
<footer>
    <p>Public profile only. No logins. Content synced from UpSkill via wium-sync.</p>
</footer>
</body>
</html>
