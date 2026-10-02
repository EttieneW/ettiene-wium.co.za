/* Void Signal motion: 3D hero, hover tilt, click press. CSP-safe (no inline styles). */
(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function animate(el, props, ms) {
    if (!el || !el.animate) return;
    el.animate(props, { duration: ms || 180, fill: "forwards", easing: "cubic-bezier(0.22, 1, 0.36, 1)" });
  }

  function reveal() {
    var nodes = document.querySelectorAll(".reveal");
    if (!nodes.length) return;
    if (reduce || !("IntersectionObserver" in window)) {
      nodes.forEach(function (n) { n.classList.add("in"); });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );
    nodes.forEach(function (n) { io.observe(n); });
  }

  function navSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll("nav a[href^='#']"));
    if (!links.length) return;
    var map = {};
    links.forEach(function (a) {
      var id = a.getAttribute("href").slice(1);
      var sec = document.getElementById(id);
      if (sec) map[id] = a;
    });
    function set(id) {
      links.forEach(function (a) { a.classList.toggle("is-active", a.getAttribute("href") === "#" + id); });
    }
    if (!("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) set(e.target.id);
        });
      },
      { rootMargin: "-40% 0px -50% 0px", threshold: 0.01 }
    );
    Object.keys(map).forEach(function (id) { io.observe(document.getElementById(id)); });
  }

  function press() {
    document.querySelectorAll(".btn").forEach(function (btn) {
      btn.addEventListener("pointerdown", function () { btn.classList.add("is-down"); });
      btn.addEventListener("pointerup", function () { btn.classList.remove("is-down"); });
      btn.addEventListener("pointerleave", function () { btn.classList.remove("is-down"); });
      btn.addEventListener("click", function () {
        animate(btn, [{ transform: "scale(0.96)" }, { transform: "scale(1.03)" }, { transform: "scale(1)" }], 280);
      });
    });
  }

  function tilt() {
    if (reduce || window.matchMedia("(pointer: coarse)").matches) return;
    var cards = document.querySelectorAll(".tilt, .work-card, .path-card, .skill-card, .job, .letter-wrap");
    cards.forEach(function (card) {
      card.addEventListener("pointermove", function (ev) {
        var r = card.getBoundingClientRect();
        var px = (ev.clientX - r.left) / r.width - 0.5;
        var py = (ev.clientY - r.top) / r.height - 0.5;
        animate(card, { transform: "perspective(900px) rotateX(" + (-py * 8).toFixed(2) + "deg) rotateY(" + (px * 10).toFixed(2) + "deg) translateY(-4px)" }, 140);
      });
      card.addEventListener("pointerleave", function () {
        animate(card, { transform: "perspective(900px) rotateX(0deg) rotateY(0deg) translateY(0)" }, 320);
      });
    });
  }

  function stage3d() {
    var canvas = document.getElementById("stage3d");
    if (!canvas || reduce) return;
    var gl = canvas.getContext("webgl", { antialias: true, alpha: true, preserveDrawingBuffer: true });
    if (!gl) return;

    function compile(type, src) {
      var sh = gl.createShader(type);
      gl.shaderSource(sh, src);
      gl.compileShader(sh);
      return sh;
    }
    var vs = compile(gl.VERTEX_SHADER, [
      "attribute vec3 aPos;",
      "attribute vec3 aCol;",
      "uniform mat4 uMVP;",
      "uniform float uPoint;",
      "varying vec3 vCol;",
      "void main(){",
      "  gl_Position = uMVP * vec4(aPos,1.0);",
      "  gl_PointSize = uPoint;",
      "  vCol = aCol;",
      "}"
    ].join("\n"));
    var fs = compile(gl.FRAGMENT_SHADER, [
      "precision mediump float;",
      "varying vec3 vCol;",
      "uniform float uAlpha;",
      "void main(){",
      "  gl_FragColor = vec4(vCol, uAlpha);",
      "}"
    ].join("\n"));
    var prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    gl.useProgram(prog);
    var aPos = gl.getAttribLocation(prog, "aPos");
    var aCol = gl.getAttribLocation(prog, "aCol");
    var uMVP = gl.getUniformLocation(prog, "uMVP");
    var uPoint = gl.getUniformLocation(prog, "uPoint");
    var uAlpha = gl.getUniformLocation(prog, "uAlpha");

    function mul(a, b) {
      var o = new Float32Array(16);
      for (var c = 0; c < 4; c++) {
        for (var r = 0; r < 4; r++) {
          o[c * 4 + r] =
            a[r] * b[c * 4] +
            a[4 + r] * b[c * 4 + 1] +
            a[8 + r] * b[c * 4 + 2] +
            a[12 + r] * b[c * 4 + 3];
        }
      }
      return o;
    }
    function perspective(fov, aspect, near, far) {
      var f = 1 / Math.tan(fov / 2);
      var nf = 1 / (near - far);
      var m = new Float32Array(16);
      m[0] = f / aspect; m[5] = f; m[10] = (far + near) * nf; m[11] = -1;
      m[14] = 2 * far * near * nf;
      return m;
    }
    function rotateXY(rx, ry) {
      var cx = Math.cos(rx), sx = Math.sin(rx);
      var cy = Math.cos(ry), sy = Math.sin(ry);
      var rxm = new Float32Array([1, 0, 0, 0, 0, cx, sx, 0, 0, -sx, cx, 0, 0, 0, 0, 1]);
      var rym = new Float32Array([cy, 0, -sy, 0, 0, 1, 0, 0, sy, 0, cy, 0, 0, 0, 0, 1]);
      return mul(rym, rxm);
    }

    var t = (1 + Math.sqrt(5)) / 2;
    var raw = [
      [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
      [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
      [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]
    ];
    var verts = raw.map(function (v) {
      var l = Math.hypot(v[0], v[1], v[2]);
      return [v[0] / l, v[1] / l, v[2] / l];
    });
    var faces = [
      [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
      [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
      [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
      [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
    ];
    function mesh(scale, mint, violet) {
      var pos = [];
      var col = [];
      faces.forEach(function (f) {
        for (var e = 0; e < 3; e++) {
          var a = verts[f[e]];
          var b = verts[f[(e + 1) % 3]];
          pos.push(a[0] * scale, a[1] * scale, a[2] * scale, b[0] * scale, b[1] * scale, b[2] * scale);
          var mix = (a[1] + 1) / 2;
          var c = [
            mint[0] + (violet[0] - mint[0]) * mix,
            mint[1] + (violet[1] - mint[1]) * mix,
            mint[2] + (violet[2] - mint[2]) * mix
          ];
          col.push(c[0], c[1], c[2], c[0], c[1], c[2]);
        }
      });
      return { pos: new Float32Array(pos), col: new Float32Array(col), n: pos.length / 3 };
    }
    var outer = mesh(0.92, [0.24, 1.0, 0.78], [0.49, 0.42, 1.0]);
    var inner = mesh(0.48, [1.0, 0.30, 0.55], [0.24, 1.0, 0.78]);

    var pPos = [];
    var pCol = [];
    for (var i = 0; i < 220; i++) {
      var u = Math.random() * Math.PI * 2;
      var v = Math.acos(2 * Math.random() - 1);
      var r = 1.15 + Math.random() * 0.35;
      pPos.push(Math.sin(v) * Math.cos(u) * r, Math.cos(v) * r, Math.sin(v) * Math.sin(u) * r);
      var hot = Math.random() > 0.82;
      if (hot) pCol.push(1.0, 0.30, 0.55);
      else if (Math.random() > 0.5) pCol.push(0.24, 1.0, 0.78);
      else pCol.push(0.49, 0.42, 1.0);
    }
    var particles = { pos: new Float32Array(pPos), col: new Float32Array(pCol), n: pPos.length / 3 };

    function buf(data) {
      var b = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, b);
      gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);
      return b;
    }
    outer.pb = buf(outer.pos); outer.cb = buf(outer.col);
    inner.pb = buf(inner.pos); inner.cb = buf(inner.col);
    particles.pb = buf(particles.pos); particles.cb = buf(particles.col);

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
    gl.enable(gl.DEPTH_TEST);
    gl.clearColor(0, 0, 0, 0);

    var rotY = 0.4;
    var rotX = 0.35;
    var velY = 0.22;
    var targetX = 0.35;
    var targetY = 0.4;
    var dragging = false;
    var last = 0;
    var visible = true;

    canvas.addEventListener("pointerdown", function (ev) {
      dragging = true;
      canvas.setPointerCapture(ev.pointerId);
      velY += 1.8;
    });
    canvas.addEventListener("pointerup", function () { dragging = false; });
    canvas.addEventListener("pointerleave", function () { dragging = false; });
    canvas.addEventListener("pointermove", function (ev) {
      var r = canvas.getBoundingClientRect();
      var nx = (ev.clientX - r.left) / r.width - 0.5;
      var ny = (ev.clientY - r.top) / r.height - 0.5;
      targetY = nx * 1.2;
      targetX = ny * 0.9;
      if (dragging) velY += nx * 0.08;
    });

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0] && entries[0].isIntersecting;
      }, { threshold: 0.05 }).observe(canvas);
    }

    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w = canvas.clientWidth;
      var h = canvas.clientHeight;
      if (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr)) {
        canvas.width = Math.floor(w * dpr);
        canvas.height = Math.floor(h * dpr);
      }
      gl.viewport(0, 0, canvas.width, canvas.height);
    }

    function drawMesh(m, mode, point, alpha) {
      gl.bindBuffer(gl.ARRAY_BUFFER, m.pb);
      gl.enableVertexAttribArray(aPos);
      gl.vertexAttribPointer(aPos, 3, gl.FLOAT, false, 0, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, m.cb);
      gl.enableVertexAttribArray(aCol);
      gl.vertexAttribPointer(aCol, 3, gl.FLOAT, false, 0, 0);
      gl.uniform1f(uPoint, point);
      gl.uniform1f(uAlpha, alpha);
      gl.drawArrays(mode, 0, m.n);
    }

    function frame(now) {
      requestAnimationFrame(frame);
      if (!visible) return;
      resize();
      var dt = Math.min((now - last) / 1000, 0.05) || 0.016;
      last = now;
      velY *= 0.992;
      rotY += velY * dt + (targetY - rotY) * 0.04;
      rotX += (targetX - rotX) * 0.05;
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      var aspect = canvas.width / Math.max(canvas.height, 1);
      var proj = perspective(0.9, aspect, 0.1, 20);
      var view = new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, -3.05, 1]);
      var mvpOuter = mul(proj, mul(view, rotateXY(rotX, rotY)));
      var mvpInner = mul(proj, mul(view, rotateXY(-rotX * 1.2, -rotY * 1.4)));
      gl.uniformMatrix4fv(uMVP, false, mvpOuter);
      drawMesh(outer, gl.LINES, 1, 0.95);
      drawMesh(particles, gl.POINTS, 2.4 * Math.min(window.devicePixelRatio || 1, 2), 0.7);
      gl.uniformMatrix4fv(uMVP, false, mvpInner);
      drawMesh(inner, gl.LINES, 1, 0.85);
    }
    requestAnimationFrame(frame);
  }

  reveal();
  navSpy();
  press();
  tilt();
  stage3d();
})();
