from datetime import date
from shlex import quote

import invoke

PROJECT_DIR = "postal_address"

CBLUE = "\33[34m"
CEND = "\33[0m"
CBOLD = "\33[1m"


def log(msg: str, section_name: str = "release") -> None:
    print(f"{CBLUE}[{section_name}]{CEND} {msg}")


def log_section(section_name: str) -> None:
    print(f"{CBLUE}{CBOLD}[{section_name}]{CEND}")


@invoke.task
def lint(ctx, changes=False):
    path = PROJECT_DIR
    if changes:
        path = f"$(git diff --name-only --diff-filter=d {PROJECT_DIR})"

    log_section("mypy")
    ctx.run(f"poetry run mypy {path}", pty=True)
    log_section("flakeheaven")
    ctx.run(f"poetry run flakeheaven lint {path}", pty=True)


@invoke.task
def format(ctx, changes=False):
    path = PROJECT_DIR
    if changes:
        path = f"$(git diff --name-only --diff-filter=d {PROJECT_DIR})"

    log_section("autoflake")
    ctx.run(
        f"poetry run autoflake -ri --remove-all-unused-imports {path}",
        pty=True,
    )
    log_section("isort")
    ctx.run(f"poetry run isort --atomic {path}", pty=True)
    log_section("black")
    ctx.run(f"poetry run black {path}", pty=True)


@invoke.task
def test(ctx, scope=""):
    if not scope:
        cov = "--cov"
    else:
        cov = f"--cov={scope}"
    ctx.run(f"poetry run pytest --color=yes {scope} {cov}")


@invoke.task
def get_current_version(ctx):
    return ctx.run("poetry version --short", hide=True).stdout.strip()


@invoke.task
def bump_version(ctx, bump, dry_run=False):
    """Bump the project's version."""
    current_version = get_current_version(ctx)
    current_version_tuple = tuple(current_version.split("."))

    today = date.today()
    new_version_tuple = (str(today.year), str(today.month), str(today.day))

    if current_version_tuple[:3] == new_version_tuple:
        if len(current_version_tuple) == 3:
            new_version_tuple = (*new_version_tuple, "1")
        else:
            new_version_tuple = (*new_version_tuple, str(int(current_version_tuple[3]) + 1))

    new_version = ".".join(new_version_tuple)

    cmd = f"poetry version {new_version}"
    if dry_run:
        log(f"Would run '{cmd}' and stage pyproject.toml")
    else:
        ctx.run(cmd)
        ctx.run("git add pyproject.toml")

    return new_version


@invoke.task
def release(ctx, dry_run=False):
    version = bump_version(ctx, dry_run=dry_run)

    tag = f"{version}"
    tag_message = f"Version {tag}"
    commit_message = quote(f"Release {tag}")

    # Commit, tag and push
    if dry_run:
        log(f"Would commit with message: {commit_message}")
        log(f"Generated tag content:\n{tag_message}")
        log("Would push tags")
    else:
        log("Commit all staged files")
        ctx.run(f"git commit -m {commit_message}")

        log("Tag commit")
        ctx.run(f"git tag -a {tag} -m {quote(tag_message)}")

        log("Push commit and tag")
        ctx.run("git push origin HEAD:master")
        ctx.run("git push --tags")
