from __future__ import annotations
from typing import Dict, Any, List

from docutils import nodes

import sphinx
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


class EventInputNode(nodes.General, nodes.Element):
    pass


def visit_event_input_node(self, node: EventInputNode) -> None:
    self.body.append(
        self.starttag(
            node,
            "input",
            empty=True,
            type="text",
            value=node.rawsource,
            disabled="",
            CLASS=node.get("class", ""),
        )
    )


def depart_event_input_node(self, node: EventInputNode) -> None:
    pass


def event_to_xref_node(event_name: str) -> addnodes.pending_xref:
    xref_node = addnodes.pending_xref(
        "",
        refdomain="py",
        reftype="func",
        reftarget=f"discord.{event_name}",
        modname=None,
        classname=None,
        objtype=None,
    )
    xref_node += nodes.literal(text=event_name)
    return xref_node


class EventDirective(SphinxDirective):
    has_content = True

    def run(self) -> List[nodes.Node]:
        if not self.content:
            return []

        events: List[str] = self.content[0].split()
        if not events:
            return []

        paragraph_node = nodes.paragraph()

        if len(events) == 1:
            paragraph_node += nodes.emphasis(text="This function can trigger the ")
            paragraph_node += event_to_xref_node(events[0])
            paragraph_node += nodes.Text(" event.")
        else:
            paragraph_node += nodes.emphasis(text="This function can trigger the following events: ")
            for i, event in enumerate(events):
                paragraph_node += event_to_xref_node(event)
                if i < len(events) - 1:
                    paragraph_node += nodes.Text(", ")

        return [paragraph_node]


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_node(EventInputNode, html=(visit_event_input_node, depart_event_input_node))
    app.add_directive("event", EventDirective)
    return {
        "version": sphinx.__display_version__,
        "parallel_read_safe": True,
    }
