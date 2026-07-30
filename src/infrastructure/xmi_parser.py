from __future__ import annotations

from pathlib import Path
from lxml import etree

from src.domain.model import UMLModel, UMLClass, UMLAttribute, UMLOperation


class XMIParser:
    # Namespaces XML usados en consultas XPath.
    NS = {
        "uml": None,
        "xmi": None,
    }

    # ------------------------------------------------------------------ #
    def parse(self, file: Path | str) -> UMLModel:
        """
        Lee un archivo XMI y devuelve un UMLModel.
        """

        # Paso 1: validar ruta
        p = Path(file)
        if not p.exists():
            raise FileNotFoundError(p.resolve())

        # Paso 2: leer XML
        try:
            root = etree.parse(str(p)).getroot()
        except etree.XMLSyntaxError as err:
            parser = etree.XMLParser(remove_comments=True, recover=True)
            root = etree.parse(str(p), parser=parser).getroot()
            print(f"⚠️ XML corregido automáticamente ({err})")

        # ================= DEBUG =================
        print("ROOT =", root.tag)
        print("NSMAP =", root.nsmap)

        nodes = root.xpath(
            ".//*[contains(@*[local-name()='type'], 'Class') or "
            "contains(@*[local-name()='type'], 'Interface')]"
        )

        print("TOTAL NODOS =", len(nodes))

        for n in nodes[:10]:
            print("TAG:", n.tag)
            print("NAME:", n.get("name"))
            print("ATTRS:", n.attrib)
            print("----------------------------")
        # =========================================

        model = UMLModel()

        xmi_ns = root.nsmap.get(
            "xmi",
            "http://schema.omg.org/spec/XMI/2.1"
        )

        # ---------- Clases / Interfaces ---------- #
        for node in nodes:

            print("Procesando:", node.tag)

            cls = UMLClass(
                id_=node.get(f"{{{xmi_ns}}}id"),
                name=node.get("name", "<unnamed>"),
                package=self._package_of(node),
            )

            print("ID =", cls.id_)
            print("NAME =", cls.name)

            # atributos
            for att in node.xpath("./ownedAttribute"):
                cls.attributes.append(
                    UMLAttribute(
                        att.get("name"),
                        att.get("type")
                    )
                )

            # operaciones
            for op in node.xpath("./ownedOperation"):
                cls.operations.append(
                    UMLOperation(
                        op.get("name"),
                        [
                            p.get("type")
                            for p in op.xpath("./ownedParameter")
                        ],
                    )
                )

            model.classes[cls.id_] = cls

        # ---------- 1.b · clientDependency (sin prefijo) ----------------- #
        # Algunas herramientas XMI guardan dependencias aqui.
        for dep in root.xpath(".//clientDependency"):
            client_id = dep.getparent().get(f"{{{self.NS['xmi']}}}id")
            supplier_id = dep.get("supplier")
            self._add_edge(model, client_id, supplier_id)

        # ---------- Dependency / Association ---s------- #
        rels = root.xpath(
            ".//*[contains(@*[local-name()='type'], 'Dependency') or "
            "contains(@*[local-name()='type'], 'Association')]"
        )

        print("RELACIONES:", len(rels))

        for rel in rels:

            client = rel.get("client") or rel.get("memberEnd")
            supplier = rel.get("supplier") or rel.get("memberEnd")

            self._add_edge(
                model,
                client,
                supplier,
            )

        print(f"[PARSE] clases cargadas: {len(model.classes)}")

        return model

    # ------------------------------------------------------------------ #
    @staticmethod
    def _add_edge(
        model: UMLModel,
        client_id: str | None,
        supplier_id: str | None,
    ):
        if (
            client_id
            and supplier_id
            and client_id in model.classes
            and supplier_id in model.classes
            and client_id != supplier_id
        ):
            model.classes[client_id].outgoing.add(supplier_id)
            model.classes[supplier_id].incoming.add(client_id)

    # ------------------------------------------------------------------ #
    def _package_of(self, element) -> str | None:

        p = element.getparent()

        while p is not None:

            if p.tag.endswith("Package"):
                return p.get("name")

            p = p.getparent()

        return None