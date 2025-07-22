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

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import threading
import time

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
from llama_index.core import PromptTemplate, Settings, VectorStoreIndex, get_response_synthesizer
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.readers.github import GithubRepositoryReader
from llama_index.readers.github.repository.github_client import GithubClient

from ansys_sphinx_theme.doc_navigator.prompts import default_prompts

# === Configuration ===
API_KEY = os.getenv("API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
API_VERSION = os.getenv("API_VERSION")
INDEX_STORAGE = None  # Will be set from theme options
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# === Flask Setup ===
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# === Global State ===
chat_engine = None
retriever = None
chat_sessions = {}

initialization_status = {
    "initialized": False,
    "loading": False,
    "error": None,
    "status": "Not initialized",
    "optimized": True,
}

# === Utility Functions ===


def initialise_library(sphinx_app):
    """Initialize the library with sphinx app."""
    print("here=============")
    theme_options = sphinx_app.config.html_theme_options
    index_storage = theme_options.get("index_storage", "index_storage_pyansys")
    project_name = theme_options.get("project_name", "PyAnsys Geometry")
    github_repo = theme_options.get("github_repo", "pyansys-geometry")
    return index_storage, project_name, github_repo


def setup_llm():
    try:
        Settings.llm = AzureOpenAI(
            model="gpt-35-turbo-16k",
            deployment_name="gpt-4o",
            api_key=API_KEY,
            azure_endpoint=AZURE_ENDPOINT,
            api_version=API_VERSION,
        )
        Settings.embed_model = AzureOpenAIEmbedding(
            model="text-embedding-ada-002",
            deployment_name="text-embedding-ada-002",
            api_key=API_KEY,
            azure_endpoint=AZURE_ENDPOINT,
            api_version=API_VERSION,
        )
        return True
    except Exception as e:
        print(f"[LLM Setup Error] {e}")
        return False


def fast_json_load(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def load_index_optimized():
    try:
        index_dir = Path(INDEX_STORAGE)
        if not index_dir.exists():
            return None

        required_files = ["docstore.json", "index_store.json", "default__vector_store.json"]
        for file in required_files:
            if not (index_dir / file).exists():
                print(f"Missing required file: {file}")
                return None

        file_sizes = {f: (index_dir / f).stat().st_size for f in required_files}

        def load_file(file_info):
            filename, file_path = file_info
            try:
                data = fast_json_load(file_path)
                return filename, data
            except Exception as e:
                print(f"Failed to load {filename}: {e}")
                return filename, None

        file_paths = [(f, index_dir / f) for f in required_files]
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(load_file, file_paths))

        if any(data is None for _, data in results):
            return None

        from llama_index.core import StorageContext, load_index_from_storage

        storage_context = StorageContext.from_defaults(persist_dir=str(index_dir))
        return load_index_from_storage(storage_context)

    except Exception as e:
        print(f"[Optimized Load Error] {e}")
        return None


def create_new_index():
    try:
        client = GithubClient(github_token=GITHUB_TOKEN, verbose=True)
        reader = GithubRepositoryReader(owner="ansys", repo=GITHUB_REPO, github_client=client)
        documents = reader.load_data(branch="main")
        return VectorStoreIndex.from_documents(documents)
    except Exception as e:
        raise Exception(f"Index creation failed: {e}")


def initialize_chatbot():
    global chat_engine, retriever, initialization_status, INDEX_STORAGE, PROJECT_NAME, GITHUB_URL
    if initialization_status["loading"]:
        return
    initialization_status["loading"] = True
    initialization_status["error"] = None
    socketio.emit("status_update", {"status": f"Setting up AI models for {PROJECT_NAME}..."})
    try:
        if not setup_llm():
            raise Exception("LLM setup failed")
        index_dir = Path(INDEX_STORAGE)
        if not index_dir.exists():
            index_dir.mkdir(parents=True)
        index = load_index_optimized() or create_new_index()
        if index and not index_dir.exists():
            os.makedirs(index_dir)
            index.storage_context.persist(index_dir)
        retriever = VectorIndexRetriever(index=index, similarity_top_k=10)
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=get_response_synthesizer(),
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
        )
        query_engine.update_prompts(
            {"response_synthesizer:summary_template": PromptTemplate(default_prompts())}
        )
        memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
        chat_engine = CondensePlusContextChatEngine.from_defaults(
            retriever=retriever,
            memory=memory,
            verbose=True,
        )
        initialization_status.update(
            {
                "initialized": True,
                "loading": False,
                "status": f"Ready! ⚡ Optimized {PROJECT_NAME} chat is live.",
                "project_name": PROJECT_NAME,
                "github_url": GITHUB_URL,
            }
        )
        socketio.emit("initialization_complete", initialization_status)
    except Exception as e:
        initialization_status.update(
            {"loading": False, "error": str(e), "status": f"Initialization error: {e}"}
        )
        socketio.emit("initialization_error", initialization_status)


def create_chat_session(session_id):
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
    session_chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        memory=memory,
        verbose=True,
        system_prompt=f"""
        You are a senior software engineer and expert on the {GITHUB_REPO} library.
        Answer questions based ONLY on the provided documentation context.
        If the question is unrelated, say: 'Sorry I can only answer questions based on the provided documentation and codebase.'
        """,
    )
    chat_sessions[session_id] = session_chat_engine
    return session_chat_engine


def get_chat_session(session_id):
    return chat_sessions.get(session_id) or create_chat_session(session_id)


# === Flask Routes ===


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def get_status():
    return jsonify(initialization_status)


@app.route("/api/initialize", methods=["POST"])
def api_initialize():
    if initialization_status["initialized"]:
        return jsonify({"message": "Already initialized"})
    elif initialization_status["loading"]:
        return jsonify({"message": "Initialization in progress"})
    else:
        threading.Thread(target=initialize_chatbot, daemon=True).start()
        return jsonify({"message": "Initialization started"})


@app.route("/api/rebuild", methods=["POST"])
def api_rebuild():
    global chat_engine, retriever, chat_sessions
    from shutil import rmtree

    if initialization_status["loading"]:
        return jsonify({"error": "Already loading"}), 400

    if os.path.exists(INDEX_STORAGE):
        rmtree(INDEX_STORAGE)

    chat_engine = None
    retriever = None
    chat_sessions.clear()
    initialization_status.update({"initialized": False, "error": None})

    threading.Thread(target=initialize_chatbot, daemon=True).start()
    return jsonify({"message": "Rebuild started"})


@app.route("/api/chat/history/<session_id>")
def get_chat_history(session_id):
    engine = chat_sessions.get(session_id)
    if not engine:
        return jsonify({"error": "Session not found"}), 404
    messages = engine.memory.get_all() if engine.memory else []
    return jsonify(
        {
            "session_id": session_id,
            "history": [{"role": m.role, "content": str(m.content)} for m in messages],
            "message_count": len(messages),
        }
    )


@app.route("/api/chat/sessions")
def get_active_sessions():
    return jsonify(
        {"active_sessions": list(chat_sessions.keys()), "session_count": len(chat_sessions)}
    )


# === Socket.IO Events ===


@socketio.on("connect")
def handle_connect():
    emit("initialization_status", initialization_status)


@socketio.on("send_message")
def handle_message(data):
    if not initialization_status["initialized"]:
        emit("bot_response", {"message": "Please initialize the chatbot first!", "error": True})
        return

    session_id = request.sid
    user_message = data.get("message", "").strip()
    if not user_message:
        return

    emit("bot_typing", {"typing": True})

    try:
        engine = get_chat_session(session_id)
        response = engine.chat(user_message)
        emit(
            "bot_response",
            {
                "message": str(response),
                "error": False,
                "response_time": f"{time.time() - data.get('timestamp', time.time()):.2f}s",
                "session_id": session_id,
            },
        )
    except Exception as e:
        emit("bot_response", {"message": f"Error: {e}", "error": True})
    finally:
        emit("bot_typing", {"typing": False})


@socketio.on("disconnect")
def handle_disconnect():
    session_id = request.sid
    chat_sessions.pop(session_id, None)


@socketio.on("clear_chat")
def handle_clear_chat():
    session_id = request.sid
    chat_sessions.pop(session_id, None)
    emit("chat_cleared", {"message": "Chat cleared."})


# === App Entry ===
def pyansys_chat_navigator(sphinx_app):
    """Initialize the PyAnsys Chat Navigator."""
    global INDEX_STORAGE, PROJECT_NAME, GITHUB_REPO
    INDEX_STORAGE, PROJECT_NAME, GITHUB_REPO = initialise_library(sphinx_app)
    print(f"🚀 Starting {PROJECT_NAME} Chat Navigator...")
    thread = threading.Thread(target=initialize_chatbot, daemon=True)
    thread.start()
    socketio.run(app, host="0.0.0.0", port=5002, debug=False)
