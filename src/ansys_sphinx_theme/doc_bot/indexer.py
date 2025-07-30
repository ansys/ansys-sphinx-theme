# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Indexing for the documentation bot."""

import os
from pathlib import Path

from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.readers.github import GithubRepositoryReader
from llama_index.readers.github.repository.github_client import GithubClient

API_KEY = os.getenv("API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
API_VERSION = os.getenv("API_VERSION")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LLM_MODEL = os.getenv("MODEL_NAME")
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL")
LLM_DEPLOYMENT_NAME = os.getenv("LLM_DEPLOYMENT_NAME")
EMBEDDINGS_DEPLOYMENT_NAME = os.getenv("EMBEDDINGS_DEPLOYMENT_NAME")

THIS_DIR = Path(__file__).parent
INDEX_STORAGE = THIS_DIR / "index"


def initialise_library(sphinx_app):
    """Initialize the library with sphinx app."""
    theme_options = sphinx_app.config.html_theme_options.get("chatbot", {})
    github_repo = theme_options.get("github_repo", "pyansys-geometry")
    index_storage = theme_options.get("index", f"{INDEX_STORAGE}/{github_repo}")
    project_name = theme_options.get("project_name", "PyAnsys Geometry")
    return index_storage, project_name, github_repo


def create_new_index(index_storage, project_name, github_repo):
    """Create a new index for the documentation bot."""
    index_path = Path(index_storage)
    print(f"Creating new index at {index_storage} for project {project_name}...")
    print(index_path)
    if not index_path.exists():
        index_path.mkdir(parents=True, exist_ok=True)

    index_path = Path(index_storage).resolve()
    print(f"[DEBUG] Resolved path: {index_path}")
    print(f"[DEBUG] Directory exists: {index_path.exists()}")

    # Try with rglob in case files are nested (e.g. vector_store/vector_store.json)
    json_files = list(index_path.rglob("*.json"))
    if not json_files:
        print("[DEBUG] No JSON files found with rglob.")
    else:
        for file in json_files:
            print(f"[FOUND] {file}")

    files = [f for f in index_path.iterdir() if f.is_file() and f.suffix == ".json"]

    if index_path.exists() and files:
        print(f"[DEBUG] Found JSON files: {files}")
        return
    else:
        print("[DEBUG] No JSON files found.")
    try:
        Settings.llm = AzureOpenAI(
            model=LLM_MODEL,
            deployment_name=LLM_DEPLOYMENT_NAME,
            api_key=API_KEY,
            azure_endpoint=AZURE_ENDPOINT,
            api_version=API_VERSION,
        )
        Settings.embed_model = AzureOpenAIEmbedding(
            model=EMBEDDINGS_MODEL,
            deployment_name=EMBEDDINGS_DEPLOYMENT_NAME,
            api_key=API_KEY,
            azure_endpoint=AZURE_ENDPOINT,
            api_version=API_VERSION,
        )
    except Exception as e:
        print(f"[LLM Setup Error] {e}")

    try:
        client = GithubClient(github_token=GITHUB_TOKEN, verbose=True)
        reader = GithubRepositoryReader(owner="ansys", repo=github_repo, github_client=client)
        documents = reader.load_data(branch="main")
        print(f"[DEBUG] Loaded {len(documents)} documents from GitHub repository {github_repo}")
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=str(index_path))
        print(f"[DEBUG] Index created and persisted at {index_path}")

    except Exception as e:
        raise Exception(f"Index creation failed: {e}")


# === App Entry ===
def pyansys_chat_navigator(sphinx_app):
    """Initialize the PyAnsys Chat Navigator."""
    index_storage, project_name, github_repo = initialise_library(sphinx_app)
    create_new_index(index_storage, project_name, github_repo)
