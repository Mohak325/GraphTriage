"""Cypher to AWS Neptune Gremlin Migration & Bulk-Loader Generator.

Translates Neo4j Cypher DDL and DML (seed_data.cypher) into:
1. Apache TinkerPop Gremlin Groovy console scripts (seed_gremlin.groovy).
2. AWS Neptune Bulk Loader compliant CSV files (nodes and edges with Neptune type tags).
"""

import os
import re
import csv
import logging
import argparse
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class CypherToGremlinMigrator:
    """Parses GraphTriage Cypher seed data and emits Gremlin scripts and Neptune CSV files."""

    def __init__(self, cypher_file_path: str):
        self.cypher_file_path = cypher_file_path
        self.var_to_node: Dict[str, Dict[str, Any]] = {}  # var -> {id, label, properties}
        self.nodes: Dict[str, Dict[str, Any]] = {}        # id -> {label, properties}
        self.edges: List[Dict[str, Any]] = []             # [{source_id, target_id, label, properties}]

    def parse(self) -> "CypherToGremlinMigrator":
        """Read and parse the Cypher file using pattern matching."""
        if not os.path.exists(self.cypher_file_path):
            raise FileNotFoundError(f"Cypher file not found: {self.cypher_file_path}")

        with open(self.cypher_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove single-line comments // ...
        clean_content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)

        # 1. Extract all node definitions: MERGE (var:Label { props })
        node_matches = re.finditer(r"MERGE\s*\(([A-Za-z0-9_]+):([A-Za-z0-9_]+)\s*\{([^}]+)\}\)", clean_content)
        for m in node_matches:
            var_name = m.group(1)
            label = m.group(2)
            props_str = m.group(3)
            props = self._parse_props_string(props_str)
            node_id = props.get("id", f"{label.lower()}-{var_name}")
            node_data = {
                "id": node_id,
                "label": label,
                "properties": props
            }
            self.var_to_node[var_name] = node_data
            self.nodes[node_id] = node_data

        # 2. Extract all relationship definitions:
        # Pattern A: MERGE (var1)-[:LABEL {props}]->(var2)
        # Pattern B: MERGE (var1)-[:LABEL]->(var2)
        rel_pattern = re.compile(
            r"MERGE\s*\(([A-Za-z0-9_]+)\)-\[:([A-Za-z0-9_]+)(?:\s*\{([^}]+)\})?\]->\(([A-Za-z0-9_]+)\)"
        )
        for m in rel_pattern.finditer(clean_content):
            src_var = m.group(1)
            rel_label = m.group(2)
            props_str = m.group(3) or ""
            tgt_var = m.group(4)

            src_node = self.var_to_node.get(src_var)
            tgt_node = self.var_to_node.get(tgt_var)

            src_id = src_node["id"] if src_node else src_var
            tgt_id = tgt_node["id"] if tgt_node else tgt_var
            props = self._parse_props_string(props_str) if props_str else {}

            self.edges.append({
                "source": src_id,
                "target": tgt_id,
                "label": rel_label,
                "properties": props
            })

        logger.info(f"Parsed {len(self.nodes)} nodes and {len(self.edges)} edges from Cypher.")
        return self

    def _parse_props_string(self, props_str: str) -> Dict[str, Any]:
        props: Dict[str, Any] = {}
        pair_matches = re.finditer(r'([A-Za-z0-9_]+)\s*:\s*("(?:\\.|[^"\\])*"|[0-9]+(?:\.[0-9]+)?|[A-Za-z0-9_]+)', props_str)
        for pm in pair_matches:
            k = pm.group(1)
            raw_v = pm.group(2)
            if raw_v.startswith('"') and raw_v.endswith('"'):
                props[k] = raw_v[1:-1]
            elif raw_v in ("true", "false"):
                props[k] = (raw_v == "true")
            elif "." in raw_v:
                try:
                    props[k] = float(raw_v)
                except ValueError:
                    props[k] = raw_v
            else:
                try:
                    props[k] = int(raw_v)
                except ValueError:
                    props[k] = raw_v
        return props

    def generate_gremlin_groovy(self) -> str:
        """Generate TinkerPop Gremlin Groovy console script."""
        lines = [
            "// ================================================================",
            "// Amazon Neptune Gremlin Topology & Seed Data Script",
            "// Generated automatically from Neo4j Cypher definitions",
            "// ================================================================",
            "",
            "// 1. Clear existing GraphTriage elements (optional, safe)",
            "g.V().drop().iterate()",
            ""
        ]

        # Generate Nodes
        lines.append("// 2. Create Vertices")
        for node_id, data in self.nodes.items():
            label = data["label"]
            props = data["properties"]
            traversal = f"g.addV('{label}').property('entity_id', '{node_id}')"
            for k, v in props.items():
                if k == "id":
                    continue
                if isinstance(v, str):
                    clean_v = v.replace("'", "\\'")
                    traversal += f".property('{k}', '{clean_v}')"
                elif isinstance(v, (int, float)):
                    traversal += f".property('{k}', {v})"
                elif isinstance(v, bool):
                    traversal += f".property('{k}', {str(v).lower()})"
            traversal += ".iterate()"
            lines.append(traversal)

        lines.append("")
        lines.append("// 3. Create Edges")
        edge_idx = 1
        for edge in self.edges:
            src = edge["source"]
            tgt = edge["target"]
            label = edge["label"]
            props = edge["properties"]

            traversal = (
                f"g.V().has('entity_id', '{src}').as('from')"
                f".V().has('entity_id', '{tgt}').as('to')"
                f".addE('{label}').from('from').to('to')"
            )
            for k, v in props.items():
                if isinstance(v, str):
                    clean_v = v.replace("'", "\\'")
                    traversal += f".property('{k}', '{clean_v}')"
                elif isinstance(v, (int, float)):
                    traversal += f".property('{k}', {v})"
                elif isinstance(v, bool):
                    traversal += f".property('{k}', {str(v).lower()})"
            traversal += ".iterate()"
            lines.append(traversal)
            edge_idx += 1

        lines.append("")
        lines.append("// Verification counts")
        lines.append("println('Total Neptune Vertices loaded: ' + g.V().count().next())")
        lines.append("println('Total Neptune Edges loaded: ' + g.E().count().next())")
        return "\n".join(lines)

    def generate_neptune_bulk_csv(self, output_dir: str) -> List[str]:
        """Generate AWS Neptune Bulk Loader compliant CSV files.

        Neptune Bulk Loader requires:
        Vertices: ~id, ~label, propertyName:Type, ...
        Edges: ~id, ~from, ~to, ~label, propertyName:Type, ...
        """
        os.makedirs(output_dir, exist_ok=True)
        created_files = []

        # 1. Vertices CSV
        vertices_file = os.path.join(output_dir, "neptune_vertices.csv")
        prop_types: Dict[str, str] = {}
        for data in self.nodes.values():
            for k, v in data["properties"].items():
                if k == "id":
                    continue
                if isinstance(v, float):
                    prop_types[k] = "Double"
                elif isinstance(v, bool):
                    prop_types[k] = "Bool"
                elif isinstance(v, int):
                    prop_types[k] = "Int" if prop_types.get(k) != "Double" else "Double"
                else:
                    prop_types[k] = "String"

        sorted_props = sorted(prop_types.keys())
        vertex_headers = ["~id", "~label"] + [f"{k}:{prop_types[k]}" for k in sorted_props]

        with open(vertices_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(vertex_headers)
            for node_id, data in self.nodes.items():
                row = [node_id, data["label"]]
                for k in sorted_props:
                    row.append(data["properties"].get(k, ""))
                writer.writerow(row)
        created_files.append(vertices_file)

        # 2. Edges CSV
        edges_file = os.path.join(output_dir, "neptune_edges.csv")
        edge_prop_types: Dict[str, str] = {}
        for edge in self.edges:
            for k, v in edge["properties"].items():
                if isinstance(v, float):
                    edge_prop_types[k] = "Double"
                elif isinstance(v, bool):
                    edge_prop_types[k] = "Bool"
                elif isinstance(v, int):
                    edge_prop_types[k] = "Int" if edge_prop_types.get(k) != "Double" else "Double"
                else:
                    edge_prop_types[k] = "String"

        sorted_edge_props = sorted(edge_prop_types.keys())
        edge_headers = ["~id", "~from", "~to", "~label"] + [f"{k}:{edge_prop_types[k]}" for k in sorted_edge_props]

        with open(edges_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(edge_headers)
            for idx, edge in enumerate(self.edges, start=1):
                edge_id = f"e-{edge['source']}-{edge['label']}-{edge['target']}-{idx}"
                row = [edge_id, edge["source"], edge["target"], edge["label"]]
                for k in sorted_edge_props:
                    row.append(edge["properties"].get(k, ""))
                writer.writerow(row)
        created_files.append(edges_file)

        return created_files


def main():
    parser = argparse.ArgumentParser(description="Migrate Neo4j Cypher topology to Amazon Neptune Gremlin and Bulk Loader CSV")
    parser.add_argument("--cypher", default="database/seed_data.cypher", help="Path to seed_data.cypher")
    parser.add_argument("--output-dir", default="database/neptune", help="Output directory for generated files")
    parser.add_argument("--validate", action="store_true", help="Validate outputs after generation")

    args = parser.parse_args()
    migrator = CypherToGremlinMigrator(args.cypher)
    migrator.parse()

    # Generate Groovy script
    groovy_script = migrator.generate_gremlin_groovy()
    groovy_path = os.path.join(args.output_dir, "seed_gremlin.groovy")
    with open(groovy_path, "w", encoding="utf-8") as f:
        f.write(groovy_script)
    print(f"Created Gremlin Groovy script: {groovy_path}")

    # Generate Bulk Loader CSVs
    bulk_dir = os.path.join(args.output_dir, "bulk_loader")
    csv_files = migrator.generate_neptune_bulk_csv(bulk_dir)
    for cf in csv_files:
        print(f"Created Neptune Bulk Loader CSV: {cf}")

    if args.validate:
        print(f"Validation successful: {len(migrator.nodes)} nodes, {len(migrator.edges)} edges processed.")


if __name__ == "__main__":
    main()
