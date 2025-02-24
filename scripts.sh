#!/bin/bash

BASHRC_EXEC_DIR="$HOME/.bashrc-exec"
SCRIPT_DIR="$BASHRC_EXEC_DIR/scripts"
VENV_PYTHON="$BASHRC_EXEC_DIR/.venv/Scripts/python"

create_python_command() {
    local script_name="$1"
    local base_name="${script_name%.py}"

    alias "$base_name"="$VENV_PYTHON $SCRIPT_DIR/$script_name"

    eval "${base_name}_c() {
        $VENV_PYTHON $SCRIPT_DIR/$script_name \"\$@\"
    }"
    export -f "${base_name}_c"
}

load_python_scripts() {
    for script in "$SCRIPT_DIR"/*.py; do
        if [ -f "$script" ]; then
            script_name=$(basename "$script")
            create_python_command "$script_name"
        fi
    done
}

load_python_scripts