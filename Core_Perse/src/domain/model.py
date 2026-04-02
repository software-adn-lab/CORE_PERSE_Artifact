from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class UMLAttribute:
    # Nombre del atributo UML. Ejemplo: "score".
    name: str
    # Tipo del atributo si existe en el XMI. Ejemplo: "String" o "int".
    type_: str | None = None


@dataclass
class UMLOperation:
    # Nombre del metodo UML. Ejemplo: "getScore".
    name: str
    # Tipos de parametros del metodo. Ejemplo: ["String", "int"].
    parameter_types: List[str] = field(default_factory=list)


@dataclass
class UMLClass:
    # Identificador unico XMI de la clase. Ejemplo: "_Abc123".
    id_: str
    # Nombre legible de clase. Ejemplo: "AchievementService".
    name: str
    # Lista de atributos declarados en la clase.
    attributes: List[UMLAttribute] = field(default_factory=list)
    # Lista de operaciones/metodos declarados.
    operations: List[UMLOperation] = field(default_factory=list)
    # Dependencias salientes por id de clase destino.
    # Ejemplo: si A usa B, entonces B aparece en outgoing de A.
    outgoing: Set[str] = field(default_factory=set)     # ids
    # Dependencias entrantes por id de clase origen.
    # Ejemplo: si A usa B, entonces A aparece en incoming de B.
    incoming: Set[str] = field(default_factory=set)     # ids
    # Nombre del paquete UML donde vive la clase.
    # Se usa para inferir capas en metrica LRC.
    package: str | None = None


@dataclass
class UMLModel:
    # Diccionario principal del modelo: class_id -> UMLClass.
    # Ejemplo: {"_id1": UMLClass(...), "_id2": UMLClass(...)}
    classes: Dict[str, UMLClass] = field(default_factory=dict)