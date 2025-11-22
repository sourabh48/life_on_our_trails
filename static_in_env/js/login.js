// static/js/login.js

// --------------------------
// TOGGLE BETWEEN SIGN-IN / SIGN-UP
// --------------------------
const container = document.getElementById("container");

function toggleAuthMode() {
    if (!container) return;
    container.classList.toggle("sign-in");
    container.classList.toggle("sign-up");
}

// Expose globally for onclick in template
window.toggle = toggleAuthMode;

// Ensure default is sign-in panel
setTimeout(() => {
    if (container && !container.classList.contains("sign-in")) {
        container.classList.add("sign-in");
    }
}, 200);


// --------------------------
// ENHANCEMENTS
// --------------------------
document.addEventListener("DOMContentLoaded", () => {

    // ====== LIVE AVATAR PREVIEW ======
    const avatarInput = document.getElementById("avatarInput");
    const avatarPreview = document.getElementById("avatarPreview");

    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener("change", () => {
            const file = avatarInput.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                avatarPreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    // ====== USERNAME AVAILABILITY (AJAX) ======
    const usernameInput = document.getElementById("signupUsername");
    const usernameStatus = document.getElementById("usernameStatus");
    let debounceId = null;

    if (usernameInput && usernameStatus) {
        usernameInput.addEventListener("input", () => {
            const value = usernameInput.value.trim();
            clearTimeout(debounceId);

            if (!value) {
                usernameStatus.textContent = "";
                return;
            }

            if (value.length < 3) {
                usernameStatus.textContent = "Too short";
                usernameStatus.style.color = "orange";
                return;
            }

            const checkUrl =
                usernameInput.dataset.checkUrl || "/check-username/";

            debounceId = setTimeout(() => {
                fetch(`${checkUrl}?username=${encodeURIComponent(value)}`)
                    .then((res) => res.json())
                    .then((data) => {
                        if (data.exists) {
                            usernameStatus.textContent = "Username taken";
                            usernameStatus.style.color = "red";
                        } else {
                            usernameStatus.textContent = "Available ✓";
                            usernameStatus.style.color = "#4EA685";
                        }
                    })
                    .catch(() => {
                        usernameStatus.textContent = "";
                    });
            }, 300);
        });
    }
});
