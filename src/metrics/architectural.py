from src.domain.model import UMLClass, UMLModel


class FanInOut:
    def calc_in(self, cls: UMLClass) -> int:
        # FanIn: cuantas clases apuntan hacia esta clase.
        # Ejemplo: ServiceA y ServiceB llaman a Repo -> FanIn(repo)=2.
        return len(cls.incoming)

    def calc_out(self, cls: UMLClass) -> int:
        # FanOut: a cuantas clases depende esta clase.
        # Ejemplo: Service usa Repo+Mapper -> FanOut(service)=2.
        return len(cls.outgoing)


class LRC:
    """Layer-Responsibility Count (cuántas capas toca una clase)."""

    UI = ("ui", "presentation")
    DAO = ("dao", "repository")
    SERVICE = ("service", "logic")

    def _layer(self, package: str | None) -> str:
        # Clasifica paquete en capa logica segun palabras clave.
        # Ejemplo: "com.app.user.service" -> "service".
        if not package:
            return "unknown"
        p = package.lower()
        if any(k in p for k in self.UI):
            return "ui"
        if any(k in p for k in self.DAO):
            return "dao"
        if any(k in p for k in self.SERVICE):
            return "service"
        return "other"

    def calc(self, cls: UMLClass, model: UMLModel) -> int:
        # Arrancamos con la capa de la clase actual.
        layers = {self._layer(cls.package)}

        # Sumamos las capas de todas sus dependencias salientes.
        # Ejemplo: clase en service que llama repository -> {service, dao}.
        for dep in cls.outgoing:
            layers.add(self._layer(model.classes[dep].package))

        # LRC = numero de capas distintas tocadas.
        # Ejemplo: {service, dao, ui} => 3.
        return len(layers)
