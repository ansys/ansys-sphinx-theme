require.config({
  paths: {
    docsSearchBar:
      "https://cdn.jsdelivr.net/npm/docs-searchbar.js@2.5.0/dist/cdn/docs-searchbar.min",
  },
});

require(["docsSearchBar"], function (docsSearchBar) {
  document.body.style.overflow = "hidden !important";
  // Initialize the MeiliSearch bar with the given API key and host
  var theSearchBar = docsSearchBar({
    hostUrl: HOST_URL,
    apiKey: API_KEY,
    indexUid: indexUid,
    inputSelector: "#search-bar-input",
    debug: true, // Set debug to true if you want to inspect the dropdown
    meilisearchOptions: {
      limit: 10,
    },
  });

  // Function to show the magnifier icon
  function showMagnifierIcon() {
    var searchIcon = document.getElementById("search-icon");
    searchIcon.classList.remove("fa-solid", "fa-spinner", "fa-spin");
  }

  // Function to show the spinner icon
  function showSpinnerIcon() {
    var searchIcon = document.getElementById("search-icon");
    if (searchIcon) {
      searchIcon.classList = "fa-solid fa-spinner fa-spin";
    }
  }

  document
    .getElementById("search-bar-input")
    .addEventListener("input", function () {
      // Show the spinner icon when the user starts typing
      const suggestions = document.querySelectorAll(".dsb-suggestion");
      const noSuggestions = suggestions.length === 0;

      if (noSuggestions) {
        // Show the spinner icon only when there are no suggestions
        showSpinnerIcon();
      } else {
        // Hide the spinner icon when there are suggestions
        showMagnifierIcon();
      }
    });
  // Listen for changes in the dropdown selector and update the index uid and suggestion accordingly
  document
    .getElementById("indexUidSelector")
    .addEventListener("change", function () {
      theSearchBar.indexUid = this.value;
      theSearchBar.suggestionIndexUid = this.value;
      theSearchBar.autocomplete.autocomplete.setVal("");
    });
});
