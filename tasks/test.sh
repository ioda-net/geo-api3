#!/usr/bin/env BASH


HELP['check']="manuel check

Launch lint and tests."
function check {
    lint
    test
}


HELP['lint']="manuel lint

Lint the python files with flake8"
function lint {
    "${FLAKE8}"  --max-line-length 99 --exclude "conf.py" chsdi
}



HELP['test']="manuel test [ARGS]

If no args are given, launch all tests.
If args is set, these arguments are passed to nose. This is equivalent to:
\t'nose ARGS'"
function test {
    if (( $# == 0)); then
        "${NOSE}" --ignore-files test_protocol.py --cover-html
    else
        "${NOSE}" "$@"
    fi
}
