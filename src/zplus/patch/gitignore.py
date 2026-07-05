"""Idempotent management of a zplus block in a project's .gitignore."""
import re

BEGIN = "# >>> zplus (managed) >>>"
END = "# <<< zplus (managed) <<<"
LINES = ["/site/", ".env", ".env.*", "!.env.example", ".venv/",
         ".staticrypt.json", "node_modules/"]


def render_block():
    return BEGIN + "\n" + "\n".join(LINES) + "\n" + END


def ensure_block(text):
    """Return text with the managed block present exactly once. Idempotent."""
    block = render_block()
    if BEGIN in text and END in text:
        pat = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)
        return pat.sub(lambda _: block, text)
    prefix = text
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    if prefix and not prefix.endswith("\n\n"):
        prefix += "\n"
    return prefix + block + "\n"
