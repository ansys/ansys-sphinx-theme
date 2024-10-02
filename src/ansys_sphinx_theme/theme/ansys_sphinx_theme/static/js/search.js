const SEARCH_BAR = document.getElementById("search-bar");
const SEARCH_INPUT = SEARCH_BAR.querySelector(".bd-search input");
const RESULTS_CONTAINER = document.getElementById("results");
const MAIN_PAGE_CONTENT = document.querySelector(".bd-main");


const FUSE_VERSION = "6.4.6";

require.config({
  paths: {
    fuse: `https://cdn.jsdelivr.net/npm/fuse.js@${FUSE_VERSION}/dist/fuse.min`,
  },
});

require(["fuse"], function (Fuse) {

    let fuse;
    let results = [];

    // Initiali Fuse when the data is fetched
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
        RESULTS_CONTAINER.style.display = "none";
        SEARCH_INPUT.classList.remove("expanded");
        SEARCH_INPUT.value = "";
        MAIN_PAGE_CONTENT.classList.remove("blurred");
    }

    // Display search results
    function displayResults(results) {
        // the RESULTS_CONTAINER is a div element
        RESULTS_CONTAINER.style.display = "block";
        results.forEach((result) => {
            const { title, text, href } = result.item;
        });
    }

    // Handle search input
    function handleSearchInput() {
        const query = SEARCH_INPUT.value.trim();
        if (query.length > 0) {
            const results = fuse.search(query);
            if (results.length > 0) {
                displayResults(results);
            }
        }
    }

    // Handle keydown event for the search input
    function handleKeyDownSearchInput(event) {

        switch (event.key) {
            case "Tab":
                event.preventDefault();
                break;

            case "Escape":
                collapseSearchInput();

            case "Enter":
                break;

            default:
                handleSearchInput();

        }
    }

    // Add event listeners
    SEARCH_INPUT.addEventListener("click", expandSearchInput);
    SEARCH_INPUT.addEventListener("keydown", handleKeyDownSearchInput);

    // Search file and options are passed via "ast-search-button.html"
    fetch(SEARCH_FILE)
      .then((response) =>
        response.ok
          ? response.json()
          : Promise.reject("Error from search: " + response.statusText),
      )
    .then((SEARCH_DATA) => initializeFuse(SEARCH_DATA, SEARCH_OPTIONS))
      .catch((error) => console.error("Fetch operation failed:", error));

});
