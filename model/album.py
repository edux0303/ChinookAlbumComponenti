from dataclasses import dataclass,field


@dataclass
class Album:
    id: int
    title: str
    numeroBrani : int
    durataTotale : float
    clienti :  set = field(default_factory=set)


    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.title

