from collections import namedtuple

from coala_decorators.decorators import generate_eq, generate_repr


@generate_repr()
@generate_eq("documentation", "language", "docstyle",
             "indent", "marker", "range")
class DocumentationComment:
    """
    The DocumentationComment holds information about a documentation comment
    inside source-code, like position etc.
    """
    Parameter = namedtuple('Parameter', 'name, desc')
    ReturnValue = namedtuple('ReturnValue', 'desc')
    Description = namedtuple('Description', 'desc')

    def __init__(self, documentation, language, docstyle,
                 indent=None, marker=None, range=None):
        """
        Instantiates a new DocumentationComment.

        :param documentation: The documentation text.
        :param language:      The language of the documention.
        :param docstyle:      The docstyle used in the documentation.
        :param indent:        The indentation in spaces used in the
                              documentation.
        :param marker:        The three-element tuple with marker strings,
                              that identified this documentation comment.
        :param range:         The position range of type TextRange.
        """
        self.documentation = documentation
        self.language = language
        self.docstyle = docstyle
        self.indent = indent
        self.marker = marker
        self.range = range

    def __str__(self):
        return self.documentation

    def parse_documentation(self):
        """
        Parses documentation independent of language and docstyle.

        :return:
            A list of the parsed documentation metadata.
        :raises:
            NotImplementedError
        """
        if self.language == "python" and self.docstyle == "default":
            return self.parse_python_default()
        else:
            raise NotImplementedError(
                "Documentation parsing for {0.language!r} in {0.docstyle!r}"
                " has not been implemented yet".format(self))

    def parse_python_default(self):
        """
        Parse documentation. Usable attributes are:

        - ``:param``
        - ``:return:``

        :return: A list of parsed sections(descriptions, params, return values)
        """
        lines = self.documentation.splitlines(keepends=True)

        param_identifier = (":param ", ": ")
        return_identifier = ":return:"

        return self._parse_documentation_with_symbols(lines, param_identifier,
                                                      return_identifier)

    def _parse_documentation_with_symbols(self, lines, param_data, return_data):
        """
        Parses documentation based on parameter and return symbols.

        :param lines:       The lines of documentation to parse.
        :param param_data:  The strings with which a parameter description
                            starts and ends.
        :param return_data: The string with which a return description starts.
        :return:            The list of all the parsed sections of the
                            documentation.
        """
        parse_mode = self.Description

        cur_param = ""

        desc = ""
        parsed = []

        for line in lines:
            if line.strip().startswith(param_data[0]):
                parse_mode = self.Parameter
                splitted = line[len(param_data[0]):].split(param_data[1], 1)
                cur_param = splitted[0].strip()
                param_desc = ""
                # For cases where the param description is not on the
                # same line, but on subsequent lines.
                try:
                    param_desc = splitted[1]
                except IndexError:
                    pass
                parsed.append(self.Parameter(name=cur_param, desc=param_desc))

            elif line.strip().startswith(return_data):
                parse_mode = self.ReturnValue
                retval_desc = line[len(return_data) + 1:]
                parsed.append(self.ReturnValue(desc=retval_desc))

            elif parse_mode == self.ReturnValue:
                retval_desc += line
                parsed.pop()
                parsed.append(self.ReturnValue(desc=retval_desc))
            elif parse_mode == self.Parameter:
                param_desc += line
                parsed.pop()
                parsed.append(self.Parameter(name=cur_param, desc=param_desc))
            else:
                desc += line
                # This is inside a try-except for cases where the list
                # is empty and has nothing to pop.
                try:
                    parsed.pop()
                except IndexError:
                    pass
                parsed.append(self.Description(desc=desc))

        return parsed
