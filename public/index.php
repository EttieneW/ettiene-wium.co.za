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
$cover = load_json($root . '/content/cover-letter.json');
$links = is_array($profile['links'] ?? null) ? $profile['links'] : [];
$skills = is_array($profile['skills'] ?? null) ? $profile['skills'] : [];
$skillLabels = [
    'ops' => 'Linux / Ops',
    'cloud' => 'Cloud / IaC',
    'data' => 'Data',
    'backend' => 'Backend',
    'languages' => 'Languages',
    'other' => 'Also',
];
$name = (string) ($profile['name'] ?? 'Ettiene Wium');
$headline = (string) ($profile['headline'] ?? 'Profile');
$location = (string) ($profile['location'] ?? '');
$email = (string) ($profile['email'] ?? '');
$phone = (string) ($profile['phone'] ?? '');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="<?= h($headline) ?>">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <title><?= h($name) ?> — <?= h($headline) ?></title>
    <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="/assets/css/app.css">
</head>
<body>
<a class="skip" href="#about">Skip to content</a>
<header class="top">
    <div class="top-inner">
        <a class="brand" href="#about">
            <img src="/assets/favicon.svg" width="28" height="28" alt="">
            <span><?= h($name) ?></span>
        </a>
        <nav>
            <a href="#about">About</a>
            <a href="#skills">Skills</a>
            <a href="#experience">Experience</a>
            <a href="#certs">Certs</a>
            <a href="#work">Work</a>
            <a href="#letter">Letter</a>
            <a href="#contact">Contact</a>
        </nav>
        <a class="btn btn-sm" href="/downloads/Ettiene-Wium-CV.pdf">Download CV</a>
    </div>
</header>
<main>
    <section class="hero" id="about">
        <p class="kicker"><?= h($location) ?></p>
        <h1><?= h($name) ?></h1>
        <p class="role"><?= h($headline) ?></p>
        <p class="status"><span class="status-dot"></span> Open to PHP production roles and SRE / DevOps · globally remote · flexi hours</p>
        <div class="prose"><?= nl2br(h((string) ($profile['summary'] ?? '')), false) ?></div>
        <p class="actions">
            <a class="btn" href="/downloads/Ettiene-Wium-CV.pdf">Download CV (PDF)</a>
            <a class="btn ghost" href="/downloads/Ettiene-Wium-CV.docx">CV (DOCX)</a>
            <?php if (!empty($links['github'])): ?><a class="btn ghost" href="<?= h((string) $links['github']) ?>" target="_blank" rel="noopener noreferrer">GitHub</a><?php endif; ?>
            <?php if (!empty($links['linkedin'])): ?><a class="btn ghost" href="<?= h((string) $links['linkedin']) ?>" target="_blank" rel="noopener noreferrer">LinkedIn</a><?php endif; ?>
            <?php if ($email !== ''): ?><a class="btn ghost" href="mailto:<?= h($email) ?>">Email</a><?php endif; ?>
        </p>
    </section>

    <section id="skills">
        <div class="section-head">
            <p class="section-index">01</p>
            <h2>Skills</h2>
        </div>
        <p class="lede">Years are honest. Kubernetes is two years of homelab (k3s/k3d), not a cluster at my current employer.</p>
        <div class="grid">
            <?php foreach ($skillLabels as $key => $label): ?>
                <?php $list = is_array($skills[$key] ?? null) ? $skills[$key] : []; ?>
                <?php if ($list === []) { continue; } ?>
                <article class="skill-card">
                    <h3><?= h($label) ?></h3>
                    <ul class="chips"><?php foreach ($list as $item): ?><li><?= h((string) $item) ?></li><?php endforeach; ?></ul>
                </article>
            <?php endforeach; ?>
        </div>
    </section>

    <section id="experience">
        <div class="section-head">
            <p class="section-index">02</p>
            <h2>Experience</h2>
        </div>
        <div class="timeline">
            <?php foreach (is_array($profile['experience'] ?? null) ? $profile['experience'] : [] as $job): ?>
                <?php if (!is_array($job)) { continue; } ?>
                <article class="job">
                    <p class="job-when"><?= h((string) ($job['dates'] ?? '')) ?></p>
                    <div class="job-body">
                        <h3><?= h((string) ($job['company'] ?? '')) ?></h3>
                        <p class="job-title"><?= h((string) ($job['title'] ?? '')) ?></p>
                        <p class="meta"><?= h((string) ($job['location'] ?? '')) ?></p>
                        <ul>
                            <?php foreach (is_array($job['bullets'] ?? null) ? $job['bullets'] : [] as $b): ?>
                                <li><?= h((string) $b) ?></li>
                            <?php endforeach; ?>
                        </ul>
                    </div>
                </article>
            <?php endforeach; ?>
        </div>
    </section>

    <section id="certs">
        <div class="section-head">
            <p class="section-index">03</p>
            <h2>Certifications and education</h2>
        </div>
        <div class="split">
            <div>
                <h3 class="kicker">AWS certifications</h3>
                <ul class="cert-list">
                    <?php foreach (is_array($profile['certs'] ?? null) ? $profile['certs'] : [] as $c): ?>
                        <li><?= h((string) $c) ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
            <div>
                <h3 class="kicker">Education</h3>
                <ul class="edu-list">
                    <?php foreach (is_array($profile['education'] ?? null) ? $profile['education'] : [] as $e): ?>
                        <li><?= h((string) $e) ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        </div>
    </section>

    <section id="work">
        <div class="section-head">
            <p class="section-index">04</p>
            <h2>Selected work</h2>
        </div>
        <p class="lede"><?= h((string) ($projects['lede'] ?? '')) ?></p>
        <div class="grid">
            <?php foreach (is_array($projects['items'] ?? null) ? $projects['items'] : [] as $p): ?>
                <?php if (!is_array($p)) { continue; } ?>
                <article class="work-card">
                    <p class="pill"><?= h((string) ($p['status'] ?? '')) ?></p>
                    <h3><?= h((string) ($p['name'] ?? '')) ?></h3>
                    <p class="meta"><?= h((string) ($p['role'] ?? '')) ?></p>
                    <?php if (!empty($p['stack'])): ?><p class="meta"><?= h((string) $p['stack']) ?></p><?php endif; ?>
                    <p><?= h((string) ($p['blurb'] ?? '')) ?></p>
                    <?php if (!empty($p['url']) && str_starts_with((string) $p['url'], 'https://')): ?>
                        <a class="text-link" href="<?= h((string) $p['url']) ?>" target="_blank" rel="noopener noreferrer">View</a>
                    <?php endif; ?>
                </article>
            <?php endforeach; ?>
        </div>
    </section>

    <section id="letter">
        <div class="section-head">
            <p class="section-index">05</p>
            <h2><?= h((string) ($cover['heading'] ?? 'Cover letter')) ?></h2>
        </div>
        <div class="letter-wrap">
            <div class="letter">
                <?php foreach (preg_split("/\n\s*\n/", (string) ($cover['body'] ?? '')) as $para): ?>
                    <?php if (trim($para) === '') { continue; } ?>
                    <p><?= nl2br(h(trim($para)), false) ?></p>
                <?php endforeach; ?>
            </div>
            <p class="actions">
                <a class="btn ghost" href="/downloads/Ettiene-Wium-Cover-Letter.pdf">Letter (PDF)</a>
                <a class="btn ghost" href="/downloads/Ettiene-Wium-Cover-Letter.docx">Letter (DOCX)</a>
            </p>
        </div>
    </section>

    <section id="contact">
        <div class="section-head">
            <p class="section-index">06</p>
            <h2>Contact</h2>
        </div>
        <div class="contact-panel">
            <?php if ($email !== ''): ?><a class="contact-email" href="mailto:<?= h($email) ?>"><?= h($email) ?></a><?php endif; ?>
            <?php if ($phone !== ''): ?><p class="phone"><?= h($phone) ?></p><?php endif; ?>
            <p class="muted"><?= h($location) ?></p>
            <p class="actions">
                <?php if ($email !== ''): ?><a class="btn ghost" href="mailto:<?= h($email) ?>">Email</a><?php endif; ?>
                <?php if (!empty($links['linkedin'])): ?><a class="btn ghost" href="<?= h((string) $links['linkedin']) ?>" target="_blank" rel="noopener noreferrer">LinkedIn</a><?php endif; ?>
                <?php if (!empty($links['github'])): ?><a class="btn ghost" href="<?= h((string) $links['github']) ?>" target="_blank" rel="noopener noreferrer">GitHub</a><?php endif; ?>
            </p>
        </div>
    </section>
</main>
<footer>
    <p>Public profile. Editor is at <a href="/admin/">/admin</a> (private login).</p>
</footer>
</body>
</html>
