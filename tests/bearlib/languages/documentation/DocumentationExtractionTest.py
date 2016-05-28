import os.path
import unittest

from coalib.bearlib.languages.documentation.DocstyleDefinition import (
    DocstyleDefinition)
from coalib.bearlib.languages.documentation.DocumentationComment import (
    DocumentationComment)
from coalib.bearlib.languages.documentation.DocumentationExtraction import (
    extract_documentation)
from coalib.results.TextRange import TextRange


class DocumentationExtractionTest(unittest.TestCase):

    def test_extract_documentation_invalid_input(self):
        with self.assertRaises(FileNotFoundError):
            tuple(extract_documentation("", "PYTHON", "INVALID"))

    @staticmethod
    def load_testdata(filename):
        filename = (os.path.dirname(os.path.realpath(__file__)) +
                    "/documentation_extraction_testdata/" + filename)
        with open(filename, "r") as fl:
            data = fl.read()

        return data.splitlines(keepends=True)

    def test_extract_documentation_C(self):
        data = DocumentationExtractionTest.load_testdata("data.c")

        # No built-in documentation for C.
        with self.assertRaises(KeyError):
            tuple(extract_documentation(data, "C", "default"))

        language = "c"
        docstyle = "doxygen"

        docstyle_C_doxygen = DocstyleDefinition.load(language, docstyle)

        expected_results = (
            DocumentationComment(
                ("\n"
                 " This is the main function.\n"
                 "\n"
                 " @returns Your favorite number.\n"),
                language, docstyle, 0,
                docstyle_C_doxygen.markers[0],
                TextRange.from_values(3, 1, 7, 4)),
            DocumentationComment(
                ("\n"
                 " Preserves alignment\n"
                 " - Main item\n"
                 "   - sub item\n"
                 "     - sub sub item\n"),
                language, docstyle, 0,
                docstyle_C_doxygen.markers[2],
                TextRange.from_values(15, 1, 20, 4)),
            DocumentationComment(
                (" ABC\n"
                 "    Another type of comment\n"
                 "\n"
                 "    ..."),
                language, docstyle, 0,
                docstyle_C_doxygen.markers[1],
                TextRange.from_values(23, 1, 26, 11)),
            DocumentationComment(
                (" foobar = barfoo.\n"
                 " @param x whatever...\n"),
                language, docstyle, 0,
                docstyle_C_doxygen.markers[0],
                TextRange.from_values(28, 1, 30, 4)))

        self.assertEqual(tuple(
            extract_documentation(data, language, docstyle)),
            expected_results)

    def test_extract_documentation_C_2(self):
        data = ['/** my main description\n', ' * continues here */']

        language = "c"
        docstyle = "doxygen"

        docstyle_C_doxygen = DocstyleDefinition.load(language, docstyle)

        self.assertEqual(
            list(extract_documentation(data, language, docstyle)),
            [DocumentationComment(" my main description\n continues here",
                                  language, docstyle, 0,
                                  docstyle_C_doxygen.markers[0],
                                  TextRange.from_values(1, 1, 2, 21))])

    def test_extract_documentation_CPP(self):
        data = DocumentationExtractionTest.load_testdata("data.cpp")

        # No built-in documentation for C++.
        with self.assertRaises(KeyError):
            tuple(extract_documentation(data, "CPP", "default"))

        language = "cpp"
        docstyle = "doxygen"

        docstyle_CPP_doxygen = DocstyleDefinition.load(language, docstyle)

        self.assertEqual(tuple(
            extract_documentation(data, language, docstyle)),
            (DocumentationComment(
                ("\n"
                 " This is the main function.\n"
                 " @returns Exit code.\n"
                 "          Or any other number.\n"),
                language, docstyle, 0,
                docstyle_CPP_doxygen.markers[0],
                TextRange.from_values(4, 1, 8, 4)),
             DocumentationComment(
                (" foobar\n"
                 " @param xyz\n"),
                language, docstyle, 0,
                docstyle_CPP_doxygen.markers[0],
                TextRange.from_values(15, 1, 17, 4)),
             DocumentationComment(
                " Some alternate style of documentation\n",
                language, docstyle, 0,
                docstyle_CPP_doxygen.markers[4],
                TextRange.from_values(22, 1, 23, 1)),
             DocumentationComment(
                " ends instantly",
                language, docstyle, 4,
                docstyle_CPP_doxygen.markers[0],
                TextRange.from_values(26, 5, 26, 26)),
             DocumentationComment(
                (" Should work\n"
                 "\n"
                 " even without a function standing below.\n"
                 "\n"
                 " @param foo WHAT PARAM PLEASE!?\n"),
                language, docstyle, 0,
                docstyle_CPP_doxygen.markers[4],
                TextRange.from_values(32, 1, 37, 1))))

    def test_extract_documentation_CPP_2(self):
        data = DocumentationExtractionTest.load_testdata("data2.cpp")

        language = "cpp"
        docstyle = "doxygen"

        docstyle_CPP_doxygen = DocstyleDefinition.load(language, docstyle)

        self.assertEqual(tuple(
            extract_documentation(data, language, docstyle,)),
            (DocumentationComment(
                ("module comment\n"
                 " hello world\n"),
                language, docstyle, 0,
                docstyle_CPP_doxygen.markers[0],
                TextRange.from_values(1, 1, 3, 4)),))

    def test_extract_documentation_PYTHON3(self):
        data = DocumentationExtractionTest.load_testdata("data.py")

        self.maxDiff = None

        language = "python3"
        docstyle_default = "default"
        docstyle_doxygen = "doxygen"

        docstyle_PYTHON3_default = DocstyleDefinition.load(language,
                                                           docstyle_default)
        docstyle_PYTHON3_doxygen = DocstyleDefinition.load(language,
                                                           docstyle_doxygen)

        expected = (
            DocumentationComment(
                ("\n"
                 "Module description.\n"
                 "\n"
                 "Some more foobar-like text.\n"),
                language, docstyle_default, 0,
                docstyle_PYTHON3_default.markers[0],
                TextRange.from_values(1, 1, 5, 4)),
            DocumentationComment(
                ("\n"
                 "A nice and neat way of documenting code.\n"
                 ":param radius: The explosion radius.\n"),
                language, docstyle_default, 4,
                docstyle_PYTHON3_default.markers[0],
                TextRange.from_values(8, 5, 11, 8)),
            DocumentationComment(
                "\nA function that returns 55.\n",
                language, docstyle_default, 8,
                docstyle_PYTHON3_default.markers[0],
                TextRange.from_values(13, 9, 15, 12)),
            DocumentationComment(
                ("\n"
                 "Docstring with layouted text.\n"
                 "\n"
                 "    layouts inside docs are preserved for these "
                 "documentation styles.\n"
                 "this is intended.\n"),
                language, docstyle_default, 0,
                docstyle_PYTHON3_default.markers[0],
                TextRange.from_values(19, 1, 24, 4)),
            DocumentationComment(
                (" Docstring directly besides triple quotes.\n"
                 "    Continues here. "),
                language, docstyle_default, 0,
                docstyle_PYTHON3_default.markers[0],
                TextRange.from_values(26, 1, 27, 24)),
            DocumentationComment(
                ("super\n"
                 " nicely\n"
                 "short"),
                language, docstyle_default, 0,
                docstyle_PYTHON3_default.markers[0],
                TextRange.from_values(40, 1, 42, 9)))

        self.assertEqual(
            tuple(extract_documentation(data, language, docstyle_default)),
            expected)

        # Change only the docstyle in expected results.
        expected = list(DocumentationComment(r.documentation,
                                             r.language,
                                             docstyle_doxygen,
                                             r.indent,
                                             r.marker,
                                             r.range)
                        for r in expected)

        expected.insert(5, DocumentationComment(
            (" Alternate documentation style in doxygen.\n"
             "  Subtext\n"
             " More subtext (not correctly aligned)\n"
             "      sub-sub-text\n"
             "\n"),
            language, docstyle_doxygen, 0,
            docstyle_PYTHON3_doxygen.markers[1],
            TextRange.from_values(30, 1, 35, 1)))

        self.assertEqual(
            list(extract_documentation(data, language, docstyle_doxygen)),
            expected)

    def test_extract_documentation_PYTHON3_2(self):
        data = ['\n', '""" documentation in single line  """\n', 'print(1)\n']

        language = "python3"
        docstyle = "default"

        docstyle_PYTHON3_default = DocstyleDefinition.load(language,
                                                           docstyle)

        self.assertEqual(
            list(extract_documentation(data, language, docstyle)),
            [DocumentationComment(" documentation in single line  ",
                                  language, docstyle, 0,
                                  docstyle_PYTHON3_default.markers[0],
                                  TextRange.from_values(2, 1, 2, 38))])

    def test_extract_documentation_PYTHON3_3(self):
        data = ['## documentation in single line without return at end.']

        language = "python3"
        docstyle = "doxygen"

        docstyle_PYTHON3_doxygen = DocstyleDefinition.load(language,
                                                           docstyle)

        self.assertEqual(
            list(extract_documentation(data, language, docstyle)),
            [DocumentationComment(" documentation in single line without "
                                  "return at end.",
                                  language, docstyle, 0,
                                  docstyle_PYTHON3_doxygen.markers[1],
                                  TextRange.from_values(1, 1, 1, 55))])
