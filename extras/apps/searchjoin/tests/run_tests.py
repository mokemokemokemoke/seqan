#!/usr/bin/env python
"""Execute the tests for search/join.

The golden test outputs are generated by the script generate_outputs.sh.

You have to give the root paths to the source and the binaries as arguments to
the program.  These are the paths to the directory that contains the 'projects'
directory.

Usage:  run_tests.py SOURCE_ROOT_PATH BINARY_ROOT_PATH
"""
import logging
import os.path
import sys
import glob

# Automagically add util/py_lib to PYTHONPATH environment variable.
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                    '..', '..', 'util', 'py_lib'))

sys.path.insert(0, path)

import seqan.app_tests as app_tests

transforms = [
	app_tests.UniqueTransform(left=False, right=True)
]

def main(source_base, binary_base):
    """Main entry point of the script."""

    print 'Executing test for searchjoin'
    print '==========================='
    print
    
    ph = app_tests.TestPathHelper(
        source_base, binary_base,
        'extras/apps/searchjoin/tests')  # tests dir

    # ============================================================
    # Auto-detect the binary path.
    # ============================================================

    path_to_join = app_tests.autolocateBinary(
      binary_base, 'bin', 's4_join')

    path_to_search = app_tests.autolocateBinary(
      binary_base, 'bin', 's4_search')

    # ============================================================
    # Built TestConf list.
    # ============================================================

    # Build list with TestConf objects, analoguely to how the output
    # was generated in generate_outputs.sh.
    conf_list = []

    # ============================================================
    # Define program parameters.
    # ============================================================

    # Seed length
    SL = {
            'geo': ['5'],
            'dna': ['10']
    }
    # Errors
    K  = {
            'geo': ['0', '1', '3'],
            'dna': ['0', '8', '16']
    }
    # Threads
    THREADS = '4'

    # ============================================================
    # Configure Join Tests.
    # ============================================================

    for alphabet in ['geo', 'dna']:
        for k in K[alphabet]:
            for sl in SL[alphabet]:
                conf = app_tests.TestConf(
                    program=path_to_join,
#                    redir_stdout=ph.outFile('join_%s_%s_%s.stdout' % (alphabet, k, sl)),
                    args=[ph.inFile('%s_database.csv' % alphabet), k,
                          '-i', alphabet,
                          '-t', THREADS,
                          '-sl', sl,
                          '-o', ph.outFile('join_%s_%s_%s.out' % (alphabet, k, sl))],
                    to_diff=[(ph.inFile('join_%s_%s.out' % (alphabet, k)),
                             ph.outFile('join_%s_%s_%s.out' % (alphabet, k, sl)),
                             transforms)])
                conf_list.append(conf)

    # ============================================================
    # Configure Search Tests.
    # ============================================================

    for alphabet in ['geo', 'dna']:
        for sl in SL[alphabet]:
            conf = app_tests.TestConf(
                program=path_to_search,
#                redir_stdout=ph.outFile('search_%s_%s.stdout' % (alphabet, sl)),
                args=[ph.inFile('%s_database.csv' % alphabet),
                      ph.inFile('%s_queries.csv' % alphabet),
                      '--no-wait',
                      '-i', alphabet,
                      '-t', THREADS,
                      '-sl', sl,
                      '-o', ph.outFile('search_%s_%s.out' % (alphabet, sl))],
                to_diff=[(ph.inFile('search_%s.out' % (alphabet)),
                         ph.outFile('search_%s_%s.out' % (alphabet, sl)),
                         transforms)])
            conf_list.append(conf)

    # ============================================================
    # Run Tests.
    # ============================================================

    # Execute the tests.
    failures = 0
    for conf in conf_list:
        res = app_tests.runTest(conf)
        # Output to the user.
        print ' '.join([conf.program] + conf.args),
        if res:
             print 'OK'
        else:
            failures += 1
            print 'FAILED'

    # Cleanup.
    ph.deleteTempDir()

    print '=============================='
    print '     total tests: %d' % len(conf_list)
    print '    failed tests: %d' % failures
    print 'successful tests: %d' % (len(conf_list) - failures)
    print '=============================='
    # Compute and return return code.
    return failures != 0


if __name__ == '__main__':
    sys.exit(app_tests.main(main))
