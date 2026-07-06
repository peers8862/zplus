"""Load and validate a project's `zplus.toml` manifest — the doc-type registry.

The engine reads this; the future `add-type` command writes it. Kept read-only
here (SP1); parsing is via stdlib `tomllib`.
"""
import tomllib
from dataclasses import dataclass, field

from . import paths

VALID_SHAPES = {"prose", "list", "task", "diagram"}
VALID_FIELD_TYPES = {"text", "enum", "multi-enum", "date", "number",
                     "bool", "owner", "status", "ref"}
VALID_ORDERS = {"alpha", "date-desc"}


@dataclass
class Section:
    heading: str
    shape: str = "prose"
    prompt: str = ""


@dataclass
class Field:
    name: str
    type: str = "text"
    required: bool = False
    values: list = field(default_factory=list)
    ref: str = ""
    many: bool = False
    done: list = field(default_factory=list)   # status values that DON'T need attention


@dataclass
class DocType:
    name: str
    label: str
    folder: str
    template: str = ""
    templated: bool = True      # False = a non-templated "section" (grows via add-page)
    landing: str = ""           # optional index.md intro text for the section
    sections: list = field(default_factory=list)
    fields: list = field(default_factory=list)
    order: str = ""             # "" derives from templated (date-desc | alpha)
    facet: str = ""             # a field name to group the collection's landing by


@dataclass
class Project:
    profile: str = ""
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
        profile=proj.get("profile", ""),
        managed_nav=proj.get("managed_nav", "ZPLUS_TYPES"),
        deploy_branch=proj.get("deploy_branch", "gh-pages"),
        deploy_remote=proj.get("deploy_remote", ""),
    )
    types = []
    seen = set()
    for t in data.get("type", []):
        for key in ("name", "label", "folder"):
            if key not in t:
                raise ValueError(f"{source}: a [[type]] is missing required '{key}'")
        templated = t.get("templated", True)
        if templated and "template" not in t:
            raise ValueError(f"{source}: templated type '{t['name']}' needs 'template'")
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
        fields = []
        for fdef in t.get("field", []):
            if "name" not in fdef:
                raise ValueError(
                    f"{source}: a field in type '{t['name']}' is missing 'name'")
            ftype = fdef.get("type", "text")
            if ftype not in VALID_FIELD_TYPES:
                raise ValueError(
                    f"{source}: invalid field type '{ftype}' in "
                    f"'{t['name']}/{fdef['name']}'")
            if ftype == "ref" and not fdef.get("ref"):
                raise ValueError(
                    f"{source}: ref field '{t['name']}/{fdef['name']}' "
                    f"needs a 'ref' target type")
            if ftype in ("enum", "multi-enum", "status") and not fdef.get("values"):
                raise ValueError(
                    f"{source}: {ftype} field '{t['name']}/{fdef['name']}' "
                    f"needs 'values'")
            fields.append(Field(name=fdef["name"], type=ftype,
                                required=fdef.get("required", False),
                                values=fdef.get("values", []),
                                ref=fdef.get("ref", ""),
                                many=fdef.get("many", False),
                                done=fdef.get("done", [])))
        order = t.get("order", "")
        if order and order not in VALID_ORDERS:
            raise ValueError(
                f"{source}: invalid order '{order}' for type '{t['name']}' "
                f"(use alpha|date-desc)")
        types.append(DocType(name=t["name"], label=t["label"],
                             folder=t["folder"], template=t.get("template", ""),
                             templated=templated, landing=t.get("landing", ""),
                             sections=sections, fields=fields, order=order,
                             facet=t.get("facet", "")))
    return Manifest(project=project, types=types)


def loads(text, source="<string>"):
    return from_dict(tomllib.loads(text), source=source)


def load(path):
    with open(path, "rb") as f:
        return from_dict(tomllib.load(f), source=str(path))


def available_profiles():
    """Names of bundled profiles (site kinds)."""
    return paths.list_profiles()


def resolve_profile_text(profile_name, managed_nav="ZPLUS_TYPES",
                         deploy_branch="gh-pages"):
    """Compose a self-contained project manifest from a profile's ordered types.

    Reads the profile's `types = [...]` list and concatenates each type's library
    `[[type]]` fragment, in order, under a fresh `[project]` header. The result is
    a standalone `zplus.toml` — the project no longer depends on the library.
    """
    prof = tomllib.loads(paths.read_profile(profile_name))
    type_names = prof.get("types", [])
    library = set(paths.list_types())
    missing = [n for n in type_names if n not in library]
    if missing:
        raise ValueError(f"profile '{profile_name}' references unknown type(s): {missing}")
    header = "\n".join([
        f"# Generated by zplus from the '{profile_name}' profile — self-contained and editable.",
        "# Reorder or add [[type]] blocks here; edit a template's prose in templates/<file>.",
        "",
        "[project]",
        f'profile = "{profile_name}"',
        f'managed_nav = "{managed_nav}"',
        f'deploy_branch = "{deploy_branch}"',
        '# deploy_remote = "https://github.com/<you>/<repo>.git"   # set before `zplus deploy`',
        "",
    ])
    frags = [paths.read_type_fragment(n).strip("\n") for n in type_names]
    return header + "\n" + "\n\n".join(frags) + "\n"


def resolve_profile(profile_name):
    """Resolve a profile into a Manifest (full type defs, in profile order)."""
    return loads(resolve_profile_text(profile_name), source=f"profile:{profile_name}")


def load_default():
    """The default profile's manifest (projecthub)."""
    return resolve_profile("projecthub")
