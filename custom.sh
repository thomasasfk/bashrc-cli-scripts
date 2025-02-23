BASHRC_EXEC_DIR="$HOME/.bashrc-exec"
PYTHON_INTERPRETER="$BASHRC_EXEC_DIR/.venv/Scripts/python"
SCRIPT_DIR="$BASHRC_EXEC_DIR/scripts"

apply_hooks() {
	. ~/.git-templates/apply-hooks.sh
}

alias gemini="$PYTHON_INTERPRETER $SCRIPT_DIR/gemini.py"
alias ai="$PYTHON_INTERPRETER $SCRIPT_DIR/ai.py"

gemini_c() {
    $PYTHON_INTERPRETER $SCRIPT_DIR/gemini.py "$@"
}
export -f gemini_c

ai_c() {
    $PYTHON_INTERPRETER $SCRIPT_DIR/ai.py "$@"
}
export -f ai_c