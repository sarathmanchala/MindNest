document.addEventListener("DOMContentLoaded", function () {

    /* ================================
       ANALYSIS SECTION
    ================================= */

    const analysisForm = document.getElementById("analysisForm");

    if (analysisForm) {

        const analyzeBtn = document.getElementById("analyzeBtn");
        const btnText = document.getElementById("btnText");
        const btnLoader = document.getElementById("btnLoader");

        const resultPlaceholder = document.getElementById("resultPlaceholder");
        const analysisResult = document.getElementById("analysisResult");

        const summaryText = document.getElementById("summaryText");
        const moodBadge = document.getElementById("moodBadge");
        const keyEmotion = document.getElementById("keyEmotion");
        const suggestedFocus = document.getElementById("suggestedFocus");

        analysisForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const reflectionInput = document.getElementById("dayReflection");
            const dayReflection = reflectionInput ? reflectionInput.value.trim() : "";

            // ✅ Client-side validation
            if (!dayReflection) {
                alert("Please write something about your day before analyzing.");
                return;
            }

            // ✅ Loading state
            if (btnText) btnText.innerText = "Analyzing...";
            if (btnLoader) btnLoader.classList.remove("d-none");
            if (analyzeBtn) analyzeBtn.disabled = true;

            try {
                const response = await fetch("/analyze", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ text: dayReflection })
                });

                // ✅ Check content type before parsing JSON
                const contentType = response.headers.get("content-type");
                if (!contentType || !contentType.includes("application/json")) {
                    throw new Error("Server did not return JSON.");
                }

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || "Analysis failed.");
                }

                // ✅ Ensure expected fields exist
                if (!result.summary || !result.mood_label || result.score === undefined) {
                    throw new Error("Invalid response format from server.");
                }

                // ✅ Update UI
                if (resultPlaceholder) resultPlaceholder.classList.add("d-none");
                if (analysisResult) analysisResult.classList.remove("d-none");

                if (summaryText) summaryText.innerText = result.summary;
                if (moodBadge) moodBadge.innerText = `${result.mood_label} (${result.score}/10)`;
                if (suggestedFocus) suggestedFocus.innerText = result.advice || "";
                if (keyEmotion) keyEmotion.innerText = result.mood_label;

                updateMoodStyling(result.mood_label, result.score, moodBadge);

            } catch (error) {
                console.error("Error:", error);
                alert(error.message || "Something went wrong.");
            } finally {
                // ✅ Reset button state
                if (btnText) btnText.innerText = "✨ Analyse My Day";
                if (btnLoader) btnLoader.classList.add("d-none");
                if (analyzeBtn) analyzeBtn.disabled = false;
            }
        });
    }


    /* ================================
       MOOD STYLING FUNCTION
    ================================= */

    function updateMoodStyling(mood, score, badgeElement) {
        if (!badgeElement) return;

        badgeElement.classList.remove("bg-success", "bg-warning", "bg-primary", "text-white", "text-dark");
        badgeElement.classList.add("badge", "rounded-pill", "px-3");

        const moodLower = mood.toLowerCase();

        if (score >= 7 || moodLower.includes("happy") || moodLower.includes("calm") || moodLower.includes("great")) {
            badgeElement.classList.add("bg-success", "text-white");
        } else if (score <= 4 || moodLower.includes("sad") || moodLower.includes("anxious") || moodLower.includes("stressed")) {
            badgeElement.classList.add("bg-warning", "text-dark");
        } else {
            badgeElement.classList.add("bg-primary", "text-white");
        }
    }


    /* ================================
       SEARCH FUNCTIONALITY
    ================================= */

    const searchReflection = document.getElementById("searchReflection");
    const searchInput = document.getElementById("searchInput");

    if (searchReflection && searchInput) {
        searchReflection.addEventListener("click", async function (e) {
            e.preventDefault();
            console.log("Search button clicked");
            const query = searchInput.value.trim();
            if (!query){
                alert("Please enter a search term ");
                return;
            }
            try{
                const response = await fetch(`/entry/${encodeURIComponent(query)}`);
                if (!response.ok){
                    throw new Error("Search failed");
                }
                const results = await response.json();
                const container = document.querySelector(".col-lg-10");
                container.innerHTML = "";
                if (results.length === 0){
                    container.innerHTML = `
                    <div class="text-center py-5">
                        <h3 class="text-muted">No reflections found. 🌱</h3>
                    </div>
                `;
                return;
                }
                results.forEach(entry => {

                const card = document.createElement("div");
                card.className = "card border-0 shadow-sm mb-4 rounded-4 overflow-hidden journal-card";

                card.innerHTML = `
                    <div class="card-body p-4">
                        <small class="text-uppercase fw-bold text-muted">
                            ${entry.timestamp}
                        </small>
                        <h5 class="fw-bold mt-2">Daily Reflection</h5>
                        <p class="mt-3">${entry.content}</p>

                        <div class="mt-3">
                            <span class="badge bg-light text-dark border rounded-pill">
                                ${entry.mood_label} (${entry.mood_score}/10)
                            </span>
                        </div>

                        <div class="mt-2">
                            <small class="text-muted">AI Advice:</small>
                            <p class="small">${entry.advice}</p>
                        </div>
                    </div>
                `;

                container.appendChild(card);
            });

        } catch (error) {
            console.error("Search error:", error);
            alert("Something went wrong while searching.");
        }
        });
    }

    // Delete functionality

    document.addEventListener("click", async function(e){
        const deleteBtn = e.target.closest(".delete-btn");
        if (!deleteBtn) return;
        const entryId = deleteBtn.dataset.id;
        const confirmed = confirm("Are you sure you want to delete this entry?");
        if (!confirmed) return;
        try{
            const response = await fetch(`/delete/${entryId}`, {
                method: "DELETE",
                headers: {
                    'Content-Type' : 'application/json'
                }
            });
            const result = await response.json();
            if (!response.ok || !result.success){
                throw new Error("Failed to delete entry.");
            }
            const card = document.getElementById(`entry-${entryId}`);
            if (card){
                card.style.transistion = "opcaity 0.3s ease";
                card.style.opacity = "0";
                setTimeout(() => {
                    card.remove();
                }, 300);
            }
        }
        catch(error){
            console.error("Delete error:", error);
            alert("Something went wrong while deleting the entry.");
        }
    });
});
