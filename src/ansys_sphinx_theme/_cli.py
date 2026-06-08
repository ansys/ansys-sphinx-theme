# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Command-line interface for ansys-sphinx-theme."""

import argparse
import pathlib
import platform
import sys

from ansys_sphinx_theme import __version__ as _THEME_VERSION  # noqa: N812

_PROMPTS_ASSET_DIR = pathlib.Path(__file__).parent / "assets" / "prompts"


def _vscode_user_prompts_dir() -> pathlib.Path:
    """Return the VS Code user-level prompts directory for the current platform."""
    system = platform.system()
    if system == "Darwin":
        base = pathlib.Path.home() / "Library" / "Application Support" / "Code" / "User"
    elif system == "Windows":
        base = pathlib.Path.home() / "AppData" / "Roaming" / "Code" / "User"
    else:  # Linux / other
        base = pathlib.Path.home() / ".config" / "Code" / "User"
    return base / "prompts"


def _install_prompts(args: argparse.Namespace) -> None:
    """Copy GitHub Copilot prompt files into the current project or globally.

    Without ``--global``: copies files under ``.github/prompts/`` (prompts)
    and ``.github/agents/`` (agents) in the current working directory.
    With ``--global``: copies files into the VS Code user-level prompts
    directory so the commands are available across all workspaces.
    Files are always overwritten. The current theme version is injected into
    each file, replacing the ``{{theme_version}}`` placeholder.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.
    """
    if args.global_install:
        prompt_dest = _vscode_user_prompts_dir()
        agent_dest = prompt_dest  # user-level: all types share one folder
        prompt_dest.mkdir(parents=True, exist_ok=True)
        display = lambda p: str(p)  # noqa: E731
    else:
        cwd = pathlib.Path.cwd()
        prompt_dest = cwd / ".github" / "prompts"
        agent_dest = cwd / ".github" / "agents"
        prompt_dest.mkdir(parents=True, exist_ok=True)
        agent_dest.mkdir(parents=True, exist_ok=True)
        display = lambda p: str(p.relative_to(cwd))  # noqa: E731

    installed = []

    for src in _PROMPTS_ASSET_DIR.glob("*.prompt.md"):
        dest = prompt_dest / src.name
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        content = src.read_text(encoding="utf-8").replace("{{theme_version}}", _THEME_VERSION)
        dest.write_text(content, encoding="utf-8")
        installed.append(display(dest))

    for src in _PROMPTS_ASSET_DIR.glob("*.agent.md"):
        dest = agent_dest / src.name
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        content = src.read_text(encoding="utf-8").replace("{{theme_version}}", _THEME_VERSION)
        dest.write_text(content, encoding="utf-8")
        installed.append(display(dest))

    if installed:
        print("Installed:")
        for path in installed:
            print(f"  {path}")
    else:
        print("No prompt or agent files found in package assets.")

    if installed:
        scope = "all workspaces" if args.global_install else "this project"
        print(f"\nReload VS Code to pick up new slash commands and agents ({scope}).")
        if not args.global_install:
            print("Tip: commit these files to share them with your team.")


def main() -> None:
    """Entry point for the ansys-sphinx-theme CLI."""
    parser = argparse.ArgumentParser(
        prog="ansys-sphinx-theme",
        description="ansys-sphinx-theme command-line tools",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    install_parser = subparsers.add_parser(
        "install-prompts",
        help="Install GitHub Copilot prompt and agent files into the current project",
    )
    install_parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install into the VS Code user-level prompts folder (available in all workspaces)",
    )
    install_parser.set_defaults(func=_install_prompts)

    args = parser.parse_args()
    args.func(args)
    sys.exit(0)


if __name__ == "__main__":
    main()
