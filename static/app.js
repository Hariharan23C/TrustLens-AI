// TrustLens AI -- dashboard frontend
// Handles tab switching, form submission to the Flask API, client-side QR
// decoding (so images never leave the browser), and the recent-scans table.

document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".tab");
  const forms = document.querySelectorAll(".check-form");
  const resultZone = document.getElementById("resultZone");

  // ---------- Tabs ----------
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => { t.classList.remove("active"); t.setAttribute("aria-selected", "false"); });
      tab.classList.add("active"); tab.setAttribute("aria-selected", "true");

      forms.forEach(f => f.classList.remove("active"));
      const target = document.getElementById(`form-${tab.dataset.tab}`);
      if (target) target.classList.add("active");

      resultZone.hidden = true;
    });
  });

  // ---------- Generic form -> API submit ----------
  forms.forEach(form => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const endpoint = form.dataset.endpoint;
      const payload = {};
      new FormData(form).forEach((value, key) => { payload[key] = value; });

      const btn = form.querySelector(".run-btn");
      const originalLabel = btn.textContent;
      btn.disabled = true;
      btn.textContent = "Scanning…";

      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error(`Server responded ${res.status}`);
        const result = await res.json();
        renderResult(result);
        refreshHistoryAndStats();
      } catch (err) {
        renderResult({
          verdict: "caution",
          risk_score: 0,
          reasons: [`Couldn't reach the server (${err.message}). Is app.py running?`],
        });
      } finally {
        btn.disabled = false;
        btn.textContent = originalLabel;
      }
    });
  });

  // ---------- Result rendering ----------
  function renderResult(result) {
    const stamp = document.getElementById("verdictStamp");
    const fill = document.getElementById("scoreFill");
    const num = document.getElementById("scoreNum");
    const list = document.getElementById("reasonsList");

    stamp.className = "stamp " + result.verdict;
    stamp.textContent = result.verdict === "danger" ? "HIGH RISK"
                       : result.verdict === "caution" ? "USE CAUTION"
                       : "LOOKS SAFE";

    fill.style.width = `${result.risk_score}%`;
    fill.style.background = result.verdict === "danger" ? "var(--danger)"
                            : result.verdict === "caution" ? "var(--caution)"
                            : "var(--safe)";
    num.textContent = `${result.risk_score}/100`;

    list.innerHTML = "";
    (result.reasons || []).forEach(reason => {
      const li = document.createElement("li");
      li.textContent = reason;
      list.appendChild(li);
    });

    resultZone.hidden = false;
    resultZone.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // ---------- QR: decode client-side with jsQR, then submit decoded text ----------
  const qrFileInput = document.getElementById("input-qr-file");
  const qrDecodedBox = document.getElementById("qrDecoded");
  const qrDecodedText = document.getElementById("qrDecodedText");
  const qrSubmitBtn = document.getElementById("qrSubmitBtn");
  const qrHint = document.getElementById("qrHint");
  let decodedQrContent = "";

  if (qrFileInput) {
    qrFileInput.addEventListener("change", () => {
      const file = qrFileInput.files[0];
      if (!file) return;

      qrHint.textContent = "Decoding…";
      const img = new Image();
      const reader = new FileReader();

      reader.onload = (e) => { img.src = e.target.result; };
      reader.onerror = () => { qrHint.textContent = "Couldn't read that file."; };

      img.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const code = window.jsQR ? jsQR(imageData.data, imageData.width, imageData.height) : null;

        if (code && code.data) {
          decodedQrContent = code.data;
          qrDecodedText.textContent = code.data;
          qrDecodedBox.hidden = false;
          qrSubmitBtn.disabled = false;
          qrHint.textContent = "Decoded entirely in your browser — the image itself is never uploaded.";
        } else {
          decodedQrContent = "";
          qrDecodedBox.hidden = true;
          qrSubmitBtn.disabled = true;
          qrHint.textContent = "Couldn't detect a QR code in that image. Try a clearer photo/screenshot.";
        }
      };
      img.onerror = () => { qrHint.textContent = "Couldn't load that image."; };

      reader.readAsDataURL(file);
    });
  }

  const qrForm = document.getElementById("form-qr");
  if (qrForm) {
    qrForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!decodedQrContent) return;

      const btn = qrSubmitBtn;
      const originalLabel = btn.textContent;
      btn.disabled = true;
      btn.textContent = "Scanning…";

      try {
        const res = await fetch("/api/check-qr", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ decoded_text: decodedQrContent }),
        });
        const result = await res.json();
        renderResult(result);
        refreshHistoryAndStats();
      } catch (err) {
        renderResult({ verdict: "caution", risk_score: 0, reasons: [`Couldn't reach the server (${err.message}).`] });
      } finally {
        btn.disabled = false;
        btn.textContent = originalLabel;
      }
    });
  }

  // ---------- History + stats ----------
  async function refreshHistoryAndStats() {
    try {
      const [historyRes, statsRes] = await Promise.all([
        fetch("/api/history"),
        fetch("/api/stats"),
      ]);
      const history = await historyRes.json();
      const stats = await statsRes.json();
      renderHistory(history);
      renderStats(stats);
    } catch (err) {
      // Non-critical: history/stats failing shouldn't block the main flow.
      console.warn("Couldn't refresh history/stats:", err);
    }
  }

  function renderHistory(rows) {
    const body = document.getElementById("historyBody");
    if (!rows || rows.length === 0) {
      body.innerHTML = `<tr><td colspan="5" class="empty-row">No scans yet — run your first check above.</td></tr>`;
      return;
    }
    body.innerHTML = rows.map(row => `
      <tr>
        <td>${escapeHtml(labelForType(row.check_type))}</td>
        <td class="input-cell" title="${escapeHtml(row.input_summary)}">${escapeHtml(row.input_summary || "—")}</td>
        <td><span class="verdict-pill ${row.verdict}">${escapeHtml(row.verdict)}</span></td>
        <td>${row.risk_score}/100</td>
        <td>${formatWhen(row.created_at)}</td>
      </tr>
    `).join("");
  }

  function renderStats(stats) {
    document.getElementById("statTotal").textContent = stats.total ?? 0;
    document.getElementById("statFlagged").textContent = stats.flagged ?? 0;
  }

  function labelForType(t) {
    return {
      url: "URL", email: "Email", internship: "Internship",
      offer_letter: "Offer Letter", qr: "QR Code", message: "Message",
    }[t] || t;
  }

  function formatWhen(iso) {
    try {
      const d = new Date(iso);
      return d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    } catch { return iso; }
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str ?? "";
    return div.innerHTML;
  }

  // Initial load
  refreshHistoryAndStats();
});
