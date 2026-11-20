import tempfile
import unittest
from pathlib import Path

from codeowners import CodeownersResolver, build_codeowners
from gates import build_ownership, detect_ownership
from policy import OwnershipSource


class CodeownersTests(unittest.TestCase):
    def resolver(self, text):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "CODEOWNERS"
        path.write_text(text)
        return CodeownersResolver(path)

    def test_langfuse_rules_and_unowned_paths(self):
        resolver = self.resolver("# * @langfuse/maintainers\n/web/.storybook/ @bezbac\n**/eslint.config.mjs @bezbac\n/packages/langfuse-skills/ @LysanderKie @bezbac\n")
        self.assertEqual(resolver.owners("web/.storybook/main.ts"), {"@bezbac"})
        self.assertEqual(resolver.owners("eslint.config.mjs"), {"@bezbac"})
        self.assertEqual(resolver.owners("web/eslint.config.mjs"), {"@bezbac"})
        self.assertEqual(resolver.owners("packages/langfuse-skills/a.md"), {"@LysanderKie", "@bezbac"})
        self.assertEqual(resolver.owners("worker/src/main.ts"), set())
        self.assertEqual(resolver.owners("nested/web/.storybook/main.ts"), set())

    def test_last_match_ownerless_and_segment_boundaries(self):
        resolver = self.resolver("* @all\n/docs/ @docs\n/docs/private/\n*.js @js\nsrc/?.ts @ts # context\n")
        self.assertEqual(resolver.owners("docs/a.md"), {"@docs"})
        self.assertEqual(resolver.owners("docs/private/a.md"), set())
        self.assertEqual(resolver.owners("docs-other/a.md"), {"@all"})
        self.assertEqual(resolver.owners("nested/a.js"), {"@js"})
        self.assertEqual(resolver.owners("src/a.ts"), {"@ts"})
        self.assertEqual(resolver.owners("src/ab.ts"), {"@all"})

    def test_empty_and_invalid_fail_closed(self):
        for text in ["", "# inactive\n", "[ab] @owner", "!foo @owner", "foo invalid-owner", "a\\ b @owner", "* @org/team"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.resolver(text)

    def test_missing_and_escaping_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                build_codeowners(root, OwnershipSource(format="codeowners", path="CODEOWNERS"))
            with self.assertRaises(ValueError):
                build_codeowners(root, OwnershipSource(format="codeowners", path="../CODEOWNERS"))

    def test_registry_hook(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CODEOWNERS").write_text("* @bezbac\n")
            resolvers = build_ownership(root, (OwnershipSource(format="codeowners", path="CODEOWNERS"),))
            ownership = detect_ownership(["web/package.json"], resolvers)
            self.assertEqual(ownership["individuals"], ["@bezbac"])
            self.assertEqual(ownership["teams"], [])


if __name__ == "__main__":
    unittest.main()
