(function () {
  const loginBox = document.getElementById("login-box");
  const editor = document.getElementById("editor");
  const logoutBtn = document.getElementById("logout");
  const loginError = document.getElementById("login-error");
  const saveStatus = document.getElementById("save-status");

  function lines(id) {
    return document.getElementById(id).value.split("\n").map((s) => s.trim()).filter(Boolean);
  }
  function setLines(id, arr) {
    document.getElementById(id).value = Array.isArray(arr) ? arr.join("\n") : "";
  }
  function parseJson(id) {
    return JSON.parse(document.getElementById(id).value || "[]");
  }

  async function api(path, opts) {
    const res = await fetch(path, Object.assign({ credentials: "same-origin" }, opts));
    const ctype = res.headers.get("content-type") || "";
    const data = ctype.includes("json") ? await res.json() : null;
    if (!res.ok) {
      throw new Error((data && data.error) || ("HTTP " + res.status));
    }
    return data;
  }

  function fill(site) {
    const p = site.profile || {};
    const links = p.links || {};
    const skills = p.skills || {};
    document.getElementById("name").value = p.name || "";
    document.getElementById("headline").value = p.headline || "";
    document.getElementById("location").value = p.location || "";
    document.getElementById("email").value = p.email || "";
    document.getElementById("phone").value = p.phone || "";
    document.getElementById("github").value = links.github || "";
    document.getElementById("linkedin").value = links.linkedin || "";
    document.getElementById("summary").value = p.summary || "";
    setLines("skills-ops", skills.ops);
    setLines("skills-cloud", skills.cloud);
    setLines("skills-data", skills.data);
    setLines("skills-backend", skills.backend);
    setLines("skills-languages", skills.languages);
    document.getElementById("experience").value = JSON.stringify(p.experience || [], null, 2);
    setLines("certs", p.certs);
    setLines("education", p.education);
    const c = site.cover_letter || {};
    document.getElementById("letter-heading").value = c.heading || "";
    document.getElementById("letter-body").value = c.body || "";
    const pr = site.projects || {};
    document.getElementById("projects-lede").value = pr.lede || "";
    document.getElementById("projects-items").value = JSON.stringify(pr.items || [], null, 2);
  }

  function collect() {
    return {
      profile: {
        name: document.getElementById("name").value.trim(),
        headline: document.getElementById("headline").value.trim(),
        location: document.getElementById("location").value.trim(),
        email: document.getElementById("email").value.trim(),
        phone: document.getElementById("phone").value.trim(),
        links: {
          github: document.getElementById("github").value.trim(),
          linkedin: document.getElementById("linkedin").value.trim(),
          portfolio: "https://ettiene-wium.com"
        },
        summary: document.getElementById("summary").value,
        skills: {
          ops: lines("skills-ops"),
          cloud: lines("skills-cloud"),
          data: lines("skills-data"),
          backend: lines("skills-backend"),
          languages: lines("skills-languages")
        },
        experience: parseJson("experience"),
        certs: lines("certs"),
        education: lines("education")
      },
      cover_letter: {
        heading: document.getElementById("letter-heading").value.trim(),
        body: document.getElementById("letter-body").value
      },
      projects: {
        lede: document.getElementById("projects-lede").value.trim(),
        items: parseJson("projects-items")
      }
    };
  }

  async function showEditor() {
    const data = await api("/api/content");
    fill(data.site);
    loginBox.hidden = true;
    editor.hidden = false;
    logoutBtn.hidden = false;
  }

  document.getElementById("login-form").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    loginError.hidden = true;
    const fd = new FormData(ev.target);
    try {
      await api("/api/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ username: fd.get("username"), password: fd.get("password") })
      });
      await showEditor();
    } catch (err) {
      loginError.textContent = err.message;
      loginError.hidden = false;
    }
  });

  document.getElementById("save").addEventListener("click", async () => {
    saveStatus.textContent = "Saving…";
    try {
      const site = collect();
      await api("/api/content", {
        method: "PUT",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(site)
      });
      saveStatus.textContent = "Published. Public page, CV, and cover letter files updated.";
    } catch (err) {
      saveStatus.textContent = "Save failed: " + err.message;
    }
  });

  logoutBtn.addEventListener("click", async () => {
    await api("/api/logout", { method: "POST" });
    location.reload();
  });

  api("/api/session").then((s) => { if (s.authed) return showEditor(); }).catch(() => {});
})();
