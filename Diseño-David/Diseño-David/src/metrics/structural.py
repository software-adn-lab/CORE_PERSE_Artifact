from src.domain.model import UMLClass


class WMC:
    """Weighted Methods per Class (simplificado)."""

    def calc(self, cls: UMLClass) -> int:
        # Version simplificada: WMC = cantidad de metodos.
        # Ejemplo: 6 operaciones => WMC = 6.
        return len(cls.operations)


class ATFD:
    """Access To Foreign Data (basado en count de dependencias salientes)."""

    def calc(self, cls: UMLClass) -> int:
        # Version simplificada: ATFD = numero de clases externas usadas.
        # Ejemplo: si outgoing={Repo,Mapper}, ATFD=2.
        return len(cls.outgoing)


class TCC:
    """Tight Class Cohesion (pares que comparten campo / total de pares)."""

    def calc(self, cls: UMLClass) -> float:
        # Lista de metodos de la clase.
        m = cls.operations

        # Convencion usada en esta implementacion:
        # con 0 o 1 metodo, cohesion se considera maxima (1.0).
        if len(m) < 2:
            return 1.0

        # "shared" cuenta pares de metodos que comparten al menos un atributo.
        shared = 0

        # Numero total de pares unicos de metodos: n*(n-1)/2.
        total = len(m) * (len(m) - 1) / 2
        for i, mi in enumerate(m):
            for mj in m[i + 1:]:
                if self._share(mi, mj, cls):
                    shared += 1

        # TCC final entre 0 y 1.
        # Ejemplo: shared=2, total=4 => TCC=0.5.
        return shared / total

    @staticmethod
    def _share(m1, m2, cls):
        """Dos métodos comparten atributo SÓLO si el nombre coincide."""
        # Conjunto de nombres de atributos de la clase.
        attrs = {att.name for att in cls.attributes}
        # Pseudo-heurística: si el nombre del atributo aparece como
        # substring en el nombre de ambos métodos → consideramos uso.
        # Ejemplo:
        # atributo="score", m1="getScore", m2="updateScore" -> True.
        return any(a.lower() in m1.name.lower() and a.lower() in m2.name.lower()
                   for a in attrs)
