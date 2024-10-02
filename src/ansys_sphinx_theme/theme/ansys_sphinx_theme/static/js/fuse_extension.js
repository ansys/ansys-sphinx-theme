const SEARCH_BAR = document.getElementById("search-bar");
const SEARCH_INPUT = SEARCH_BAR.querySelector(".bd-search input");
resultsContainer = document.getElementById("results");
const content = document.querySelector(".bd-main");

// Function to expand the search bar and display results
function expandSearchBox() {
  searchInput.classList.add("expanded");
  content.classList.add("blurred");
  searchInput.focus();

  if (searchInput.value.trim().length >= parseInt(min_chars_for_search)) {
    resultsContainer.style.display = "flex";
  }
}

// Expand search box on click
searchInput.addEventListener("click", expandSearchBox);

// Keydown event handler using switch
document.addEventListener("keydown", function (event) {
  switch (event.key) {
    case "k":
      if (event.ctrlKey) {
        expandSearchBox();
      }
      break;
    case "Escape":
      resultsContainer.style.display = "none";
      searchInput.classList.remove("expanded");
      content.classList.remove("blurred");
      break;
  }
});

// Hide the results and collapse the search box on outside click
document.addEventListener("click", function (event) {
  if (
    !resultsContainer.contains(event.target) &&
    event.target !== searchInput
  ) {
    resultsContainer.style.display = "none";
    searchInput.classList.remove("expanded");
    content.classList.remove("blurred");
  }
});
