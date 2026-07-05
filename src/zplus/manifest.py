"""Load and validate a project's `zplus.toml` manifest — the doc-type registry.

The engine reads this; the future `add-type` command writes it. Kept read-only
here (SP1); parsing is via stdlib `tomllib`.
"""
import tomllib
from dataclasses import dataclass, field

from . import paths

VALID_SHAPES = {"prose", "list", "task"}


@dataclass
class Section:
    heading: str
    shape: str = "prose"
    prompt: str = ""


@dataclass
class DocType:
    name: str
    label: str
    folder: str
    template: str
    sections: list = field(default_factory=list)


@dataclass
class Project:
    managed_nav: str = "ZPLUS_TYPES"
    deploy_branch: str = "gh-pages"
    deploy_remote: str = ""


@dataclass
class Manifest:
    project: Project
    types: list = field(default_factory=list)

    def type_by_name(self, name):
        for t in self.types:
            if t.name == name:
                return t
        return None


def from_dict(data, source="<dict>"):
    proj = data.get("project", {})
    project = Project(
        managed_nav=proj.get("managed_nav", "ZPLUS_TYPES"),
        deploy_branch=proj.get("deploy_branch", "gh-pages"),
        deploy_remote=proj.get("deploy_remote", ""),
    )
    types = []
    seen = set()
    for t in data.get("type", []):
        for key in ("name", "label", "folder", "template"):
            if key not in t:
                raise ValueError(f"{source}: a [[type]] is missing required '{key}'")
        if t["name"] in seen:
            raise ValueError(f"{source}: duplicate type name '{t['name']}'")
        seen.add(t["name"])
        sections = []
        for s in t.get("section", []):
            if "heading" not in s:
                raise ValueError(
                    f"{source}: a section in type '{t['name']}' is missing 'heading'")
            shape = s.get("shape", "prose")
            if shape not in VALID_SHAPES:
                raise ValueError(
                    f"{source}: invalid shape '{shape}' in "
                    f"'{t['name']}/{s['heading']}' (use prose|list|task)")
            sections.append(Section(heading=s["heading"], shape=shape,
                                    prompt=s.get("prompt", "")))
        types.append(DocType(name=t["name"], label=t["label"],
                             folder=t["folder"], template=t["template"],
                             sections=sections))
    return Manifest(project=project, types=types)


def loads(text, source="<string>"):
    return from_dict(tomllib.loads(text), source=source)


def load(path):
    with open(path, "rb") as f:
        return from_dict(tomllib.load(f), source=str(path))


def load_default():
    """The manifest bundled with the package (the built-in 8 doc types)."""
    return loads(paths.read_data("zplus.default.toml").decode("utf-8"),
                 source="zplus.default.toml")
