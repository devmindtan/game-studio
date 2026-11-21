"""Unit tests of gdgraph (see README.md). Run with the venv next to it:

    tools/gdgraph/.venv/bin/python -m unittest discover -s tools/gdgraph -p 'test_gdgraph.py'
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gdgraph  # noqa: E402


def make_game(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp(prefix="gdgraph-test-"))
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


def node(graph: dict, label: str) -> dict:
    hits = [n for n in graph["nodes"] if n["label"] == label]
    assert len(hits) == 1, f"expected one {label!r}, got {[h['source_file'] for h in hits]}"
    return hits[0]


def edges(graph: dict, relation: str) -> set[tuple[str, str]]:
    by_id = {n["id"]: n["label"] for n in graph["nodes"]}
    return {
        (by_id[link["source"]], by_id[link["target"]])
        for link in graph["links"]
        if link["relation"] == relation
    }


class GdgraphTest(unittest.TestCase):
    def test_nodes_carry_file_and_line(self):
        root = make_game({
            "src/actor.gd": (
                "class_name Actor\n"
                "extends RefCounted\n"
                "\n"
                "const MAX_HP := 10\n"
                "\n"
                "func hit() -> void:\n"
                "\tpass\n"
            ),
        })
        graph = gdgraph.build(root)
        actor = node(graph, "Actor")
        self.assertEqual(actor["source_file"], "src/actor.gd")
        self.assertEqual(actor["source_location"], "L1")
        hit = node(graph, "hit()")
        self.assertEqual(hit["source_location"], "L6")
        self.assertIn(("actor.gd", "Actor"), edges(graph, "contains"))
        self.assertIn(("Actor", "hit()"), edges(graph, "contains"))
        self.assertIn(("Actor", "RefCounted"), edges(graph, "extends"))
        self.assertIn(("Actor", "MAX_HP"), edges(graph, "contains"))

    def test_typed_variable_call_resolves_across_files(self):
        root = make_game({
            "src/target.gd": "class_name Target\n\nfunc hit(dmg: int) -> void:\n\tpass\n",
            "src/shooter.gd": (
                "class_name Shooter\n"
                "\n"
                "var target := Target.new()\n"
                "\n"
                "func fire() -> void:\n"
                "\ttarget.hit(1)\n"
            ),
        })
        graph = gdgraph.build(root)
        self.assertIn(("fire()", "hit()"), edges(graph, "calls"))

    def test_autoload_call_resolves_through_project_godot(self):
        root = make_game({
            "project.godot": '[autoload]\n\nAudio="*res://src/audio/sound.gd"\n',
            "src/audio/sound.gd": "extends Node\n\nfunc play(id: String) -> void:\n\tpass\n",
            "src/run/run.gd": "func _ready() -> void:\n\tAudio.play(\"run\")\n",
        })
        graph = gdgraph.build(root)
        self.assertIn(("_ready()", "play()"), edges(graph, "calls"))

    def test_same_file_and_unique_project_names_resolve(self):
        root = make_game({
            "src/a.gd": "func helper() -> void:\n\tpass\n\nfunc caller() -> void:\n\thelper()\n",
            "src/b.gd": "func unique() -> void:\n\tpass\n",
            "src/c.gd": "func other() -> void:\n\tunique()\n",
        })
        graph = gdgraph.build(root)
        self.assertIn(("caller()", "helper()"), edges(graph, "calls"))
        self.assertIn(("other()", "unique()"), edges(graph, "calls"))

    def test_builtins_and_unknown_receivers_are_not_guessed(self):
        root = make_game({
            "src/a.gd": (
                "func caller(items: Array) -> void:\n"
                "\titems.append(1)\n"
                "\tprint(sqrt(4.0))\n"
            ),
        })
        graph = gdgraph.build(root)
        self.assertEqual(edges(graph, "calls"), set())

    def test_every_link_points_at_a_node_and_calls_keep_the_site(self):
        root = make_game({
            "src/a.gd": "func helper() -> void:\n\tpass\n\nfunc caller() -> void:\n\thelper()\n",
        })
        graph = gdgraph.build(root)
        ids = {n["id"] for n in graph["nodes"]}
        self.assertEqual(len(ids), len(graph["nodes"]))
        for link in graph["links"]:
            self.assertIn(link["source"], ids)
            self.assertIn(link["target"], ids)
        calls = [link for link in graph["links"] if link["relation"] == "calls"]
        self.assertEqual(calls[0]["source_file"], "src/a.gd")
        self.assertEqual(calls[0]["source_location"], "L5")

    def test_graph_loads_the_way_graphify_reads_it(self):
        root = make_game({"src/a.gd": "func f() -> void:\n\tpass\n"})
        graph = gdgraph.build(root)
        plain = json.loads(json.dumps(graph))
        self.assertTrue(plain["directed"])
        self.assertIn("links", plain)
        self.assertIsInstance(plain["nodes"], list)
        for n in plain["nodes"]:
            self.assertIn("id", n)
            self.assertIn("label", n)


if __name__ == "__main__":
    unittest.main()
