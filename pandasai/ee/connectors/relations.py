from abc import abstractmethod


class AbstractRelation:
    @abstractmethod
    def to_string(self):
        raise NotImplementedError


class PrimaryKey(AbstractRelation):
    def __init__(self, name):
        self.name = name

    def to_string(self):
        return f"PRIMARY KEY ({self.name})"


class ForeignKey(AbstractRelation):
    def __init__(self, field, foreign_table, foreign_table_field):
        self.field = field
        self.foreign_table_field = foreign_table_field
        self.foreign_table = foreign_table

    def to_string(self):
        return f"FOREIGN KEY ({self.field}) REFERENCES {self.foreign_table}({self.foreign_table_field})"
