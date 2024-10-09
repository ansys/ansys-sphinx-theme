const SEARCH_BAR = document.getElementById("search-bar");
const SEARCH_INPUT = SEARCH_BAR.querySelector(".bd-search input");
const RESULTS = document.getElementById("search-results");
const MAIN_PAGE_CONTENT = document.querySelector(".bd-main");
let CURRENT_INDEX = -1;

const FUSE_VERSION = "6.4.6";

require.config({
  paths: {
    fuse: `https://cdn.jsdelivr.net/npm/fuse.js@${FUSE_VERSION}/dist/fuse.min`,
  },
});

require(["fuse"], function (Fuse) {
  // Declare global variables
  let fuse;

  // Debounce function to limit the rate of function calls
  function debounce(func, delay) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), delay);
    };
  }

  // Initialize Fuse when the data is fetched
  function initializeFuse(data, options) {
    fuse = new Fuse(data, options);
  }

  // Expand the search bar input
  function expandSearchInput() {
    SEARCH_INPUT.classList.add("expanded");
    MAIN_PAGE_CONTENT.classList.add("blurred");
    SEARCH_INPUT.focus();
  }

  // Collapse the search bar input and hide any results
  function collapseSearchInput() {
    RESULTS.style.display = "none";
    SEARCH_INPUT.classList.remove("expanded");
    SEARCH_INPUT.value = "";
    MAIN_PAGE_CONTENT.classList.remove("blurred");
  }

  // Display search results
  function displayResults(results) {
    if (!RESULTS) {
      console.error("RESULTS element is not defined.");
      return;
    }

    if (results.length === 0) {
      noResultsFoundBanner();
      RESULTS.style.display = "none";
      return;
    }

    RESULTS.style.display = "flex";
    RESULTS.innerHTML = "";

    const fragment = document.createDocumentFragment();

    results.forEach((result) => {
      const { title, text, href } = result.item;

      const resultItem = document.createElement("div");
      resultItem.className = "result-item";
      resultItem.dataset.href = href;

      const resultTitle = document.createElement("div");
      resultTitle.className = "result-title";
      resultTitle.textContent = title;
      resultItem.appendChild(resultTitle);

      const resultText = document.createElement("div");
      resultText.className = "result-text";
      resultText.textContent = text;
      resultItem.appendChild(resultText);

      fragment.appendChild(resultItem);
    });

    RESULTS.appendChild(fragment);
  }

  // Handle search for results and no results found divs
  function noResultsFoundBanner() {
    RESULTS.innerHTML = "";
    RESULTS.style.display = "flex";
    const warningBanner = document.createElement("div");
    warningBanner.className = "warning-banner";
    warningBanner.textContent = "No results found.";
    warningBanner.style.display = "block";
    // show in italic
    warningBanner.style.fontStyle = "italic";
    RESULTS.appendChild(warningBanner);
  }

  function searchingForResultsBanner() {
    RESULTS.innerHTML = "";
    RESULTS.style.display = "flex";
    const searchingBanner = document.createElement("div");
    searchingBanner.className = "searching-banner";
    searchingBanner.textContent = "Searching...";
    searchingBanner.style.display = "block";
    console.log("Searching...");
    // show in italic
    searchingBanner.style.fontStyle = "italic";
    RESULTS.appendChild(searchingBanner);
  }

  // Handle search input
  const handleSearchInput = debounce(
    () => {
      const query = SEARCH_INPUT.value.trim();
      searchingForResultsBanner();
      if (query.length > 0) {
        const searchResults = fuse.search(query, {
          limit: parseInt(SEARCH_OPTIONS.limit),
        });
        searchingForResultsBanner();
        if (searchResults.length === 0) {
          noResultsFoundBanner();
        } else {
          searchingForResultsBanner();
          displayResults(searchResults);
        }
      } else {
        RESULTS.style.display = "none";
      }
    },
    parseInt(SEARCH_OPTIONS.delay) || 0,
  ); // Adjust the delay as necessary

  // Handle keydown event for the search input
  function handleKeyDownSearchInput(event) {
    const resultItems = RESULTS.querySelectorAll(".result-item");

    switch (event.key) {
      case "Tab":
        event.preventDefault();
        break;

      case "Escape":
        collapseSearchInput();
        break; // Added break to avoid fall-through

      case "Enter":
        // Optionally handle Enter key here
        break;

      case "ArrowDown":
        if (resultItems.length > 0) {
          CURRENT_INDEX = (CURRENT_INDEX + 1) % resultItems.length; // Move down
          focusSelected(resultItems);
        }
        break;

      case "ArrowUp":
        if (resultItems.length > 0) {
          CURRENT_INDEX =
            (CURRENT_INDEX - 1 + resultItems.length) % resultItems.length; // Move up
          focusSelected(resultItems);
        }
        break;

      default:
        handleSearchInput();
    }
  }

  // Handle keydown event globally
  function handleGlobalKeyDown(event) {
    switch (event.key) {
      case "k":
        if (event.ctrlKey) {
          expandSearchInput();
        }
        break;

      case "Escape":
        collapseSearchInput();
        break;
    }
  }

  function focusSelected(resultsItems) {
    if (CURRENT_INDEX >= 0 && CURRENT_INDEX < resultsItems.length) {
      resultsItems.forEach((item) => item.classList.remove("selected"));
      const currentItem = resultsItems[CURRENT_INDEX];
      currentItem.classList.add("selected");
      currentItem.focus();
      currentItem.scrollIntoView({ block: "nearest" });
    }
  }

  // Handle click event globally
  function handleGlobalClick(event) {
    if (!RESULTS.contains(event.target) && event.target !== SEARCH_INPUT) {
      collapseSearchInput();
    }
  }

  // Add event listeners
  SEARCH_INPUT.addEventListener("click", expandSearchInput);
  SEARCH_INPUT.addEventListener("keydown", handleKeyDownSearchInput);
  document.addEventListener("keydown", handleGlobalKeyDown);
  document.addEventListener("click", handleGlobalClick);

  // Fetch search data and initialize Fuse
  fetch(SEARCH_FILE)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`[AST]: HTTPS error ${response.statusText}`);
      }
      return response.json();
    })
    .then((SEARCH_DATA) => initializeFuse(SEARCH_DATA, SEARCH_OPTIONS))
    .catch((error) =>
      console.error(`[AST]: Can not fetch ${SEARCH_FILE}`, error.message),
    );
});
