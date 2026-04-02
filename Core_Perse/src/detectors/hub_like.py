import networkx as nx
from src.domain.model import UMLModel


class HubLikeDependencyDetector:
    """Detecta hubs mediante PageRank + umbral estadístico μ+σ."""

    def detect(self, model: UMLModel, top_k: int = 10):
        # Paso 1: creamos un grafo dirigido vacio.
        # Ejemplo: A -> B significa "A depende de B".
        g = nx.DiGraph()

        # Paso 2: convertimos el modelo UML a aristas del grafo.
        # Si cls.name="AchievementService" y tgt="IAchievementRepository",
        # se agrega la arista "AchievementService" -> "IAchievementRepository".
        for cls in model.classes.values():
            for tgt in cls.outgoing:
                g.add_edge(cls.name, model.classes[tgt].name)

        # Paso 3: si no hay relaciones, no hay hubs para reportar.
        if not g:
            return []

        # Paso 4: PageRank mide "importancia" de nodos dentro de la red.
        # Ejemplo de salida: {"Guest": 0.12, "Repo": 0.30, "Service": 0.20}
        pr = nx.pagerank(g)

        # Paso 5: calculamos grado promedio (in+out) de todos los nodos.
        mean_deg = sum(dict(g.degree()).values()) / g.number_of_nodes()

        # Paso 6: desviacion estandar de grados.
        # Se usa para saber que tan dispersa esta la conectividad.
        # Formula: sqrt(sum((d-media)^2)/N)
        std_deg = (sum((d - mean_deg) ** 2 for d in dict(g.degree()).values())
                   / g.number_of_nodes()) ** 0.5

        # Paso 7: umbral estadistico para llamar "hub" a un nodo.
        # Umbral = media + desviacion.
        # Si media=2 y desviacion=1.5 => threshold=3.5
        threshold = mean_deg + std_deg

        # Paso 8: seleccionamos nodos cuyo grado supere el umbral.
        hubs = [n for n in pr if g.degree(n) > threshold]

        # Paso 9: ordenamos por PageRank descendente para priorizar hubs mas centrales.
        hubs.sort(key=lambda n: pr[n], reverse=True)

        # Paso 10: devolvemos solo los top_k hubs (por defecto 10).
        # Ejemplo: si hubs=["Repo","Service","Gateway"] y top_k=2 => ["Repo","Service"]
        return hubs[:top_k]
