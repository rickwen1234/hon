from __future__ import annotations

import ast
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PACKAGE = os.path.join(ROOT, "src", "network_science_project")


FORBIDDEN = {
    "hon": {"network_science_project.multilayer", "network_science_project.cascade", "network_science_project.visualization"},
    "multilayer": {"network_science_project.hon", "network_science_project.cascade", "network_science_project.visualization"},
    "cascade": {"network_science_project.hon", "network_science_project.visualization"},
    "visualization": {"network_science_project.cascade.simulation", "network_science_project.experiments.run_peng_cascade"},
}


def imported_modules(path: str) -> set[str]:
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


class ImportBoundaryTests(unittest.TestCase):
    def test_forbidden_package_imports(self) -> None:
        violations = []
        for package, forbidden in FORBIDDEN.items():
            package_dir = os.path.join(SRC_PACKAGE, package)
            for dirpath, _, filenames in os.walk(package_dir):
                for filename in filenames:
                    if not filename.endswith(".py"):
                        continue
                    path = os.path.join(dirpath, filename)
                    imports = imported_modules(path)
                    for module in imports:
                        if any(module == bad or module.startswith(bad + ".") for bad in forbidden):
                            violations.append((path, module))
        self.assertEqual(violations, [])

    def test_scripts_are_thin_wrappers(self) -> None:
        scripts_dir = os.path.join(ROOT, "scripts")
        violations = []
        for filename in os.listdir(scripts_dir):
            if not filename.endswith(".py") or filename == "verify_project_structure.py":
                continue
            path = os.path.join(scripts_dir, filename)
            with open(path, encoding="utf-8") as handle:
                lines = [line for line in handle.readlines() if line.strip() and not line.strip().startswith("#")]
            imports = imported_modules(path)
            if len(lines) > 35:
                violations.append((path, "too many lines"))
            if not any(module.startswith("network_science_project.cli") for module in imports):
                violations.append((path, "does not import cli"))
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
