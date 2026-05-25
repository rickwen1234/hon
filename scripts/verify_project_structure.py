"""Verify the refactored project structure."""

from __future__ import annotations

import ast
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src", "network_science_project")

REQUIRED_DIRS = [
    "configs",
    "src/network_science_project/hon",
    "src/network_science_project/multilayer",
    "src/network_science_project/cascade",
    "src/network_science_project/visualization",
    "src/network_science_project/experiments",
    "src/network_science_project/cli",
    "src/network_science_project/utils",
    "scripts",
    "tests",
    "docs",
    "examples",
    "outputs",
]
REQUIRED_DOCS = [
    "architecture.md",
    "data_formats.md",
    "hon_and_cog_hon.md",
    "multilayer_interface.md",
    "peng_cascade.md",
    "visualization.md",
    "migration_guide.md",
    "refactor_audit.md",
    "refactor_report.md",
]
REQUIRED_TESTS = [
    "test_import_boundaries.py",
    "test_hon_rule_extraction.py",
    "test_temporal_weighting.py",
    "test_multilayer_core.py",
    "test_multilayer_generators.py",
    "test_dependencies.py",
    "test_simplices.py",
    "test_peng_cascade.py",
    "test_io_roundtrip.py",
    "test_experiments_full.py",
]
REQUIRED_COMMANDS = [
    "ns-build-hon",
    "ns-build-memory-hon",
    "ns-build-multilayer",
    "ns-run-peng-cascade",
    "ns-run-full-pipeline",
    "ns-visualize-multilayer",
    "ns-summarize-results",
]
FORBIDDEN = {
    "hon": {"network_science_project.multilayer", "network_science_project.cascade", "network_science_project.visualization"},
    "multilayer": {"network_science_project.hon", "network_science_project.cascade", "network_science_project.visualization"},
    "cascade": {"network_science_project.hon", "network_science_project.visualization"},
}


def imports_for(path: str) -> set[str]:
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def check_forbidden_imports() -> list[str]:
    failures = []
    for package, forbidden in FORBIDDEN.items():
        root = os.path.join(SRC, package)
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if filename.endswith(".py"):
                    path = os.path.join(dirpath, filename)
                    for module in imports_for(path):
                        if any(module == bad or module.startswith(bad + ".") for bad in forbidden):
                            failures.append("forbidden import {0} in {1}".format(module, path))
    return failures


def check_scripts() -> list[str]:
    failures = []
    for filename in os.listdir(os.path.join(ROOT, "scripts")):
        if not filename.endswith(".py") or filename == "verify_project_structure.py":
            continue
        path = os.path.join(ROOT, "scripts", filename)
        with open(path, encoding="utf-8") as handle:
            lines = [line for line in handle if line.strip() and not line.strip().startswith("#")]
        if len(lines) > 35:
            failures.append("script is not thin: {0}".format(filename))
        if not any(module.startswith("network_science_project.cli") for module in imports_for(path)):
            failures.append("script does not dispatch to cli: {0}".format(filename))
    return failures


def main() -> int:
    failures = []
    failures += ["missing folder: " + path for path in REQUIRED_DIRS if not os.path.isdir(os.path.join(ROOT, path))]
    failures += ["missing doc: " + name for name in REQUIRED_DOCS if not os.path.exists(os.path.join(ROOT, "docs", name))]
    failures += ["missing test: " + name for name in REQUIRED_TESTS if not os.path.exists(os.path.join(ROOT, "tests", name))]
    failures += check_forbidden_imports()
    failures += check_scripts()
    gitignore = open(os.path.join(ROOT, ".gitignore"), encoding="utf-8").read() if os.path.exists(os.path.join(ROOT, ".gitignore")) else ""
    if "outputs/*" not in gitignore or "!outputs/.gitkeep" not in gitignore:
        failures.append("outputs/ is not gitignored except .gitkeep")
    pyproject = open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read()
    for command in REQUIRED_COMMANDS:
        if command not in pyproject:
            failures.append("missing pyproject command: " + command)
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read().lower()
    if "quick start" not in readme or "ns-build-multilayer" not in readme:
        failures.append("README lacks quick-start commands")
    for name in ["toy_sequences.csv", "toy_timestamped_sequences.csv", "toy_layer_A_edges.csv", "toy_layer_B_edges.csv", "toy_dependencies.csv", "toy_triangles.csv"]:
        if not os.path.exists(os.path.join(ROOT, "examples", name)):
            failures.append("missing example: " + name)
    if failures:
        for failure in failures:
            print("FAIL: " + failure)
        return 1
    print("PASS: project structure is clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
