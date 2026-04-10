let sessionId = document.getElementById("sessionId").value;
let currentPapers = [];

function showLoading() {
    document.getElementById("loadingOverlay").style.display = "flex";
}

function hideLoading() {
    document.getElementById("loadingOverlay").style.display = "none";
}

function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove("show");
    }, 4000);
}

function showSections() {
    document.getElementById("section2").style.display = "block";
    document.getElementById("section3").style.display = "block";
    document.getElementById("section4").style.display = "block";
}

document.getElementById("fetchBtn").addEventListener("click", async () => {
    const topic = document.getElementById("topicInput").value.trim();
    const limit = parseInt(document.getElementById("paperCount").value);

    if (!topic) {
        showToast("Please enter a research topic", "error");
        return;
    }

    showLoading();

    try {
        const response = await fetch("/api/fetch-papers", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                topic: topic,
                limit: limit,
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (!data.success) {
            showToast(data.error || "Failed to fetch papers", "error");
            return;
        }

        currentPapers = data.papers || [];

        const statusBox = document.getElementById("fetchStatus");
        statusBox.style.display = "block";

        statusBox.innerHTML = `
            ✅ Papers fetched from API: ${data.fetched}<br>
            ⬇️ Valid downloadable PDFs: ${data.downloaded}
            ${data.downloaded === 0 ? "<br><br>⚠️ No downloadable open-access PDFs found." : ""}
        `;

        if (currentPapers.length === 0) {
            document.getElementById("papersGrid").innerHTML = "<p style='color:#94a3b8;'>No downloadable papers available.</p>";
            document.getElementById("paperSelector").innerHTML = "<p style='color:#94a3b8;'>No downloadable papers available for synthesis.</p>";
            showSections();
            showToast("No downloadable papers found.", "error");
            return;
        }

        renderPapersGrid();
        renderPaperSelector();
        showSections();
        showToast("Downloadable papers loaded successfully!", "success");

        setTimeout(() => {
            document.getElementById("section2").scrollIntoView({ behavior: "smooth", block: "start" });
        }, 300);

    } catch (error) {
        showToast("Error: " + error.message, "error");
    } finally {
        hideLoading();
    }
});

function renderPapersGrid() {
    const grid = document.getElementById("papersGrid");
    grid.innerHTML = "";

    if (currentPapers.length === 0) {
        grid.innerHTML = "<p style='color:#94a3b8;'>No downloadable papers found.</p>";
        return;
    }

    currentPapers.forEach((paper) => {
        const card = document.createElement("div");
        card.className = "paper-card";

        card.innerHTML = `
            <h3>${paper.title}</h3>
            <p><strong>Authors:</strong> ${paper.authors.join(", ")}</p>
            <p><strong>Year:</strong> ${paper.year}</p>
            <div style="margin-top:14px; display:flex; gap:12px; flex-wrap:wrap; align-items:center;">
                <span class="paper-badge available">✅ PDF Available</span>
                <button class="btn btn-view" data-paperid="${paper.id}" style="padding:10px 18px; font-size:0.9rem;">🔗 Open in New Tab</button>
                <button class="btn btn-download" data-paperid="${paper.id}" style="padding:10px 18px; font-size:0.9rem;">📥 Download</button>
            </div>
        `;

        grid.appendChild(card);
    });

    document.querySelectorAll(".btn-view").forEach(btn => {
        btn.addEventListener("click", () => {
            const paperId = btn.getAttribute("data-paperid");
            openPDFNewTab(paperId);
        });
    });

    document.querySelectorAll(".btn-download").forEach(btn => {
        btn.addEventListener("click", () => {
            const paperId = btn.getAttribute("data-paperid");
            downloadPDF(paperId);
        });
    });
}

function renderPaperSelector() {
    const selector = document.getElementById("paperSelector");
    selector.innerHTML = "";

    if (currentPapers.length === 0) {
        selector.innerHTML = "<p style='color:#94a3b8;'>No downloadable papers available for synthesis.</p>";
        return;
    }

    currentPapers.forEach((paper, index) => {
        const item = document.createElement("div");
        item.className = "paper-checkbox-item";

        item.innerHTML = `
            <input type="checkbox" id="paper_${index}" value="${paper.id}" checked>
            <label for="paper_${index}">${paper.title} (${paper.year})</label>
        `;

        selector.appendChild(item);
    });
}

document.getElementById("selectAllBtn").addEventListener("click", () => {
    const boxes = document.querySelectorAll("#paperSelector input[type='checkbox']");
    boxes.forEach(cb => {
        cb.checked = true;
    });
    showToast("All papers selected", "success");
});

document.getElementById("deselectAllBtn").addEventListener("click", () => {
    const boxes = document.querySelectorAll("#paperSelector input[type='checkbox']");
    boxes.forEach(cb => {
        cb.checked = false;
    });
    showToast("All papers deselected", "success");
});

function openPDFNewTab(paperId) {
    const pdfUrl = `/api/pdf/${sessionId}/${paperId}`;
    window.open(pdfUrl, '_blank');
    showToast("PDF opened in new tab!", "success");
}

function downloadPDF(paperId) {
    window.open(`/api/download-pdf/${sessionId}/${paperId}`, "_blank");
    showToast("Download started!", "success");
}

document.getElementById("synthesizeBtn").addEventListener("click", async () => {
    const selected = Array.from(
        document.querySelectorAll("#paperSelector input[type='checkbox']:checked")
    ).map(cb => cb.value);

    if (selected.length === 0) {
        showToast("Please select at least one paper", "error");
        return;
    }

    showLoading();

    try {
        const response = await fetch("/api/synthesize", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                selected_papers: selected,
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (!data.success) {
            showToast(data.error || "Failed to synthesize paper", "error");
            return;
        }

        document.getElementById("synthesisResult").style.display = "block";
        document.getElementById("synthesisContent").innerHTML = data.paper_html;
        showToast("Synthesis generated successfully!", "success");

        setTimeout(() => {
            document.getElementById("synthesisResult").scrollIntoView({ behavior: "smooth", block: "start" });
        }, 300);

    } catch (error) {
        showToast("Error: " + error.message, "error");
    } finally {
        hideLoading();
    }
});

document.getElementById("refineBtn").addEventListener("click", async () => {
    const instruction = document.getElementById("refinementInput").value.trim();

    if (!instruction) {
        showToast("Please enter refinement instructions", "error");
        return;
    }

    showLoading();

    try {
        const response = await fetch("/api/refine", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                instruction: instruction,
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (!data.success) {
            showToast(data.error || "Failed to refine paper", "error");
            return;
        }

        document.getElementById("synthesisContent").innerHTML = data.paper_html;
        document.getElementById("refinementInput").value = "";
        showToast("Paper refined successfully!", "success");

    } catch (error) {
        showToast("Error: " + error.message, "error");
    } finally {
        hideLoading();
    }
});

document.getElementById("downloadSynthesisBtn").addEventListener("click", () => {
    window.open(`/api/download-synthesis/${sessionId}`, "_blank");
    showToast("Synthesis PDF download started!", "success");
});

document.getElementById("compareBtn").addEventListener("click", async () => {
    showLoading();

    try {
        const response = await fetch("/api/compare", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (!data.success) {
            showToast(data.error || "Failed to compare papers", "error");
            return;
        }

        document.getElementById("comparisonResult").style.display = "block";
        document.getElementById("comparisonContent").textContent = data.result;
        showToast("Comparison completed!", "success");

        setTimeout(() => {
            document.getElementById("comparisonResult").scrollIntoView({ behavior: "smooth", block: "start" });
        }, 300);

    } catch (error) {
        showToast("Error: " + error.message, "error");
    } finally {
        hideLoading();
    }
});

console.log("🚀 PaperPilot AI initialized");