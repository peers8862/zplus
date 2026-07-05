"""Access to data: the bundled library (in-package) + a writable user library.

Types/profiles resolve from a **merged** view — a user library at `$ZPLUS_HOME`
(default `~/.config/zplus/`) overlays and extends the bundled defaults. Authoring
commands (`add-type`, `add-profile`) write to the user library so the pip-installed
package is never edited in place.
"""
import os
from importlib.resources import files


# --- locations ---

def _bundled():
    return files("zplus") / "data"


def user_home():
    return os.environ.get("ZPLUS_HOME") or os.path.expanduser("~/.config/zplus")


def user_type_dir(name):
    return os.path.join(user_home(), "types", name)


def user_profile_path(name):
    return os.path.join(user_home(), "profiles", f"{name}.toml")


# --- generic bundled data (env.example, …) ---

def data_root():
    return _bundled()


def read_data(*parts):
    node = _bundled()
    for p in parts:
        node = node / p
    return node.read_bytes()


# --- type library (bundled ∪ user) ---

def _bundled_types():
    return [p.name for p in (_bundled() / "types").iterdir()
            if (p / "type.toml").is_file()]


def _user_types():
    root = os.path.join(user_home(), "types")
    if not os.path.isdir(root):
        return []
    return [n for n in os.listdir(root)
            if os.path.isfile(os.path.join(root, n, "type.toml"))]


def list_types():
    return sorted(set(_bundled_types()) | set(_user_types()))


def read_type_fragment(name):
    up = os.path.join(user_type_dir(name), "type.toml")
    if os.path.exists(up):
        with open(up, encoding="utf-8") as f:
            return f.read()
    return (_bundled() / "types" / name / "type.toml").read_text(encoding="utf-8")


def read_type_template(name):
    up = os.path.join(user_type_dir(name), "template.md")
    if os.path.exists(up):
        with open(up, "rb") as f:
            return f.read()
    return (_bundled() / "types" / name / "template.md").read_bytes()


# --- profiles (bundled ∪ user) ---

def _bundled_profiles():
    return [p.name[:-5] for p in (_bundled() / "profiles").iterdir()
            if p.name.endswith(".toml")]


def _user_profiles():
    root = os.path.join(user_home(), "profiles")
    if not os.path.isdir(root):
        return []
    return [n[:-5] for n in os.listdir(root) if n.endswith(".toml")]


def list_profiles():
    return sorted(set(_bundled_profiles()) | set(_user_profiles()))


def read_profile(name):
    up = user_profile_path(name)
    if os.path.exists(up):
        with open(up, encoding="utf-8") as f:
            return f.read()
    return (_bundled() / "profiles" / f"{name}.toml").read_text(encoding="utf-8")
