from __future__ import annotations

from pathlib import Path
from lxml import etree

from src.domain.model import UMLModel, UMLClass, UMLAttribute, UMLOperation


class XMIParser:
    # Namespaces XML usados en consultas XPath.
    NS = {
        "uml": "http://www.omg.org/spec/UML/20090901",
        "xmi": "http://www.omg.org/XMI",
    }

    # ------------------------------------------------------------------ #
    def parse(self, file: Path | str) -> UMLModel:
        """
        Lee un archivo XMI y devuelve un UMLModel.
        - Primer intento: parseo estricto.
        - Si falla por XMLSyntaxError, reintenta sin comentarios y con recover=True.
        """
        # Paso 1: normalizamos y validamos la ruta de entrada.
        p = Path(file)
        if not p.exists():
            raise FileNotFoundError(p.resolve())

        try:
            # Paso 2 (intento estricto): parseo XML normal.
            root = etree.parse(str(p)).getroot()
        except etree.XMLSyntaxError as err:
            # Segundo intento: tolerante
            # remove_comments/recover ayudan con XMI mal formado.
            parser = etree.XMLParser(remove_comments=True, recover=True)
            root = etree.parse(str(p), parser=parser).getroot()
            print(f"⚠️  XML corregido automáticamente ({err})")

        # Paso 3: contenedor del modelo UML en memoria.
        model = UMLModel()

        # ---------- 1 · clases / interfaces ----------------------------- #
        # Buscamos nodos UML que sean Class o Interface.
        # Ejemplo de XPath objetivo:
        # .//packagedElement[@xmi:type='uml:Class']
        for node in root.xpath(
            ".//packagedElement[@xmi:type='uml:Class' or @xmi:type='uml:Interface']",
            namespaces=self.NS,
        ):
            # Construimos entidad de dominio UMLClass.
            cls = UMLClass(
                id_=node.get(f"{{{self.NS['xmi']}}}id"),
                name=node.get("name", "<unnamed>"),
                package=self._package_of(node),
            )
            # atributos
            for att in node.xpath("./ownedAttribute"):
                # Ejemplo: <ownedAttribute name="score" type="int"/>
                cls.attributes.append(UMLAttribute(att.get("name"), att.get("type")))
            # operaciones
            for op in node.xpath("./ownedOperation"):
                # Ejemplo: <ownedOperation name="getScore">...
                cls.operations.append(
                    UMLOperation(
                        op.get("name"),
                        [p.get("type") for p in op.xpath("./ownedParameter")],
                    )
                )
            # Registramos clase por id.
            model.classes[cls.id_] = cls

        # ---------- 1.b · clientDependency (sin prefijo) ----------------- #
        # Algunas herramientas XMI guardan dependencias aqui.
        for dep in root.xpath(".//clientDependency"):
            client_id = dep.getparent().get(f"{{{self.NS['xmi']}}}id")
            supplier_id = dep.get("supplier")
            self._add_edge(model, client_id, supplier_id)

        # ---------- 2 · Dependency / Association ------------------------ #
        # Otras relaciones vienen como packagedElement Dependency/Association.
        for rel in root.xpath(
            ".//packagedElement[@xmi:type='uml:Dependency' "
            "or @xmi:type='uml:Association']",
            namespaces=self.NS,
        ):
            # Fallback memberEnd cuando no existe client/supplier explicitos.
            client = rel.get("client") or rel.get("memberEnd")
            supplier = rel.get("supplier") or rel.get("memberEnd")
            self._add_edge(model, client, supplier)

        print(f"[PARSE]  clases cargadas: {len(model.classes)}")  # debug opcional
        return model

    # ------------------------------------------------------------------ #
    @staticmethod
    def _add_edge(model: UMLModel, client_id: str | None, supplier_id: str | None):
        # Solo agregamos arista si ambos ids son validos y no hay self-loop.
        # Ejemplo valido: A -> B.
        # Ejemplo invalido: A -> A.
        if (
            client_id
            and supplier_id
            and client_id in model.classes
            and supplier_id in model.classes
            and client_id != supplier_id
        ):
            # Guardamos ambos sentidos para soportar FanIn/FanOut.
            model.classes[client_id].outgoing.add(supplier_id)
            model.classes[supplier_id].incoming.add(client_id)

    # ------------------------------------------------------------------ #
    def _package_of(self, element) -> str | None:
        # Recorre ancestros hasta encontrar un Package contenedor.
        # Ejemplo: com.app.service -> devuelve "service" segun XMI.
        p = element.getparent()
        while p is not None:
            if p.tag.endswith("Package"):
                return p.get("name")
            p = p.getparent()
        return None
