const searchBar = document.getElementById("search-bar");
const searchBarBox = searchBar.querySelector(".bd-search input");
resultsContainer = document.getElementById("results");

// Expand search box on click
searchBarBox.addEventListener("click", function () {
  searchBarBox.classList.add("expanded");
  searchBarBox.focus();

  if (searchBarBox.value.trim().length >= parseInt(min_chars_for_search)) {
    resultsContainer.style.display = "flex";
  }
});

// Expand the search box on pressing ctrl + k
document.addEventListener("keydown", function (event) {
  if (event.ctrlKey && event.key === "k") {
    searchBarBox.classList.add("expanded");
    searchBarBox.focus();

    if (searchBarBox.value.trim().length >= parseInt(min_chars_for_search)) {
      resultsContainer.style.display = "flex";
    }
  }
});

// Hide the results and collapse the search box on outside click
document.addEventListener("click", function (event) {
  if (
    !resultsContainer.contains(event.target) &&
    event.target !== searchBarBox
  ) {
    resultsContainer.style.display = "none";
    searchBarBox.classList.remove("expanded");
  }
});

// Close the result container on pressing the escape key
document.addEventListener("keydown", function (event) {
  if (event.key === "Escape") {
    resultsContainer.style.display = "none";
    searchBarBox.classList.remove("expanded");
  }
});
