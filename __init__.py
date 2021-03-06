# -*- coding: utf-8 -*-
"""
Snippety repeats chunks of text.

To Do:

    Find out if I can do def __init__(self, config=SnippetyConfig()):
    Save buffer prompt (In config, set type of prompt: shell or GUI)
    Create CapitalisedMarker * 2 using ~
    printout saying what files were affected.

    Beef up test suite
    Check nested directives work
    Make it easy to direct to output files
        get_output_path lambda
    File backup

    Feature: Output control. Users will want to:
        a) Write back to source file
        b) Write just output to another file.
        c) Write everything to another file.
        d) Write output to another file, and add stuff like class definitions...
    Feature: modify lines

    Allow executing as code is marker text starts with $
    Conditionals
    Flags
    User manual
    Pip
    As module:
        --eg: generate an example script to use
        --tests: runs all tests
        --help
        --version

Not done because it's tricky:
    multi-line directive
    allowing output blocks to have inline comment

Ideas:
    Use a flag system at the end | flag1 flag2

    Have a post processing function, which gets to read all the lines, and optionally cancel the output.
    Could use this to redirect to a different file, or modify the lines... Or collect all the import statements.


    sn.add_collection('person_fields',
        ['name', 'type', 'dbtype'],
        ['age', 'int', 'varchar(50)'],
        ['height', '', 'varchar(50)'],
        )

    Add a collection parser utility, for people who prefer keeping it in files?
    can also add collections directly as hashes.

"""
import os

# Order matters! http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html
from errors import DirectiveFormatError, FileParsingError
from markers import StandardMarker, IteratorMarker, KeyValueMarker
from snippety_config import SnippetyConfig
from directive_parser import DirectiveParser
from directive import Directive
from source_file_processor import SourceFileProcessor


class Snippety:
    """
    The entry point to using Snippety. Provides access methods to process files.
    """

    def __init__(self, config=None):
        if config is not None:
            self.config = config
        else:
            self.config = SnippetyConfig()

    def process_dir(self, dirpath, include=None, exclude=None, config=None):
        """Process the list files returned by collect_files. Refer to collect_files
        docstring for details on filtering.
        """
        if config is None:
            config = self.config
        for file in self.collect_files(dirpath, include, exclude):
            self.process_file(file, config=config)

    def collect_files(self, dirpath, include=None, exclude=None):
        """Returns a list of files, as used by process_dir. You can use this to
        check what files will be processed.

        Parameters 'include' and 'exclude' can be None, or lists of fnmatch pattern
        strings. (See python module fnmatch).


        If 'include' is not specified, all files in dirpath and subdirectories
        will be collected.
        If 'include' is specified, only files which match any of those patterns
        will be collected.
        If 'exclude' is specified, files which match any of those patterns will be
        removed from the list of files collected. Therefore 'exclude' overrides
        'include'.

        The match is relative to dirpath.
        Example:

        Find all .py files except those in dir 'test' directly under dirpath on
        Unix/Linux operating system:

            sn.collect_files(dirpath, include=['*.py'], exclude=['test/*'])

        Find all .py files except those in dir 'bin' anywhere under dirpath, on
        Windows operating system::

            sn.collect_files(dirpath, include=['*.py'], exclude=['*\\bin\\*'])

        """
        from fnmatch import fnmatch
        collected_files = []
        for root, dirs, files in os.walk(dirpath):
            for filename in files:
                filepath = os.path.join(root, filename)
                reltive_dir = os.path.relpath(root, dirpath)
                reltive_file_path = os.path.join(reltive_dir, filename)
                if include:
                    if any(fnmatch(reltive_file_path, pattern) for pattern in include):
                        collected_files.append(filepath)
                else:
                    collected_files.append(filepath)
                if exclude:
                    if filepath in collected_files:
                        if any(fnmatch(reltive_file_path, pattern) for pattern in exclude):
                            collected_files.remove(filepath)
                if filepath in collected_files:
                    print "Found ", reltive_file_path
        collected_files.sort()
        return collected_files

    def process_file(self, filepath, config=None):
        if config is None:
            config = self.config
        SourceFileProcessor(config).process_file(filepath)

__all__ = [
        'Snippety',
        'SnippetyConfig',
        'SourceFileProcessor',
        'Directive',
        'DirectiveParser',
        'StandardMarker',
        'IteratorMarker',
        'KeyValueMarker',
        'DirectiveFormatError',
        'FileParsingError',
        ]

if __name__ == "__main__":
    import pytest
    pytest.main()

