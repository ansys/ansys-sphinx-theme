require.config({
  paths: {
    fuse: "https://cdn.jsdelivr.net/npm/fuse.js@6.6.2/dist/fuse.min",
  },
});

/* IndexDD functions */

function openDB(name = "search-cache", version = 1) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(name, version);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains("indexes")) {
        db.createObjectStore("indexes");
      }
    };
  });
}

async function getFromIDB(key) {
  console.log("Getting from IDB", key);
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction("indexes", "readonly");
    const store = tx.objectStore("indexes");
    const request = store.get(key);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function saveToIDB(key, value) {
  console.log("Saving to IDB", key, value);
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction("indexes", "readwrite");
    const store = tx.objectStore("indexes");
    const request = store.put(value, key);
    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

/**
 * Initializes the search system by loading the document search index.
 */

require(["fuse"], function (Fuse) {
  let fuse;
  let searchData = [];
  let selectedObjectIDs = [];
  let selectedLibraries = [];
  const libSearchData = {};

  let selectedFilter = new Set();
  //   const SEARCH_FILE_1 = "/_static/search.json";

  function debounce(func, delay) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), delay);
    };
  }

  /**
   * Initializes the search system by loading the document search index.
   */
  async function initializeSearch() {
    try {
      const cacheKey = "main-search-index";
      let data = await getFromIDB(cacheKey);

      if (!data) {
        const response = await fetch(SEARCH_FILE);
        data = await response.json();
        await saveToIDB(cacheKey, data);
      }

      searchData = data;
      fuse = new Fuse(searchData, {
        keys: ["title", "text", "objectID"],
        ignoreLocation: true,
        threshold: 0.3,
      });

      const allLibs = Object.keys(extra_sources);
      for (const lib of allLibs) {
        const cacheKey = `lib-search-${lib}`;
        let libData = await getFromIDB(cacheKey);

        if (!libData) {
          const libPath = extra_sources[lib];
          const libJsonPath = `${libPath}/_static/search.json`;
          const res = await fetch(libJsonPath);
          libData = await res.json();
          await saveToIDB(cacheKey, libData);
        }

        libSearchData[lib] = libData; // Save in memory
      }

      setupFilterDropdown();
    } catch (err) {
      console.error("Search init failed", err);
    }
  }

  /**
   * Sets up the filter dropdown and its toggle interactions.
   */
  function setupFilterDropdown() {
    const selectButton = document.getElementById("filter-btn");
    const dropdownContainer = document.getElementById("search-sidebar");
    selectButton.addEventListener("click", () => {
      dropdownContainer.style.display =
        dropdownContainer.style.display === "none" ? "block" : "none";
    });

    const filters = [
      {
        name: "Documents",
        dropdownId: "objectid-dropdown",
        callback: showObjectIdDropdown,
      },
      {
        name: "Library",
        dropdownId: "library-dropdown",
        callback: showLibraryDropdown,
      },
    ];

    filters.forEach(({ name, dropdownId, callback }) => {
      const toggleDiv = document.createElement("div");
      toggleDiv.className = "search-page-sidebar toggle-section";
      toggleDiv.dataset.target = dropdownId;

      const icon = document.createElement("span");
      icon.className = "toggle-icon";
      icon.textContent = "▶";
      icon.style.fontSize = "12px";

      const label = document.createElement("span");
      label.className = "toggle-label";
      label.textContent = name;

      toggleDiv.append(icon, label);

      const dropdown = document.createElement("div");
      dropdown.id = dropdownId;
      dropdown.className = "dropdown-menu show";
      dropdown.style.display = "none";
      dropdown.style.marginTop = "10px";

      toggleDiv.addEventListener("click", () => {
        const isVisible = dropdown.style.display === "block";
        dropdown.style.display = isVisible ? "none" : "block";
        icon.textContent = isVisible ? "▶" : "▼";

        if (isVisible) {
          selectedFilter.delete(name);
          toggleDiv.classList.remove("active");
        } else {
          selectedFilter.add(name);
          toggleDiv.classList.add("active");
          callback?.();
        }

        performSearch();
      });

      dropdownContainer.append(toggleDiv, dropdown);
    });
  }

  function showObjectIdDropdown() {
    const dropdown = document.getElementById("objectid-dropdown");
    dropdown.innerHTML = "";

    const objectIDs = [
      ...new Set(searchData.map((item) => item.objectID)),
    ].filter(Boolean);

    objectIDs.forEach((id) => {
      const checkbox = createCheckboxItem(id, selectedObjectIDs, () => {
        renderSelectedChips();
        performSearch();
      });
      dropdown.appendChild(checkbox);
    });

    dropdown.style.display = "block";
    renderSelectedChips();
  }

  function showLibraryDropdown() {
    const dropdown = document.getElementById("library-dropdown");
    dropdown.innerHTML = "";

    for (const lib in extra_sources) {
      const checkbox = createCheckboxItem(lib, selectedLibraries, () => {
        renderSelectedChips();
        performSearch();
      });
      dropdown.appendChild(checkbox);
    }

    dropdown.style.display = "block";
    renderSelectedChips();
  }

  function createCheckboxItem(value, selectedArray, onchnage) {
    const div = document.createElement("div");
    div.className = "checkbox-item";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = value;
    checkbox.style.margin = "8px";
    checkbox.checked = selectedArray.includes(value);
    checkbox.onchange = (e) => {
      if (e.target.checked) {
        selectedArray.push(value);
      } else {
        const index = selectedArray.indexOf(value);
        if (index > -1) {
          selectedArray.splice(index, 1);
        }
      }
      onchnage();
    };

    const label = document.createElement("label");
    label.textContent = value;
    div.appendChild(checkbox);
    div.appendChild(label);
    return div;
  }

  /**
   * Renders chips for selected filters and binds remove logic.
   */
  function renderSelectedChips() {
    const container = document.getElementById("selected-chips");
    container.innerHTML = "";

    const renderChip = (value, type, selectedArray) => {
      const chip = document.createElement("div");
      chip.className = "chip";
      chip.textContent = `${value} (${type})`;

      const removeBtn = document.createElement("button");
      removeBtn.className = "remove-btn";
      removeBtn.innerHTML = "&times;";
      removeBtn.onclick = () => {
        const index = selectedArray.indexOf(value);
        if (index !== -1) selectedArray.splice(index, 1);
        renderSelectedChips();
        if (type === "Documents") showObjectIdDropdown();
        if (type === "Library") showLibraryDropdown();
        performSearch();
      };

      chip.appendChild(removeBtn);
      container.appendChild(chip);
    };

    selectedObjectIDs.forEach((id) =>
      renderChip(id, "Documents", selectedObjectIDs),
    );
    selectedLibraries.forEach((lib) =>
      renderChip(lib, "Library", selectedLibraries),
    );
  }

  async function performSearch() {
    const query = document.getElementById("search-input").value.trim();
    if (!fuse) return;

    const resultsContainer = document.getElementById("search-results");
    resultsContainer.innerHTML = "Searching...";

    let docResults = [];
    let libResults = [];

    const resultLimit = getSelectedResultLimit();

    // === Search in internal documents ===
    if (selectedFilter.size === 0 || selectedFilter.has("Documents")) {
      docResults = fuse
        .search(query, { limit: resultLimit })
        .map((r) => r.item);

      if (selectedObjectIDs.length > 0) {
        docResults = docResults.filter((item) =>
          selectedObjectIDs.includes(item.objectID),
        );
      }
    }

    for (const lib of selectedLibraries) {
      const libBaseUrl = extra_sources[lib];
      const cacheKey = `lib-search-${lib}`;

      try {
        const data = await getFromIDB(cacheKey); // Use cached data

        if (data) {
          const enrichedEntries = data.map((entry) => ({
            title: entry.title,
            text: entry.text,
            section: entry.section, // if used in keys
            link: `${libBaseUrl}${entry.href}`,
            source: lib,
          }));

          // Create a separate Fuse instance for this library
          const libFuse = new Fuse(enrichedEntries, {
            keys: ["title", "text", "section"],
            threshold: 0.3,
            includeScore: false,
          });

          // Search and add to results (append instead of overwrite)
          const results = libFuse
            .search(query, { limit: resultLimit })
            .map((r) => r.item);

          libResults.push(...results);
        }
      } catch (err) {
        console.error(`Error accessing cache for ${lib}:`, err);
      }
    }

    // === Merge and show results ===
    const mergedResults = [...docResults, ...libResults];

    if (mergedResults.length === 0) {
      resultsContainer.innerHTML = "<p>No results found.</p>";
      return;
    }

    const highlightedResults = highlightResults(mergedResults, query);
    displayResults(highlightedResults);
  }

  function highlightResults(results, query) {
    const regex = new RegExp(`(${query})`, "gi");

    return results
      .map((result) => {
        const matchIndex = result.text
          .toLowerCase()
          .indexOf(query.toLowerCase());
        if (matchIndex === -1) return null;

        const contextLength = 100;
        const start = Math.max(0, matchIndex - contextLength);
        const end = Math.min(result.text.length, matchIndex + contextLength);
        let snippet = result.text.slice(start, end);

        if (start > 0) snippet = "…" + snippet;
        if (end < result.text.length) snippet += "…";

        return {
          ...result,
          title: result.title.replace(
            regex,
            `<span class="highlight">$1</span>`,
          ),
          text: snippet.replace(regex, `<span class="highlight">$1</span>`),
        };
      })
      .filter(Boolean);
  }

  /**
   * Displays the final search results on the UI.
   */
  function displayResults(results) {
    const container = document.getElementById("search-results");
    container.innerHTML = "";

    results.forEach((item) => {
      const div = document.createElement("div");
      div.className = "result-item";

      const title = document.createElement("a");
      title.href = item.href || item.link || "#";
      title.target = "_blank";
      title.innerHTML = item.title || "Untitled";
      title.className = "result-title";

      div.appendChild(title);

      if (item.text) {
        const text = document.createElement("p");
        text.innerHTML = item.text;
        text.className = "result-text";
        div.appendChild(text);
      }

      if (item.source) {
        const source = document.createElement("p");
        source.className = "checkmark";
        source.textContent = `Source: ${item.source}`;
        div.appendChild(source);
      }

      container.appendChild(div);
    });
  }

  function getSelectedResultLimit() {
    const select = document.getElementById("result-limit");
    return parseInt(select.value, 10) || 10; // default to 10 if not set
  }

  const handleSearchInput = debounce(
    () => {
      const query = document.getElementById("search-input").value.trim();
      console.log("Search query:", query);
      if (query.length > 0) {
        performSearch();
      }
    },
    parseInt(SEARCH_OPTIONS.delay) || 300,
  );

  document
    .getElementById("search-input")
    .addEventListener("input", handleSearchInput);
  document
    .getElementById("result-limit")
    .addEventListener("change", performSearch);

  initializeSearch();

  // cut the query from the URL of the page ?q=
  const urlParams = new URLSearchParams(window.location.search);
  const query = urlParams.get("q");

  if (query) {
    const inputElement = document.getElementById("search-input");
    inputElement.value = query;

    handleSearchInput();
  }
});
