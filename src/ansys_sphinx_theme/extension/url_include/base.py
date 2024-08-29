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

"""``BaseInclude`` class for ``urlinclude`` directives."""

from pathlib import Path

from docutils import io, statemachine, utils
from docutils.parsers.rst import Directive, directives


class BaseInclude(Directive):
    """Provides the base directive for urlinclude directives."""

    def run(self, path=None):
        """Include a file as part of the content of the reStructuredText (RST) file.

        Depending on the options, the file (or a specified part of the file) is
        converted to nodes and returned or inserted into the input stream.

        Parameters
        ----------
        path : str, optional
            The path to the file to include. The default is None.

        Returns
        -------
        list
            A list of nodes to be inserted into the document.

        Raises
        ------
        Warning
            The directive is disabled.
        UnicodeEncodeError
            Problems occurred encoding the input file path.
        OSError
            Problems exist in the directive path.
        """
        if not self.state.document.settings.file_insertion_enabled:
            raise self.warning(f"'{self.name}' directive is disabled.")

        current_source = self.state.document.current_source
        path = directives.path(self.arguments[0]) if path is None else path

        if str(path).startswith("<") and str(path).endswith(">"):
            base_path = self.standard_include_path
            path = path[1:-1]
        else:
            base_path = Path(current_source).resolve().parent

        path = utils.relative_path(None, base_path / path)

        try:
            include_file = io.FileInput(
                source_path=path,
                encoding=self.state.document.settings.input_encoding,
                error_handler=self.e_handler,
            )
        except UnicodeEncodeError as error:
            raise self.severe(
                f'Problems occurred encoding the input file path "{path}": {io.error_string(error)}'
            )
        except OSError as error:
            raise self.severe(
                f'Problems exist in the "{self.name}" directive path: {io.error_string(error)}.'
            )
        else:
            self.state.document.settings.record_dependencies.add(path)

        try:
            rawtext = include_file.read()
        except UnicodeError as error:
            raise self.severe(
                f'Problem exists in the "{self.name}" directive: {io.error_string(error)}'
            )

        self.include_lines = statemachine.string2lines(
            rawtext, self.tab_width, convert_whitespace=True
        )
        clip_options = (None, None, None, None)

        include_log = self.state.document.include_log
        if not include_log:
            include_log.append(
                (
                    utils.relative_path(None, current_source),
                    (None, None, None, None),
                )
            )

        if (path, clip_options) in include_log:
            master_paths = (pth for (pth, opt) in reversed(include_log))
            inclusion_chain = "\n> ".join(path, *master_paths)
            raise self.warning(
                f'Circular inclusion exists in the "{self.name}" directive:\n{inclusion_chain}.'
            )

        if "parser" in self.options:
            document = utils.new_document(path, self.state.document.settings)
            document.include_log = include_log + [(path, clip_options)]
            parser = self.options["parser"]()
            parser.parse("\n".join(self.include_lines), document)
            document.transformer.populate_from_components(
                parser,
            )
            document.transformer.apply_transforms()
            return document.children

        self.include_lines += ["", f'.. end of inclusion from "{path}"']
        self.state_machine.insert_input(self.include_lines, path)
        include_log.append(path)
        return []
