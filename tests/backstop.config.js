// The scenario URLs in backstop.json are paths; BACKSTOP_BASE_URL says where the docs are served.
const config = require("./backstop.json");

const baseUrl = process.env.BACKSTOP_BASE_URL?.replace(/\/$/, "");
if (!baseUrl) {
  throw new Error(
    "Set BACKSTOP_BASE_URL to the served documentation, for example " +
      "BACKSTOP_BASE_URL=http://localhost:<port> npm run reference-tests",
  );
}

for (const scenario of config.scenarios) {
  scenario.url = `${baseUrl}${scenario.url}`;
}

module.exports = config;
