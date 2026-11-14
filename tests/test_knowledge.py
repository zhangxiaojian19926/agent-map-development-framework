"""Behavior regressions for the portable knowledge helpers. Synthetic data only."""
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill/llm-wiki/scripts"

class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="agent-map-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / ".git").mkdir()
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        self.env.pop("FRAMEWORK_PROJECT_ROOT", None)
        self.env.pop("WIKI_WRITE_CONFIRM", None)

    def run_script(self, name, *args, cwd=None, confirm=False):
        env = dict(self.env)
        if confirm:
            env["WIKI_WRITE_CONFIRM"] = "yes"
        return subprocess.run(["bash", str(SCRIPTS / (name + ".sh")), *map(str,args)],
                              cwd=cwd or self.root, env=env, text=True,
                              capture_output=True, timeout=15)

    def kb(self, name):
        p = self.root / name
        (p / "wiki/sources").mkdir(parents=True)
        (p / "raw/notes").mkdir(parents=True)
        (p / ".wiki-schema.md").write_text("Topic: synthetic\nLanguage: en\n")
        for n in ["index.md", "log.md", "purpose.md"]:
            (p / n).write_text("# Synthetic\n")
        return p

    def aliases(self, items):
        (self.root / "llm-wiki-aliases.json").write_text(json.dumps(items))

    def test_alias_is_relative_to_registry_not_current_directory(self):
        b = self.kb("modules/b/knowledge")
        self.aliases({"b": "modules/b/knowledge"})
        sub = self.root / "nested/deep"
        sub.mkdir(parents=True)
        r = self.run_script("common", "resolve", "b", cwd=sub)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), str(b))

    def test_explicit_alias_not_shadowed_by_current_kb(self):
        a,b = self.kb("a"),self.kb("b")
        self.aliases({"b":"b"})
        r = self.run_script("common","resolve","b",cwd=a)
        self.assertEqual(r.stdout.strip(),str(b))

    def test_registry_search_stops_at_nested_repository_boundary(self):
        self.kb("b")
        self.aliases({"b":"b"})
        nested = self.root / "child"
        (nested / ".git").mkdir(parents=True)
        r = self.run_script("common","resolve","b",cwd=nested)
        self.assertNotEqual(r.returncode,0)

    def test_missing_registry_query_reports_not_configured(self):
        r = self.run_script("query","--all","topic")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("NOT_CONFIGURED",r.stdout)

    def test_multikb_query_from_subdirectory_supports_unicode_and_spaces(self):
        for name in ["mod a/kb","mod b/kb","nested/c/kb"]:
            p=self.kb(name)
            (p/"wiki/sources/page one.md").write_text("中文连接 recovery\n")
        self.aliases({"a":"mod a/kb","b":"mod b/kb","c":"nested/c/kb"})
        r=self.run_script("query","--all","中文连接",cwd=self.root/"mod a")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout.count("page one.md"),3)

    def test_unregistered_explicit_path_works_without_registry(self):
        b=self.kb("b")
        r=self.run_script("common","resolve",b)
        self.assertEqual(r.stdout.strip(),str(b))

    def test_symlink_alias_cannot_escape_project(self):
        with tempfile.TemporaryDirectory(prefix="agent-map-outside-") as outside:
            (Path(outside)/".wiki-schema.md").write_text("Topic: outside")
            (self.root/"escape").symlink_to(outside,target_is_directory=True)
            self.aliases({"bad":"escape"})
            r=self.run_script("common","resolve","bad")
            self.assertNotEqual(r.returncode,0)

    def test_quoted_alias_is_data_not_python_source(self):
        b=self.kb("b")
        alias="owner's [kb]"
        self.aliases({alias:"b"})
        r=self.run_script("common","resolve",alias)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout.strip(),str(b))

    def test_path_like_aliases_are_rejected(self):
        b = self.kb('b')
        for alias in ['.', '..', 'a/b', 'a\\b', '', '/tmp/kb']:
            with self.subTest(alias=alias):
                r = self.run_script('common', 'add-alias', alias, b, confirm=True)
                self.assertNotEqual(r.returncode, 0)
                self.assertFalse((self.root / 'llm-wiki-aliases.json').exists())
                self.aliases({alias: 'b'})
                r = self.run_script('query', '--all', 'topic')
                self.assertNotEqual(r.returncode, 0)
                (self.root / 'llm-wiki-aliases.json').unlink()

    def test_init_requires_per_operation_confirmation(self):
        r=self.run_script("init","new","topic","en")
        self.assertNotEqual(r.returncode,0)
        self.assertFalse((self.root/"new").exists())

    def test_init_english_handles_literal_topic_without_auto_alias(self):
        topic="team's / 中文 & notes"
        r=self.run_script("init","new",topic,"en",confirm=True)
        self.assertEqual(r.returncode,0,r.stderr)
        schema=(self.root/"new/.wiki-schema.md").read_text()
        self.assertIn(topic,schema)
        self.assertNotIn("{{",schema)
        self.assertFalse((self.root/"llm-wiki-aliases.json").exists())

    def test_init_rejects_nonempty_target_without_overwrite(self):
        dest=self.root/"new"
        dest.mkdir()
        (dest/"purpose.md").write_text("KEEP")
        r=self.run_script("init",dest,"topic","zh",confirm=True)
        self.assertNotEqual(r.returncode,0)
        self.assertEqual((dest/"purpose.md").read_text(),"KEEP")

    def test_register_conflict_keeps_existing_alias(self):
        self.kb("a");self.kb("b");self.aliases({"one":"a"})
        r=self.run_script("common","add-alias","one","b",confirm=True)
        self.assertNotEqual(r.returncode,0)
        self.assertEqual(json.loads((self.root/"llm-wiki-aliases.json").read_text()),{"one":"a"})

    def test_ingest_requires_confirmation_and_never_claims_completion(self):
        b=self.kb("b")
        source=self.root/"input.md";source.write_text("synthetic")
        r=self.run_script("ingest",b,source)
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(list((b/"raw").rglob("input.md")))
        r=self.run_script("ingest",b,source,confirm=True)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("PREPARED",r.stdout)
        self.assertIn("pending",r.stdout)
        self.assertEqual(len(list((b/"raw").rglob("*input.md"))),1)
        r=self.run_script("ingest",b,source,confirm=True)
        self.assertNotEqual(r.returncode,0)

    def test_batch_empty_success_and_partial_failure_is_nonzero(self):
        b=self.kb("b")
        folder=self.root/"inputs";folder.mkdir()
        r=self.run_script("batch-ingest",b,folder,confirm=True)
        self.assertEqual(r.returncode,0,r.stderr)
        (folder/"one file.md").write_text("one")
        r=self.run_script("batch-ingest",b,folder,confirm=True)
        self.assertEqual(r.returncode,0,r.stderr)
        (folder/"two.md").write_text("two")
        r=self.run_script("batch-ingest",b,folder,confirm=True)
        self.assertNotEqual(r.returncode,0)
        self.assertIn("failed",r.stdout)
        self.assertEqual(len(list((b/"raw").rglob("*.md"))),2)

    def test_graph_and_status_are_readonly(self):
        b=self.kb("b")
        (b/"wiki/sources/A.md").write_text("---\ntype: source\ncreated: 2026-01-01\n---\n[[B]]")
        (b/"wiki/sources/B.md").write_text("---\ntype: source\ncreated: 2026-01-01\n---\nB")
        before={str(p):p.read_bytes() for p in b.rglob("*") if p.is_file()}
        for command in ["status","graph","lint"]:
            r=self.run_script(command,b)
            self.assertEqual(r.returncode,0,(command,r.stdout,r.stderr))
        self.assertEqual(before,{str(p):p.read_bytes() for p in b.rglob("*") if p.is_file()})

    def test_strict_lint_rejects_missing_metadata(self):
        b=self.kb("b")
        (b/"wiki/sources/bad.md").write_text("no metadata")
        r=self.run_script("lint",b,"--strict")
        self.assertNotEqual(r.returncode,0)

    def test_delete_only_plans_and_rejects_escape(self):
        b=self.kb("b")
        f=b/"raw/notes/a.md";f.write_text("keep")
        r=self.run_script("delete",b,"notes/a.md")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("PLAN_ONLY",r.stdout)
        self.assertTrue(f.exists())
        outside=self.root/"outside.md";outside.write_text("keep")
        r=self.run_script("delete",b,"../../outside.md")
        self.assertNotEqual(r.returncode,0)
        self.assertTrue(outside.exists())

    def test_digest_and_crystallize_are_explicit_plans(self):
        b=self.kb("b")
        r=self.run_script("digest",b,"topic")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("PLAN_ONLY",r.stdout)
        f=self.root/"session.md";f.write_text("synthetic")
        r=self.run_script("crystallize",b,f,"lesson")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("INFERRED",r.stdout)
        self.assertFalse(list((b/"wiki").rglob("*.md")))

    def test_init_creates_engineering_shell_without_pages(self):
        r = self.run_script("init", "new", "demo", "zh", confirm=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        kb = self.root / "new"
        for folder in ("wiki/sources/designs", "wiki/sources/verifications", "wiki/entities/modules",
                       "wiki/topics/requirements", "wiki/topics/plans", "wiki/topics/problems",
                       "wiki/topics/constraints", "wiki/topics/concepts", "wiki/synthesis/decisions"):
            self.assertTrue((kb / folder / ".gitkeep").is_file(), folder)
        self.assertIn("ingestion", r.stdout)
        self.assertFalse(list((kb / "wiki").rglob("*.md")))
        status = json.loads(self.run_script("status", kb).stdout)
        self.assertEqual(status["shell"], "READY")
        self.assertEqual(status["ingestion"], "EMPTY")

    def page(self, kb, relative, body):
        path = kb / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def problem_page(self, applies="请求走了 X 分支且 Y 为空", not_applies="Y 非空的请求"):
        return ("---\ntype: problem\nartifact_kind: problem\ncreated: 2026-01-01\n"
                "confidence: EXTRACTED\nstatus: verified\n"
                "applies_when: %s\nnot_applicable_when: %s\n---\n\n结论\n" % (applies, not_applies))

    def concept_page(self, applies="本工程内指该术语时"):
        return ("---\ntype: concept\nartifact_kind: concept\ncreated: 2026-01-01\n"
                "confidence: EXTRACTED\nstatus: approved\n"
                "applies_when: %s\n---\n\n扩展语义\n" % applies)

    def test_strict_lint_requires_applicability_on_problem_pages(self):
        b = self.kb("b")
        self.page(b, "wiki/topics/problems/no-when.md",
                  "---\ntype: problem\nartifact_kind: problem\ncreated: 2026-01-01\n"
                  "not_applicable_when: Y 非空\n---\n\n结论\n")
        r = self.run_script("lint", b, "--strict")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("missing applicability field: applies_when", r.stdout)

    def test_strict_lint_requires_a_not_applicable_condition_on_problem_pages(self):
        b = self.kb("b")
        self.page(b, "wiki/topics/problems/no-not-when.md",
                  "---\ntype: problem\nartifact_kind: problem\ncreated: 2026-01-01\n"
                  "applies_when: X 分支\n---\n\n结论\n")
        r = self.run_script("lint", b, "--strict")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("missing applicability field: not_applicable_when", r.stdout)

    def test_strict_lint_requires_applicability_on_concept_pages(self):
        b = self.kb("b")
        self.page(b, "wiki/topics/concepts/no-when.md",
                  "---\ntype: concept\nartifact_kind: concept\ncreated: 2026-01-01\n---\n\n扩展语义\n")
        r = self.run_script("lint", b, "--strict")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("missing applicability field: applies_when", r.stdout)

    def test_strict_lint_leaves_requirement_pages_alone(self):
        b = self.kb("b")
        self.page(b, "wiki/topics/requirements/legacy.md",
                  "---\ntype: requirement\nartifact_kind: requirement\ncreated: 2026-01-01\n---\n\n需求\n")
        r = self.run_script("lint", b, "--strict")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_strict_lint_keeps_checking_the_format_of_a_requirement_page_field(self):
        b = self.kb("b")
        self.page(b, "wiki/topics/requirements/legacy.md",
                  "---\ntype: requirement\nartifact_kind: requirement\ncreated: 2026-01-01\n"
                  "applies_when: {{APPLIES_WHEN}}\n---\n\n需求\n")
        r = self.run_script("lint", b, "--strict")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_strict_lint_treats_an_unfilled_placeholder_as_missing(self):
        b = self.kb("b")
        self.page(b, "wiki/topics/problems/placeholder.md",
                  "---\ntype: problem\nartifact_kind: problem\ncreated: 2026-01-01\n"
                  "applies_when: {{APPLIES_WHEN}}\nnot_applicable_when: Y 非空\n---\n\n结论\n")
        r = self.run_script("lint", b, "--strict")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("missing applicability field: applies_when", r.stdout)

    def test_strict_lint_accepts_pages_that_declare_their_conditions(self):
        b = self.kb("b")
        self.page(b, "wiki/topics/problems/good.md", self.problem_page())
        self.page(b, "wiki/topics/concepts/good.md", self.concept_page())
        r = self.run_script("lint", b, "--strict")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_concept_page_and_glossary_do_not_duplicate_the_definition(self):
        template = (ROOT / "skill/llm-wiki/templates/engineering-template.md").read_text(encoding="utf-8")
        self.assertIn("artifact_kind", template)
        self.assertIn("concept", template)
        self.assertIn("does not restate the definition", template)
        self.assertIn("applies_when", template)

    def test_the_glossary_boundary_is_declared_in_one_place(self):
        policy = (ROOT / "docs/framework/knowledge-policy.md").read_text(encoding="utf-8")
        layer = (ROOT / "skill/matt-pocock/domain-modeling/framework-rules.md").read_text(encoding="utf-8")
        self.assertIn("KB-GLOSSARY-SPLIT", policy)
        self.assertIn("KB-GLOSSARY-SPLIT", layer)
        self.assertNotIn("The knowledge base does not hold it", layer)
        self.assertNotIn("术语表与决策记录不属于知识库内容", policy)

    def test_the_schema_template_and_the_project_schema_agree(self):
        template = (ROOT / "skill/llm-wiki/templates/schema-template.md").read_text(encoding="utf-8")
        instance = (ROOT / "knowledge/project/.wiki-schema.md").read_text(encoding="utf-8")

        def body(text):
            keep = [line for line in text.splitlines()
                    if not line.startswith(("Topic:", "Language:", "Created:"))]
            return "\n".join(keep)

        self.assertEqual(body(template), body(instance))

    def test_the_page_status_vocabulary_matches_the_schema(self):
        loader = importlib.machinery.SourceFileLoader("wikimod", str(SCRIPTS / "wiki.py"))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        schema = (ROOT / "skill/llm-wiki/templates/schema-template.md").read_text(encoding="utf-8")
        line = next(l for l in schema.splitlines() if "status is " in l)
        declared = [s.strip() for s in line.split("status is ", 1)[1].split(".")[0].split(",")]
        if declared[-1].startswith("or "):
            declared[-1] = declared[-1][3:].strip()
        self.assertEqual(set(declared), set(module.PAGE_STATUSES))

    def test_strict_lint_reports_an_unknown_page_status(self):
        b = self.kb("b")
        self.page(b, "wiki/topics/problems/bad-status.md",
                  "---\ntype: problem\nartifact_kind: problem\ncreated: 2026-01-01\n"
                  "status: totally-made-up\napplies_when: X\nnot_applicable_when: Y\n---\n\n结论\n")
        r = self.run_script("lint", b, "--strict")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not a known page status", r.stdout)

    def test_the_framework_status_dictionary_does_not_hold_page_statuses(self):
        guide = (ROOT / "docs/guide/framework-model.md").read_text(encoding="utf-8")
        block = guide.split("<!-- status-dictionary:start -->", 1)[1].split("<!-- status-dictionary:end -->", 1)[0]
        for status in ("approved", "verified", "temporary-workaround", "superseded", "retracted", "needs-review"):
            self.assertNotIn("`%s`" % status, block)

    def test_chinese_fragment_matches_without_the_whole_phrase(self):
        b = self.kb("b")
        (b / "wiki/topics").mkdir(parents=True)
        (b / "wiki/topics/link.md").write_text("# 连接\n只写了连接。\n")
        (b / "wiki/topics/other.md").write_text("# 其他\n没有目标词。\n")
        r = self.run_script("query", b, "中文连接")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("link.md", r.stdout)
        self.assertNotIn("other.md", r.stdout)

    def test_lint_reports_raw_that_has_no_page(self):
        b = self.kb("b")
        (b / "raw/notes/orphan.md").write_text("source")
        r = self.run_script("lint", b)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("raw without knowledge page", r.stdout)
        (b / "wiki/sources/note.md").write_text("see orphan.md\n")
        r = self.run_script("lint", b)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

if __name__ == "__main__":
    unittest.main()
