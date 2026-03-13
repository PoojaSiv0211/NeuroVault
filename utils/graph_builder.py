import os
import networkx as nx
from pyvis.network import Network


def get_node_color(label: str) -> str:
    label = label.lower()

    if "learning" in label or "neural" in label or "ai" in label:
        return "#4F8EF7"  # blue

    if "vision" in label or "science" in label:
        return "#4CAF50"  # green

    if "python" in label or "tensorflow" in label:
        return "#FF9800"  # orange

    return "#90A4AE"  # default grey


def build_graph(concepts, relations, output_path="output/graph.html"):
    os.makedirs("output", exist_ok=True)

    G = nx.DiGraph()

    related_nodes = set()
    for subject, relation, obj in relations:
        related_nodes.add(subject)
        related_nodes.add(obj)

    filtered_concepts = [c for c in concepts if c in related_nodes]

    for concept in filtered_concepts:
        G.add_node(concept)

    for subject, relation, obj in relations:
        G.add_node(subject)
        G.add_node(obj)
        G.add_edge(subject, obj, label=relation)

    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#ffffff",
        font_color="black"
    )

    net.barnes_hut()
    net.toggle_physics(True)

    for node in G.nodes():
        net.add_node(
            node,
            label=node,
            title=node,
            color=get_node_color(node)
        )

    for source, target, data in G.edges(data=True):
        net.add_edge(
            source,
            target,
            label=data.get("label", "")
        )

    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -20000,
          "centralGravity": 0.3,
          "springLength": 120,
          "springConstant": 0.04,
          "damping": 0.09
        },
        "minVelocity": 0.75
      },
      "nodes": {
        "shape": "dot",
        "size": 18,
        "font": {
          "size": 18,
          "face": "arial"
        },
        "borderWidth": 2
      },
      "edges": {
        "color": {
          "color": "#848484",
          "highlight": "#2B7CE9"
        },
        "smooth": {
          "enabled": true,
          "type": "dynamic"
        },
        "arrows": {
          "to": {
            "enabled": true
          }
        },
        "font": {
          "size": 12,
          "align": "middle"
        }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)

    net.write_html(output_path)
    return output_path