"""serve / build / deploy — the encrypted static-site pipeline (from build.sh).

Zensical has no in-build encryption, so `build` runs staticrypt over the output.
`deploy` force-pushes the encrypted `site/` to a branch (default gh-pages), with a
fresh throwaway git repo each time so repeat deploys don't collide.
"""
import os
import shutil
import subprocess
import tempfile

from .. import manifest as manifest_mod
from . import nav

_REMEMBER_FIND = (
    r"""find {site} -name '*.html' -exec sed -i """
    r"""'s|<input id="staticrypt-remember" type="checkbox" name="remember" />"""
    r"""|<input id="staticrypt-remember" type="checkbox" name="remember" checked />|' {{}} +"""
)


def load_env(project_dir):
    env = dict(os.environ)
    envp = os.path.join(project_dir, ".env")
    if os.path.exists(envp):
        with open(envp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def serve(project_dir):
    nav.regenerate(project_dir)
    subprocess.call(["bash", "-c",
                     "command -v fuser >/dev/null && fuser -k 8000/tcp >/dev/null 2>&1 || true"])
    os.chdir(project_dir)
    os.execvp("zensical", ["zensical", "serve"])  # replaces process; Ctrl-C to stop


def build(project_dir, env=None):
    env = env or load_env(project_dir)
    password = env.get("SITE_PASSWORD")
    if not password:
        raise SystemExit("error: SITE_PASSWORD not set (put it in .env) — "
                         "refusing to build an unprotected site")
    nav.regenerate(project_dir)
    subprocess.check_call(["zensical", "build", "--clean"], cwd=project_dir)

    site = os.path.join(project_dir, "site")
    enc = tempfile.mkdtemp()
    subprocess.check_call(
        ["npx", "--yes", "staticrypt", site, "-r", "-d", enc, "--remember", "365", "--short",
         "--template-instructions",
         "This site is password protected — enter the password once; your browser will remember it."],
        cwd=project_dir, env={**env, "STATICRYPT_PASSWORD": password})
    shutil.rmtree(site)
    shutil.move(os.path.join(enc, "site"), site)
    subprocess.call(["bash", "-c", _REMEMBER_FIND.format(site=site)])
    print("✔ Built and encrypted → ./site/")


def deploy(project_dir, env=None):
    env = env or load_env(project_dir)
    build(project_dir, env)
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    remote = m.project.deploy_remote
    if not remote:
        raise SystemExit("error: set [project].deploy_remote in zplus.toml before deploy")
    branch = m.project.deploy_branch or "gh-pages"
    site = os.path.join(project_dir, "site")
    open(os.path.join(site, ".nojekyll"), "w").close()
    name = env.get("GIT_NAME", "zplus")
    email = env.get("GIT_EMAIL", "zplus@localhost")
    script = f"""set -e
cd {site}
rm -rf .git
git init -q
git config user.name "{name}"
git config user.email "{email}"
git checkout -q -b {branch}
git add -A
git commit -q -m "Deploy encrypted Zensical build ($(date +%Y-%m-%d))"
git remote add origin {remote}
git push -q -f origin {branch}
"""
    subprocess.check_call(["bash", "-c", script])
    print(f"✔ Deployed → {branch}")
