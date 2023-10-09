require.config({
  paths: {
    docsSearchBar:
      "https://cdn.jsdelivr.net/npm/docs-searchbar.js@2.5.0/dist/cdn/docs-searchbar.min",
  },
});

require(["docsSearchBar"], function (docsSearchBar) {
  document.body.style.overflow = "hidden !important";
  // Initialize the MeiliSearch bar with the given API key and host
  // inspect the first value of index UID as default
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

  // Assuming you have an element with id "search-icon" for the search icon

  // Function to show the magnifier icon
  function showMagnifierIcon() {
    var searchIcon = document.getElementById("search-icon");
    searchIcon.classList.remove("fa-solid", "fa-spinner", "fa-spin");
    // Assuming you are using Font Awesome for icons
  }

  // Function to show the spinner/loading icon
  function showSpinnerIcon() {
    var searchIcon = document.getElementById("search-icon");
    if (searchIcon) {
      console.log("reached");
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
