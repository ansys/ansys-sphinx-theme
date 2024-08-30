require.config({
  paths: {
    Fuse: "https://cdn.jsdelivr.net/npm/fuse.js@6.4.6/dist/fuse.min",
  },
});

require(["Fuse"], function (Fuse) {
  // Function to initialize Fuse.js and set up search functionality
  function initializeFuse(data) {
    // Fuse.js options
    const fuseOptions = {
      keys: ["title", "text"],
      includeScore: true, // Optional: includes the score in the search result
    };

    // Create a Fuse instance
    const fuse = new Fuse(data, fuseOptions);

    // Function to perform search and update UI
    function performSearch(query) {
      const results = fuse.search(query);

      // Debugging: Log results to the console
      console.log("Search Results:", results);

      // Update UI with search results
      const resultsContainer = document.getElementById("results");
      resultsContainer.innerHTML = "";

      results.forEach((result) => {
        const item = document.createElement("div");
        item.className = "result-item";
        const { title, text } = result.item;

        // Get a snippet of text around the matched terms
        const snippet = getSnippet(text, query);

        item.innerHTML =
          `<div class="result-title">${highlightTerms(title, query)}</div>` +
          `<div class="result-text">${snippet}</div>`;
        resultsContainer.appendChild(item);
      });
    }

    // Function to highlight multiple search terms in text
    function highlightTerms(text, query) {
      if (!query.trim()) return text;

      // Split the query into individual words or phrases
      const terms = query.split(/\s+/); // Split by spaces

      // Escape special characters and create regex for each term
      const regex = new RegExp(
        `(${terms.map((term) => term.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&")).join("|")})`,
        "gi",
      );

      // Replace matched text with highlighted version
      return text.replace(regex, '<span class="highlight">$1</span>');
    }

    // Function to get a snippet of text around the matched terms
    function getSnippet(text, query) {
      if (!query.trim()) return text;

      const terms = query.split(/\s+/);
      const regex = new RegExp(
        `(${terms.map((term) => term.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&")).join("|")})`,
        "gi",
      );

      // Find the first match position
      const match = regex.exec(text);
      if (!match) return text;

      // Get the index of the first match
      const startIndex = Math.max(0, match.index - 50); // Show some text before the match
      const endIndex = Math.min(
        text.length,
        match.index + match[0].length + 50,
      ); // Show some text after the match

      // Extract the snippet and highlight terms
      const snippet = text.slice(startIndex, endIndex);
      return highlightTerms(snippet, query);
    }

    // Set up the search box event listener
    const searchBox = document.getElementById("searchBox");
    searchBox.addEventListener("input", function () {
      const query = searchBox.value.trim();
      performSearch(query);
    });
  }

  // Fetch data from search.json and initialize Fuse.js
  fetch("http://127.0.0.1:8002/search.json")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok " + response.statusText);
      }
      return response.json();
    })
    .then((data) => {
      initializeFuse(data);
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
});
