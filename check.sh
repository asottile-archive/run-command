#!/usr/bin/env bash

RED=$(tput setab 1)
GREEN=$(tput setab 2)
NORMAL=$(tput sgr0)
col=$(tput cols)

exit_ret=0

print_found() {
    # Args: cols ret
    local cols=$1
    local ret=$2

    if [ $ret -ne 0 ]
    then
        exit_ret=1
        local find_text=$RED"Missing!"$NORMAL
    else
        local find_text=$GREEN"Found!"$NORMAL
    fi
    local A=$(printf '%*s\n' $cols $find_text)
    local B=${A// /.}
    echo "$B"
}

check_prog() {
    # Args: program name to check that it exists
    local prog_name=$1

    local check_text="Checking for $prog_name"
    local cols=$(($col - ${#check_text} + 6))

    echo -n "$check_text"
    which "$prog_name" >& /dev/null
    print_found "$cols" $?
}

check_python_module() {
    # Args: python name to check that it exists
    local module_name=$1

    local check_text="Checking for Python module $module_name"
    local cols=$(($col - ${#check_text} + 6))

    echo -n "$check_text"
    python -c "import $module_name" >& /dev/null
    print_found "$cols" $?
}

check_prog python
check_prog pyflakes
check_prog ipython
check_prog pip
check_python_module ipdb
check_python_module testify
check_python_module coverage
check_python_module json

exit $exit_ret
