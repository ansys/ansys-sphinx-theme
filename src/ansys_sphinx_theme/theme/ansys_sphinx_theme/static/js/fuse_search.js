// Global search options
src = "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js";

// Configure RequireJS
require.config({
  paths: {
    fuse: "https://cdn.jsdelivr.net/npm/fuse.js@6.4.6/dist/fuse.min",
  },
});

// Main script for search functionality
require(["fuse"], function (Fuse) {
  let fuseInstance;
  let searchData = []; // Track selected result
  let currentIndex = -1;

  // Initialize Fuse.js with search data and options
  function initializeFuse(data) {
    const fuseOptions = theme_static_search;
    fuseInstance = new Fuse(data, fuseOptions);
    searchData = data; // Save the search data for later use
  }

  // Perform search with Fuse.js
  function performSearch(query) {
    const results = fuseInstance.search(query, {
      limit: parseInt(theme_limit),
    });
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = "";
    currentIndex = -1; // Reset index on each new search

    if (results.length === 0) {
      displayNoResultsMessage(resultsContainer);
      return;
    }

    // Show the results container if there's a query
    if (query === "") {
      resultsContainer.style.display = "none";
      return;
    }
    resultsContainer.style.display = "block";

    // Populate results
    results.forEach((result) => {
      const { title, text, href } = result.item;
      const item = createResultItem(title, text, href, query);
      resultsContainer.appendChild(item);
    });
  }

  // Display "No matched documents" message
  function displayNoResultsMessage(container) {
    const noResultsMessage = document.createElement("div");
    noResultsMessage.className = "no-results";
    noResultsMessage.textContent = "No matched documents";
    container.appendChild(noResultsMessage);
  }

  // Create and return a result item
  function createResultItem(title, text, href, query) {
    const item = document.createElement("div");
    item.className = "result-item";
    item.setAttribute("tabindex", "0"); // Make result focusable

    const highlightedTitle = highlightTerms(title, query);
    const highlightedText = highlightTerms(text, query);

    item.innerHTML = `
      <div class="result-title">${highlightedTitle}</div>
      <div class="result-text">${highlightedText}</div>
    `;
    item.setAttribute("data-href", href);

    // Navigate to the result's href on click
    item.addEventListener("click", () => navigateToHref(href));
    return item;
  }

  // Highlight matching terms in search results
  function highlightTerms(text, query) {
    if (!query.trim()) return text;
    const words = query.trim().split(/\s+/);
    const escapedWords = words.map((word) =>
      word.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&"),
    );
    const regex = new RegExp(`(${escapedWords.join("|")})`, "gi");
    return text.replace(regex, '<span class="highlight">$1</span>');
  }

  // Navigate to the href
  function navigateToHref(href) {
    const baseUrl = window.location.origin;
    const relativeUrl = href.startsWith("/") ? href : `/${href}`;
    window.location.href = new URL(relativeUrl, baseUrl).href;
  }

  // Event listeners
  const searchBox = document
    .getElementById("search-bar")
    .querySelector(".bd-search input");

  // Handle input in the search box
  searchBox.addEventListener("input", function () {
    const query = this.value.trim();
    if (query.length < parseInt(min_chars_for_search)) {
      document.getElementById("results").innerHTML = "";
      return;
    }
    performSearch(query);
  });

  searchBox.addEventListener("keydown", function (event) {
    const resultsContainer = document.getElementById("results");
    const resultItems = resultsContainer.querySelectorAll(".result-item");

    // Handle Enter key press
    if (event.key === "Enter") {
      if (currentIndex >= 0 && currentIndex < resultItems.length) {
        const selectedResult = resultItems[currentIndex];
        navigateToHref(selectedResult.getAttribute("data-href"));
      }
      event.preventDefault();
    }

    // use keycode

    // Handle arrow down key
    if (event.key === "ArrowDown") {
      if (resultItems.length > 0) {
        // Move to the next item
        currentIndex = (currentIndex + 1) % resultItems.length; // Wrap around
        focusSelected(resultItems);
      }
    }

    // Handle arrow up key
    if (event.key === "ArrowUp") {
      if (resultItems.length > 0) {
        // Move to the previous item
        currentIndex =
          (currentIndex - 1 + resultItems.length) % resultItems.length; // Wrap around
        focusSelected(resultItems);
      }
    }
  });

  function focusSelected(resultItems) {
    // Clear focus from all items
    resultItems.forEach((item) => item.blur());

    // Focus the selected item only if currentIndex is valid
    if (currentIndex >= 0 && currentIndex < resultItems.length) {
      resultItems[currentIndex].focus();
      resultItems[currentIndex].scrollIntoView({ block: "nearest" });
    }
  }

  // Fetch search data and initialize Fuse.js
  fetch("../../search.json")
    .then((response) =>
      response.ok
        ? response.json()
        : Promise.reject("Error: " + response.statusText),
    )
    .then((data) => initializeFuse(data))
    .catch((error) => console.error("Fetch operation failed:", error));
});
