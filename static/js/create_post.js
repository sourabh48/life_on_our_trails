/* =====================================================
   QUILL EDITOR INIT
===================================================== */

const editor = new Quill("#quill-editor", {
    theme: "snow",
    placeholder: "Start writing your article…",
    modules: {
        toolbar: [
            [{font: []}],
            [{size: ["small", false, "large", "huge"]}],
            [{header: [1, 2, 3, 4, 5, 6, false]}],
            ["bold", "italic", "underline", "strike"],
            [{color: []}, {background: []}],
            [{script: "sub"}, {script: "super"}],
            [{list: "ordered"}, {list: "bullet"}],
            [{indent: "-1"}, {indent: "+1"}],
            [{align: []}],
            ["blockquote", "code-block"],
            ["link", "image", "video"],
            ["clean"],
        ],
    },
});
editor.root.setAttribute("spellcheck", "true");

/* =====================================================
   DOM ELEMENTS
===================================================== */

const formEl = document.getElementById("post-create-form");
const titleField = document.getElementById("id_title");
const metaField = document.getElementById("id_meta_description");
const statusSelect = document.getElementById("id_status");
const imageInput = document.getElementById("id_image");
const categorySelect = document.getElementById("id_category");
const newCategoryInput = document.getElementById("id_new_category");

let selectedTags = []; // existing tag objects {id, name}
let newTags = [];      // new tag names ["travel", "coding"]
let suggestions = [];
let suggestionIndex = -1;

/* =====================================================
   EDITOR HELPERS
===================================================== */

function getWordCount() {
    const text = editor.getText().trim().replace(/\s+/g, " ");
    return text ? text.split(" ").length : 0;
}

function getPlainText() {
    return editor.getText().replace(/\s+/g, " ").trim();
}

function validateEditor() {
    const wc = getWordCount();
    const box = document.getElementById("content-error");

    if (wc < 20) {
        box.textContent = "Please write some content before saving.";
        box.style.display = "block";
        return false;
    }
    box.style.display = "none";
    return true;
}

/* =====================================================
   FORM SUBMISSION
===================================================== */

if (formEl) {
    formEl.addEventListener("submit", (e) => {
        if (!validateEditor()) {
            e.preventDefault();
            return;
        }
        document.getElementById("content-input").value = editor.root.innerHTML;
    });
}

/* =====================================================
   LIVE METRICS (SEO + GRAMMAR)
===================================================== */

const wordsEl = document.getElementById("stat-words");
const readingEl = document.getElementById("stat-reading");
const seoScoreEl = document.getElementById("stat-seo-score");
const seoBarFill = document.getElementById("seo-bar-fill");
const seoBarLabel = document.getElementById("seo-bar-label");
const grammarHintsEl = document.getElementById("grammar-hints");

function estimateReadingTime(words) {
    return Math.max(1, Math.round(words / 200));
}

function computeSeoScore(words, title, meta) {
    let score = 0;

    if (words >= 300) score += 25;
    else if (words >= 150) score += 15;

    if (title.length >= 30 && title.length <= 70) score += 25;
    if (meta.length >= 80 && meta.length <= 160) score += 25;

    if (editor.root.innerHTML.match(/<h[1-3]/gi)) score += 15;
    if (editor.root.innerHTML.match(/<a\s/gi)) score += 10;

    return Math.min(score, 100);
}

function grammarHints(text) {
    const hints = [];
    if (/ {2,}/.test(text)) hints.push("Multiple spaces found.");
    if (/\b(\w+)\s+\1\b/i.test(text)) hints.push("Repeated word detected.");
    if (text.split(/[.!?]/).some(s => s.trim().split(/\s+/).length > 30))
        hints.push("Some sentences are too long.");
    return hints;
}

function updateMetrics() {
    const words = getWordCount();
    const title = titleField?.value || "";
    const meta = metaField?.value || "";

    wordsEl.textContent = words;
    readingEl.textContent = estimateReadingTime(words) + " min";

    const score = computeSeoScore(words, title, meta);
    seoScoreEl.textContent = score;
    seoBarFill.style.width = score + "%";
    seoBarLabel.textContent =
        score < 40 ? "Too weak – add more content." :
            score < 70 ? "Decent – improve title/meta." : "Strong SEO ✓";

    const hints = grammarHints(getPlainText());
    grammarHintsEl.innerHTML = hints.length
        ? "<ul>" + hints.map(h => `<li>${h}</li>`).join("") + "</ul>"
        : "";

    togglePublishLock();
}

editor.on("text-change", updateMetrics);
titleField?.addEventListener("input", updateMetrics);
metaField?.addEventListener("input", updateMetrics);

/* =====================================================
   AUTOSAVE
===================================================== */

const DRAFT_KEY = "create_post_draft_v2";

function saveDraft() {
    try {
        localStorage.setItem(
            DRAFT_KEY,
            JSON.stringify({
                title: titleField.value,
                content: editor.root.innerHTML,
                meta_title: document.getElementById("id_meta_title").value,
                meta_description: metaField.value,
                category: categorySelect.value,
                status: statusSelect.value,
            })
        );
    } catch (e) {
    }
}

function loadDraft() {
    try {
        const saved = JSON.parse(localStorage.getItem(DRAFT_KEY));
        if (!saved) return;

        titleField.value = saved.title;
        document.getElementById("id_meta_title").value = saved.meta_title;
        metaField.value = saved.meta_description;
        editor.root.innerHTML = saved.content;
        categorySelect.value = saved.category;
        statusSelect.value = saved.status;

        updateMetrics();
    } catch (e) {
    }
}

loadDraft();
setInterval(saveDraft, 5000);

/* =====================================================
   PUBLISH LOCK
===================================================== */

const MIN_PUBLISH_WORDS = 500;
const scheduleWrapper = document.getElementById("schedule-wrapper");

function toggleSchedule() {
    scheduleWrapper.style.display =
        statusSelect.value === "scheduled" ? "block" : "none";
}

function togglePublishLock() {
    const btn = document.querySelector(".create-post-btn");
    const msg = document.getElementById("publish-lock-msg");

    const strict = ["published", "scheduled"].includes(statusSelect.value);

    if (!strict) {
        btn.disabled = false;
        msg.textContent = "Status: Draft – you can save anytime.";
        return;
    }

    const reasons = [];
    const wc = getWordCount();

    if (titleField.value.length < 10) reasons.push("Title (10 chars)");
    if (!imageInput.files.length) reasons.push("Featured image");
    if (!categorySelect.value && !newCategoryInput.value.trim())
        reasons.push("Category");
    if (selectedTags.length === 0 && newTags.length === 0)
        reasons.push("Tags (min 1)");
    if (wc < MIN_PUBLISH_WORDS)
        reasons.push("500+ words");

    const locked = reasons.length > 0;

    btn.disabled = locked;
    btn.classList.toggle("btn-disabled", locked);
    msg.textContent = locked
        ? "Complete before publishing: " + reasons.join(", ")
        : "Ready to publish ✓";
}

statusSelect?.addEventListener("change", () => {
    toggleSchedule();
    togglePublishLock();
});

/* =====================================================
   AI TOOLBAR
===================================================== */

const AI_WRITE_URL = "/ai/write/";
const AI_IMPROVE_URL = "/ai/improve/";
const AI_FIX_URL = "/ai/fix/";
const aiStatusEl = document.getElementById("ai-status");

function csrftoken() {
    return document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="))
        ?.split("=")[1];
}

function setAIStatus(text, error = false) {
    aiStatusEl.textContent = text;
    aiStatusEl.classList.toggle("ai-status-error", error);
}

async function aiCall(url, payload, mode) {
    try {
        setAIStatus("Thinking…");

        const res = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken(),
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!data.result) {
            setAIStatus("AI error", true);
            return;
        }

        editor.root.innerHTML =
            mode === "append"
                ? editor.root.innerHTML + data.result
                : data.result;

        updateMetrics();
        setAIStatus("Done ✓");
        setTimeout(() => setAIStatus(""), 1500);

    } catch (e) {
        setAIStatus("Network error", true);
    }
}

document.getElementById("ai-write-btn")?.addEventListener("click", () => {
    if (!titleField.value.trim()) {
        setAIStatus("Enter a title first.", true);
        return;
    }
    aiCall(AI_WRITE_URL, {prompt: titleField.value}, "append");
});

document.getElementById("ai-improve-btn")?.addEventListener("click", () => {
    aiCall(AI_IMPROVE_URL, {content: editor.root.innerHTML}, "replace");
});

document.getElementById("ai-fix-btn")?.addEventListener("click", () => {
    aiCall(AI_FIX_URL, {content: editor.root.innerHTML}, "replace");
});

/* =====================================================
   TAG MANAGER — AUTOCOMPLETE + MULTI-TAGS
===================================================== */

const tagInput = document.getElementById("tag-input");
const tagChips = document.getElementById("tag-chips");
const tagSuggestBox = document.getElementById("tag-suggest-box");
const selectedTagsInput = document.getElementById("selected-tags");
const newTagsHidden = document.getElementById("new-tags");

/* -----------------------------------------------
   Helper: Add MULTIPLE tags separated by commas
------------------------------------------------ */
function addMultipleTags(raw) {
    raw.split(",")
        .map(t => t.trim())
        .filter(t => t.length > 0)
        .forEach(t => {
            if (!newTags.includes(t) &&
                !selectedTags.some(x => x.name === t)
            ) {
                newTags.push(t);
            }
        });

    tagInput.value = "";
    renderChips();
}

/* -----------------------------------------------
   Helper: Add new tag
------------------------------------------------ */
function addNewTag(name) {
    const clean = name.trim();
    if (clean && !newTags.includes(clean)) newTags.push(clean);
    tagInput.value = "";
    closeSuggest();
    renderChips();
}

/* -----------------------------------------------
   Helper: Add existing tag (from suggestions)
------------------------------------------------ */
function addExistingTag(tag) {
    if (!selectedTags.some(t => t.id === tag.id)) {
        selectedTags.push(tag);
    }
    tagInput.value = "";
    closeSuggest();
    renderChips();
}

/* -----------------------------------------------
   Render tag chips
------------------------------------------------ */
function renderChips() {
    tagChips.innerHTML = "";

    selectedTags.forEach(t => {
        const chip = document.createElement("div");
        chip.className = "tag-chip";
        chip.innerHTML = `${t.name} <span data-id="${t.id}" class="tag-chip-remove">&times;</span>`;
        tagChips.appendChild(chip);
    });

    newTags.forEach(name => {
        const chip = document.createElement("div");
        chip.className = "tag-chip";
        chip.innerHTML = `${name} <span data-new="${name}" class="tag-chip-remove">&times;</span>`;
        tagChips.appendChild(chip);
    });

    selectedTagsInput.value = selectedTags.map(t => t.id).join(",");
    newTagsHidden.value = newTags.join(", ");
    togglePublishLock();
}

/* -----------------------------------------------
   Fetch tag suggestions
------------------------------------------------ */
async function fetchTagSuggestions(q) {
    const r = await fetch(`/tags/suggest/?q=${encodeURIComponent(q)}`);
    return r.json();
}

/* -----------------------------------------------
   Render suggestions dropdown
------------------------------------------------ */
function renderSuggestions() {
    tagSuggestBox.innerHTML = "";
    tagSuggestBox.style.display = "block";

    suggestions.forEach((tag, i) => {
        const item = document.createElement("div");
        item.className = "tag-suggest-item";
        if (i === suggestionIndex) item.classList.add("active");
        item.textContent = tag.name;
        item.addEventListener("click", () => addExistingTag(tag));
        tagSuggestBox.appendChild(item);
    });

    const createItem = document.createElement("div");
    createItem.className = "tag-suggest-item";
    if (suggestionIndex === suggestions.length) createItem.classList.add("active");
    createItem.textContent = `Create tag: ${tagInput.value}`;
    createItem.addEventListener("click", () => addNewTag(tagInput.value));
    tagSuggestBox.appendChild(createItem);
}

function closeSuggest() {
    tagSuggestBox.style.display = "none";
    suggestions = [];
    suggestionIndex = -1;
}

/* -----------------------------------------------
   INPUT HANDLERS
------------------------------------------------ */

// Typing
tagInput?.addEventListener("input", async () => {
    const q = tagInput.value.trim();

    if (!q) {
        closeSuggest();
        return;
    }

    // If user types comma → instantly split tags
    if (q.includes(",")) {
        addMultipleTags(q);
        closeSuggest();
        return;
    }

    // Fetch suggestions
    const data = await fetchTagSuggestions(q);
    suggestions = data.results || [];
    suggestionIndex = -1;
    renderSuggestions();
});

// Keyboard navigation + multi-tag enter support
tagInput?.addEventListener("keydown", (e) => {
    const val = tagInput.value.trim();

    // COMMA → create multiple tags
    if (e.key === ",") {
        e.preventDefault();
        if (val.length > 0) addMultipleTags(val);
        return;
    }

    // ENTER → create tag or select suggestion
    if (e.key === "Enter") {
        e.preventDefault();

        if (val.includes(",")) {
            addMultipleTags(val);
            return;
        }

        if (suggestionIndex >= 0 && suggestionIndex < suggestions.length) {
            addExistingTag(suggestions[suggestionIndex]);
            return;
        }

        addNewTag(val);
        return;
    }

    // Suggestion navigation
    const total = suggestions.length + 1;

    if (e.key === "ArrowDown") {
        e.preventDefault();
        suggestionIndex = (suggestionIndex + 1) % total;
        renderSuggestions();
    }

    if (e.key === "ArrowUp") {
        e.preventDefault();
        suggestionIndex = (suggestionIndex - 1 + total) % total;
        renderSuggestions();
    }
});

/* -----------------------------------------------
   BLUR HANDLER (FIXED)
------------------------------------------------ */

tagInput?.addEventListener("blur", () => {
    setTimeout(() => {
        const val = tagInput.value.trim();

        // If user clicked a suggestion → ignore
        if (
            document.activeElement === tagSuggestBox ||
            tagSuggestBox.contains(document.activeElement)
        ) return;

        if (!val) {
            closeSuggest();
            return;
        }

        // Support multi-tags on blur
        if (val.includes(",")) {
            addMultipleTags(val);
            closeSuggest();
            return;
        }

        // Only create if no suggestions available
        if (suggestions.length === 0) {
            addNewTag(val);
        }

        closeSuggest();
    }, 150);
});

/* -----------------------------------------------
   REMOVE CHIP
------------------------------------------------ */

tagChips?.addEventListener("click", (e) => {
    if (!e.target.classList.contains("tag-chip-remove")) return;

    const id = e.target.dataset.id;
    const name = e.target.dataset.new;

    if (id) selectedTags = selectedTags.filter(t => t.id != id);
    if (name) newTags = newTags.filter(t => t !== name);

    renderChips();
});

/* -----------------------------------------------
   Close suggestion on outside click
------------------------------------------------ */

document.addEventListener("click", (e) => {
    if (!tagInput.contains(e.target) && !tagSuggestBox.contains(e.target)) {
        closeSuggest();
    }
});

/* =====================================================
   INIT JS
===================================================== */
renderChips();
updateMetrics();
toggleSchedule();
togglePublishLock();
