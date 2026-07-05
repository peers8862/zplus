"""Access to bundled package data: the type library, profiles, and seed files."""
from importlib.resources import files


def data_root():
    return files("zplus") / "data"


def read_data(*parts):
    node = data_root()
    for p in parts:
        node = node / p
    return node.read_bytes()


def types_root():
    return data_root() / "types"


def profiles_root():
    return data_root() / "profiles"


def list_types():
    """Names of doc types in the bundled library."""
    return sorted(p.name for p in types_root().iterdir()
                  if (p / "type.toml").is_file())


def list_profiles():
    """Names of bundled profiles (site kinds)."""
    return sorted(p.name[:-5] for p in profiles_root().iterdir()
                  if p.name.endswith(".toml"))


def read_type_fragment(name):
    """The `[[type]]` TOML fragment for a library type (concatenatable)."""
    return (types_root() / name / "type.toml").read_text(encoding="utf-8")


def read_type_template(name):
    """The seed template bytes for a library type."""
    return (types_root() / name / "template.md").read_bytes()


def read_profile(name):
    return (profiles_root() / f"{name}.toml").read_text(encoding="utf-8")
