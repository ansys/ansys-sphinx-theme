# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
