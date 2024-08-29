# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module to fetch raw files from GitHub."""

import os
import re
from typing import Optional

import httpx
from sphinx.util import logging

logger = logging.getLogger(__name__)

URL_WITH_TAG = re.compile(r"^(.*?)(@)(.*)$")
"""Regular expression to match a URL with a tag."""


class GitHubFile:
    """Models a file in a GitHub repository."""

    def __init__(self, url: str, access_token: Optional[str] = None):
        """Initialize an instance.

        Parameters
        ----------
        url : str
            The URL of the file in the GitHub repository.
        access_token : str, optional
            The GitHub access token, by default None.
        """
        if not self.is_valid_url(url):
            raise ValueError(
                f"URL {url} is not valid. Please, provide a valid URL following \
                the pattern <org>/<repo>/<doc-snippet-dir>/...@<ref>"
            )
        self._url = url

        self.access_token = access_token or os.getenv("GITHUB_ACCESS_TOKEN")

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if the given URL is a valid GitHub URL.

        Parameters
        ----------
        url : str
            The URL to check.

        Returns
        -------
        bool
            True if the URL is a valid GitHub URL, False otherwise.
        """
        return bool(URL_WITH_TAG.match(url))

    @property
    def url(self) -> str:
        """URL of the file in the repository."""
        return self._url

    @property
    def url_without_tag(self) -> str:
        """URL of the file in the repository without the tag."""
        return self.url.split("@")[0]

    @property
    def ref(self) -> str:
        """Git reference (branch, tag, or commit) of the file."""
        return self.url.split("@")[-1]

    @property
    def owner(self) -> str:
        """Owner name of the repository."""
        return self.url.split("/")[0]

    @property
    def repo(self) -> str:
        """Repository name."""
        return self.url.split("/")[1]

    @property
    def path(self) -> str:
        """Path of the file in the repository."""
        return "/".join(self.url_without_tag.split("/")[2:])

    async def fetch_content(self) -> str:
        """Fetch content of the file as a string."""
        headers = {"Authorization": f"token {self.access_token}"} if self.access_token else None
        raw_url = (
            f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.ref}/{self.path}"
        )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(raw_url, headers=headers)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as exc:
                logger.error(
                    f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}"
                )
            except Exception as exc:
                logger.error(f"An error occurred: {exc}")
