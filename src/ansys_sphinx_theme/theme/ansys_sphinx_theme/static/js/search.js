// ==============================
// Fuse.js Search Integration
// ==============================

// Constants
const MAIN_PAGE_CONTENT = document.querySelector(".bd-main");
const FUSE_VERSION = "6.4.6";
let SEARCH_BAR,
  RESULTS,
  SEARCH_INPUT,
  CURRENT_INDEX = -1;
let fuse;

// Load Fuse.js from CDN
require.config({
  paths: {
    fuse: `https://cdn.jsdelivr.net/npm/fuse.js@${FUSE_VERSION}/dist/fuse.min`,
  },
});

require(["fuse"], function (Fuse) {
  /**
   * Debounce function to limit how often a function is called.
   * @param {Function} func - Function to debounce.
   * @param {number} delay - Delay in milliseconds.
   * @returns {Function}
   */
  const debounce = (func, delay) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), delay);
    };
  };

  /**
   * Truncate a long text string to a specified length.
   * @param {string} text - Text to truncate.
   * @param {number} maxLength - Maximum allowed length.
   * @returns {string}
   */
  const truncateTextPreview = (text, maxLength = 200) =>
    text.length <= maxLength ? text : `${text.slice(0, maxLength)}...`;

  /**
   * Return full path based on Sphinx's data-content_root.
   * @param {string} targetFile - Path to file.
   * @returns {string}
   */
  const getDynamicPath = (targetFile) => {
    const contentRoot =
      document.documentElement.getAttribute("data-content_root");
    return `${contentRoot}${targetFile}`;
  };

  /**
   * Navigate to a given URL.
   * @param {string} href - Target href.
   */
  const navigateToHref = (href) => {
    window.location.href = getDynamicPath(href);
  };

  /**
   * Expand the search input UI.
   */
  function expandSearchInput() {
    RESULTS.style.display = "flex";
    SEARCH_INPUT.classList.add("expanded");
    MAIN_PAGE_CONTENT.classList.add("blurred");
    SEARCH_INPUT.focus();

    // Fix overlapping on mobile view
    const modalSidebar = document.querySelector(
      "#pst-primary-sidebar-modal > div.sidebar-primary-items__start.sidebar-primary__section",
    );
    if (modalSidebar) {
      modalSidebar.style.opacity = "0.1";
    }
  }

  /**
   * Collapse and reset the search UI.
   */
  function collapseSearchInput() {
    RESULTS.style.display = "none";
    SEARCH_INPUT.classList.remove("expanded");
    SEARCH_INPUT.value = "";
    MAIN_PAGE_CONTENT.classList.remove("blurred");
    CURRENT_INDEX = -1;

    const modalSidebar = document.querySelector(
      "#pst-primary-sidebar-modal > div.sidebar-primary-items__start.sidebar-primary__section",
    );
    if (modalSidebar) {
      modalSidebar.style.opacity = "1";
    }
  }

  /**
   * Show banner when no results found.
   */
  function noResultsFoundBanner() {
    RESULTS.innerHTML = "";
    RESULTS.style.display = "flex";
    const banner = document.createElement("div");
    banner.className = "warning-banner";
    banner.textContent = "No results found. Press Enter for extended search.";
    banner.style.fontStyle = "italic";
    RESULTS.appendChild(banner);
  }

  /**
   * Show a temporary searching indicator.
   */
  function searchingForResultsBanner() {
    RESULTS.innerHTML = "";
    RESULTS.style.display = "flex";
    const banner = document.createElement("div");
    banner.className = "searching-banner";
    banner.textContent = "Searching...";
    banner.style.fontStyle = "italic";
    RESULTS.appendChild(banner);
  }

  /**
   * Display search results from Fuse.
   * @param {Array} results - Fuse search result objects.
   */
  function displayResults(results) {
    RESULTS.innerHTML = "";
    if (results.length === 0) return noResultsFoundBanner();

    const fragment = document.createDocumentFragment();
    results.forEach(({ item: { title, text, href } }) => {
      const resultItem = document.createElement("div");
      resultItem.className = "result-item";
      resultItem.dataset.href = href;
      resultItem.addEventListener("click", () => navigateToHref(href));

      const resultTitle = document.createElement("div");
      resultTitle.className = "result-title";
      resultTitle.textContent = title;

      const resultText = document.createElement("div");
      resultText.className = "result-text";
      resultText.textContent = truncateTextPreview(text);

      resultItem.appendChild(resultTitle);
      resultItem.appendChild(resultText);
      fragment.appendChild(resultItem);
    });

    RESULTS.appendChild(fragment);
    RESULTS.style.display = "flex";
  }

  /**
   * Highlight the currently selected item.
   * @param {NodeList} resultsItems - List of result items.
   */
  function focusSelected(resultsItems) {
    if (CURRENT_INDEX >= 0 && CURRENT_INDEX < resultsItems.length) {
      resultsItems.forEach((item) => item.classList.remove("selected"));
      const currentItem = resultsItems[CURRENT_INDEX];
      currentItem.classList.add("selected");
      currentItem.focus();
      currentItem.scrollIntoView({ block: "nearest" });
    }
  }

  /**
   * Handle search query input with debounce.
   */
  const handleSearchInput = debounce(
    () => {
      const query = SEARCH_INPUT.value.trim();
      if (!query) return (RESULTS.style.display = "none");

      const searchResults = fuse.search(query, {
        limit: parseInt(SEARCH_OPTIONS.limit),
      });
      displayResults(searchResults);
    },
    parseInt(SEARCH_OPTIONS.delay) || 300,
  );

  /**
   * Handle keyboard navigation inside search input.
   * @param {KeyboardEvent} event
   */
  function handleKeyDownSearchInput(event) {
    const resultItems = RESULTS.querySelectorAll(".result-item");

    switch (event.key) {
      case "Tab":
        event.preventDefault();
        break;
      case "Escape":
        collapseSearchInput();
        break;
      case "Enter":
        event.preventDefault();
        const indexToNavigate =
          CURRENT_INDEX >= 0 && CURRENT_INDEX < resultItems.length
            ? CURRENT_INDEX
            : resultItems.length > 0
              ? 0
              : -1;
        if (indexToNavigate >= 0) {
          const href = resultItems[indexToNavigate].dataset.href;
          navigateToHref(href);
        }
        break;
      case "ArrowDown":
        if (resultItems.length > 0) {
          CURRENT_INDEX = (CURRENT_INDEX + 1) % resultItems.length;
          focusSelected(resultItems);
        }
        break;
      case "ArrowUp":
        if (resultItems.length > 0) {
          CURRENT_INDEX =
            (CURRENT_INDEX - 1 + resultItems.length) % resultItems.length;
          focusSelected(resultItems);
        }
        break;
      default:
        if (
          document.documentElement.getAttribute("data-fuse_active") === "true"
        ) {
          searchingForResultsBanner();
        } else {
          console.error("[AST]: Fuse is not active yet.");
          RESULTS.style.display = "none";
        }
        handleSearchInput();
    }
  }

  /**
   * Initialize and bind search elements.
   */
  function setupSearchElements() {
    if (window.innerWidth < 1200) {
      SEARCH_BAR = document.querySelector(
        "div.sidebar-header-items__end #search-bar",
      );
      RESULTS = document.querySelector(
        "div.sidebar-header-items__end .static-search-results",
      );
    } else {
      SEARCH_BAR = document.getElementById("search-bar");
      RESULTS = document.querySelector(".static-search-results");
    }

    if (!SEARCH_BAR) {
      console.warn("SEARCH_BAR not found for current view.");
      return;
    }

    SEARCH_INPUT = SEARCH_BAR.querySelector(".bd-search input.form-control");
    if (SEARCH_INPUT) {
      SEARCH_INPUT.addEventListener("click", expandSearchInput);
      SEARCH_INPUT.addEventListener("keydown", handleKeyDownSearchInput);
    }
  }

  // Global event listeners
  function handleGlobalKeyDown(event) {
    if (event.key === "Escape") collapseSearchInput();
    else if (event.key === "k" && event.ctrlKey) expandSearchInput();
  }

  function handleGlobalClick(event) {
    if (!RESULTS.contains(event.target) && event.target !== SEARCH_INPUT) {
      collapseSearchInput();
    }
  }

  // Initialize search system
  setupSearchElements();
  window.addEventListener("resize", debounce(setupSearchElements, 250));
  document.addEventListener("keydown", handleGlobalKeyDown);
  document.addEventListener("click", handleGlobalClick);

  fetch(SEARCH_FILE)
    .then((response) => {
      if (!response.ok)
        throw new Error(`[AST]: HTTPS error ${response.statusText}`);
      return response.json();
    })
    .then((SEARCH_DATA) => initializeFuse(SEARCH_DATA, SEARCH_OPTIONS))
    .catch((error) =>
      console.error(`[AST]: Cannot fetch ${SEARCH_FILE}`, error.message),
    );

  /**
   * Initialize Fuse with the given data and options.
   * @param {Array} data - Search index data.
   * @param {Object} options - Fuse.js configuration options.
   */
  function initializeFuse(data, options) {
    fuse = new Fuse(data, options);
    document.documentElement.setAttribute("data-fuse_active", "true");
  }
});
