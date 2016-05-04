import unittest
import re
import os
import time

from pyprint.NullPrinter import NullPrinter

from coalib.misc.Caching import FileCache
from coalib.misc.CachingUtilities import (
    get_settings_hash, settings_changed, update_settings_db,
    pickle_load, pickle_dump
    )
from coalib.output.printers.LogPrinter import LogPrinter
from coalib import coala
from coalib.misc.ContextManagers import prepare_file
from tests.TestUtilities import execute_coala, bear_test_module


class CachingTest(unittest.TestCase):

    def setUp(self):
        current_dir = os.path.split(__file__)[0]
        self.caching_test_dir = os.path.join(
            current_dir,
            "caching_testfiles")
        self.log_printer = LogPrinter(NullPrinter())
        self.cache = FileCache(self.log_printer, "coala_test", flush_cache=True)

    def test_file_tracking(self):
        self.cache.track_files({"test.c", "file.py"})
        self.assertEqual(self.cache.data, {"test.c": -1, "file.py": -1})

        self.cache.untrack_files({"test.c"})
        self.assertFalse("test.c" in self.cache.data)
        self.assertTrue("file.py" in self.cache.data)

        self.cache.untrack_files({"test.c", "file.py"})
        self.assertFalse("test.c" in self.cache.data)
        self.assertFalse("file.py" in self.cache.data)

    def test_write(self):
        self.cache.track_files({"test2.c"})
        self.assertEqual(self.cache.data["test2.c"], -1)

        self.cache.write()
        self.assertNotEqual(self.cache.data["test2.c"], -1)

    def test_get_uncached_files(self):
        file_path = os.path.join(self.caching_test_dir, "test.c")
        cache = FileCache(self.log_printer, "coala_test3", flush_cache=True)

        # Since this is a new FileCache object, the return must be the full set
        self.assertEqual(cache.get_uncached_files({file_path}), {file_path})

        open(file_path, "w").close()
        cache.track_files({file_path})
        self.assertEqual(cache.get_uncached_files({file_path}), {file_path})

        cache.write()
        self.assertEqual(cache.get_uncached_files({file_path}), set())

        # Simulate changing the file and then getting uncached files
        # Since the file has been edited since the last run it's returned
        time.sleep(1)
        open(file_path, "w").close()
        cache = FileCache(self.log_printer, "coala_test3", flush_cache=False)
        cache.track_files({file_path})
        self.assertEqual(cache.get_uncached_files({file_path}), {file_path})
        cache.write()

        # Not changing the file should NOT return it the next time
        time.sleep(1)
        cache = FileCache(self.log_printer, "coala_test3", flush_cache=False)
        cache.track_files({file_path})
        print(cache.data)
        self.assertEqual(cache.get_uncached_files({file_path}), set())
        cache.write()

    def test_persistence(self):
        cache = FileCache(self.log_printer, "coala_test3", flush_cache=True)
        cache.track_files({"file.c"})
        cache.write()
        self.assertTrue("file.c" in cache.data)

        cache = FileCache(self.log_printer, "coala_test3", flush_cache=False)
        self.assertTrue("file.c" in cache.data)

    def test_time_travel(self):
        cache = FileCache(self.log_printer, "coala_test2", flush_cache=True)
        cache.track_files({"file.c"})
        cache.write()
        self.assertTrue("file.c" in cache.data)

        cache_data = pickle_load(self.log_printer, "coala_test2", {})
        # Back to the future :)
        # 2000000000 corresponds to the future year 2033
        cache_data["time"] = 2000000000
        pickle_dump(self.log_printer, "coala_test2", cache_data)

        cache = FileCache(self.log_printer, "coala_test2", flush_cache=False)
        self.assertFalse("file.c" in cache.data)

    def test_settings_change(self):
        sections = {}
        settings_hash = get_settings_hash(sections)
        update_settings_db(self.log_printer, settings_hash)
        self.assertFalse(settings_changed(self.log_printer, settings_hash))

        sections = {"a": 1}
        settings_hash = get_settings_hash(sections)
        self.assertTrue(settings_changed(self.log_printer, settings_hash))

    def test_caching_results(self):
        """
        A simple integration test to assert that results are not dropped
        when coala is ran multiple times with caching enabled.
        """
        with bear_test_module(), \
                prepare_file(["a=(5,6)"], None) as (lines, filename):
            retval, output = execute_coala(
                coala.main,
                "coala",
                "-l", "python")
            print(output)

            retval, output = execute_coala(
                coala.main,
                "coala",
                "-c", os.devnull,
                "--flush-cache",
                "--caching",
                "-f", re.escape(filename),
                "-b", "LineCountTestBear",
                "-L", "DEBUG")
            print(output)
            self.assertIn("This file has", output)

            retval, output = execute_coala(
                coala.main,
                "coala",
                "-c", os.devnull,
                "--caching",
                "-f", re.escape(filename),
                "-b", "LineCountTestBear")
            self.assertIn("This file has", output)
