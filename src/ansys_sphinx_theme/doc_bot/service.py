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

"""Optimized Flask Web Service for PyAnsys Doc Bot."""

import os
from pathlib import Path
import threading

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from llama_index.core import PromptTemplate, Settings, get_response_synthesizer
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from ansys_sphinx_theme.doc_bot.prompts import DEFAULT_PROMPT

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"
socketio = SocketIO(app, cors_allowed_origins="*")

# Globals
chat_sessions = {}  # { (lib_name, session_id): chat_engine }
initialization_status = {}  # { lib_name: {...} }

# Environment vars
API_KEY = os.getenv("API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
API_VERSION = os.getenv("API_VERSION")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

LLM_MODEL = os.getenv("MODEL_NAME")
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL")
LLM_DEPLOYMENT_NAME = os.getenv("LLM_DEPLOYMENT_NAME")
EMBEDDINGS_DEPLOYMENT_NAME = os.getenv("EMBEDDINGS_DEPLOYMENT_NAME")

THIS_DIR = Path(__file__).parent
INDEX_STORAGE = THIS_DIR / "index"


def setup_llm():
    """Set the LLM and embeddings with Azure OpenAI."""
    try:
        # Settings.llm = AzureOpenAI(
        #     model=LLM_MODEL,
        #     deployment_name=LLM_DEPLOYMENT_NAME,
        #     api_key=API_KEY,
        #     azure_endpoint=AZURE_ENDPOINT,
        #     api_version=API_VERSION,
        # )
        # Settings.embed_model = AzureOpenAIEmbedding(
        #     model=EMBEDDINGS_MODEL,
        #     deployment_name=EMBEDDINGS_DEPLOYMENT_NAME,
        #     api_key=API_KEY,
        #     azure_endpoint=AZURE_ENDPOINT,
        #     api_version=API_VERSION,
        # )
        Settings.llm = Ollama(model="llama3.2", request_timeout=120.0, max_tokens=100, repetition_penalty=1.5, temperature=0.1)
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.embed_model = embed_model
        return True
    except Exception as e:
        print(f"LLM Setup Error: {e}")
        return False


def load_index_optimized(lib_name):
    """Load the index for the given library."""
    index_dir = Path(INDEX_STORAGE) / lib_name

    if not index_dir.exists():
        print(f"[DEBUG] Index directory {index_dir} does not exist.")
        return None
    from llama_index.core import StorageContext, load_index_from_storage

    try:
        storage_context = StorageContext.from_defaults(persist_dir=str(index_dir))
        return load_index_from_storage(storage_context)
    except Exception as e:
        print(f"Failed loading index for {lib_name}: {e}")
        return None

# from llama_index.core.prompts import RichPromptTemplate

# text_qa_template_str = """Context information is below:
# <context>
# {{ context_str }}
# </context>

# Using both the context information as an expert in library, ans
# {{ query_str }} as an expert in library
# """
# text_qa_template = RichPromptTemplate(text_qa_template_str)

# refine_template_str = """New context information has been provided:
# <context>
# {{ context_msg }}
# </context>

# We also have an existing answer generated using previous context:
# <existing_answer>
# {{ existing_answer }}
# </existing_answer>

# Using the new context, either update the existing answer, or repeat it if the new context is not relevant, when answering this query:
# {query_str}
# """
# refine_template = RichPromptTemplate(refine_template_str)


def initialize_chatbot(lib_name):
    """Initialize the chatbot for the given library."""
    if lib_name in initialization_status and initialization_status[lib_name].get("loading"):
        return

    initialization_status[lib_name] = {
        "initialized": False,
        "loading": True,
        "error": None,
        "status": "Initializing...",
    }

    def _init():
        """Initialize the chatbot for the given library."""
        if not setup_llm():
            initialization_status[lib_name].update(
                {"loading": False, "error": "LLM setup failed", "status": "Failed"}
            )
            return

        index = load_index_optimized(lib_name)
        if index is None:
            initialization_status[lib_name].update(
                {"loading": False, "error": f"Index for {lib_name} not found", "status": "Failed"}
            )
            return

        retriever = VectorIndexRetriever(index=index, similarity_top_k=10)
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=get_response_synthesizer(),
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
        )
        prompt = PromptTemplate(DEFAULT_PROMPT)
        query_engine.update_prompts({"response_synthesizer:summary_template": prompt})

        initialization_status[lib_name].update(
            {"initialized": True, "loading": False, "status": "Ready"}
        )

    threading.Thread(target=_init).start()


def get_chat_session(lib_name, session_id):
    """Get or create a chat session for the given library and session ID."""
    key = (lib_name, session_id)
    if key in chat_sessions:
        return chat_sessions[key]

    memory = ChatMemoryBuffer.from_defaults(token_limit=1000)
    prompt = PromptTemplate(DEFAULT_PROMPT)
    retriever = VectorIndexRetriever(index=load_index_optimized(lib_name), similarity_top_k=10)
    chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
        memory=memory,
        verbose=True,
        condense_question_prompt=prompt,
        # system_prompt="""You are a senior software engineer and expert on the {lib_name} library.
        # avoiding unnecessary elaboration or additional context unless explicitly requested.
        # If a response requires further detail, prioritize the most relevant information and conclude promptly.
        
        # Your job is to answer questions based ONLY on the provided documentation context.
        # Using the scraped documentation and GitHub repository as your knowledge base, respond
        # precisely and clearly to user questions.
        # Your response must:
        # 1. Be concise and relevant to the question
        # 2. Use the provided context to answer the question
        # 3. If the question is not related to the {lib_name} library or there is no relative context,
        # respond EXACTLY with: "Sorry i can only answer questions based on the provided documentation
        # and codebase." and provide the docs link to the documentation
        # 4. Be concise but helpful in your responses
        # Avoid apologies or mentions of limitations; simply deliver the most direct and straightforward answer.

        # Only answer based on the **Context**, Do NOT CREATE NEW INFORMATION"""
    )
    chat_sessions[key] = chat_engine
    return chat_engine


@app.route("/<lib_name>/api/status")
def api_status(lib_name):
    """Get the initialization status of the chatbot for the given library."""
    return jsonify(initialization_status.get(lib_name, {"status": "Not initialized"}))


@app.route("/<lib_name>/api/initialize", methods=["POST"])
def api_initialize(lib_name):
    """Initialize the chatbot for the given library."""
    initialize_chatbot(lib_name)
    return jsonify({"message": f"Initialization started for {lib_name}"})


@socketio.on("connect")
def handle_connect():
    """Handle new socket connection."""
    session_id = request.sid
    lib_name = request.args.get("lib_name", "ansys-sphinx-theme")
    print(f"[DEBUG] New connection: {session_id} for library {lib_name}")

    initialize_chatbot(lib_name)

    if lib_name not in initialization_status:
        initialization_status[lib_name] = {
            "initialized": False,
            "loading": False,
            "error": None,
            "status": "Not initialized",
        }

    if not initialization_status[lib_name]["initialized"]:
        initialize_chatbot(lib_name)

    emit("connected", {"message": f"Connected to {lib_name}", "session_id": session_id})


@socketio.on("send_message")
def handle_message(data):
    """Handle incoming messages from the client."""
    lib_name = data.get("lib")
    message = data.get("message")
    session_id = request.sid
    if not initialization_status.get(lib_name, {}).get("initialized"):
        emit("bot_response", {"message": initialization_status[lib_name]["error"], "error": True})
    try:
        engine = get_chat_session(lib_name, session_id)
        response = engine.chat(message)
        emit("bot_response", {"message": str(response), "error": False})
    except Exception as e:
        emit("bot_response", {"message": f"Error: {str(e)}", "error": True})


@socketio.on("disconnect")
def cleanup():
    """Handle socket disconnection."""
    sid = request.sid
    to_delete = [key for key in chat_sessions if key[1] == sid]
    for key in to_delete:
        del chat_sessions[key]


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=15300)
