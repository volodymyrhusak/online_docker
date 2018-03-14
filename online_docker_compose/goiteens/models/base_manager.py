# -*- coding:utf-8 -*-
from schematics.models import Model
from schematics.types import ModelType

from models.bool_where import BoolWhereDelete, BoolWhereSelect
from .model import UserModel, UserAddModel, UserType
from .executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from .my_types import One2One, One2Many


class SNBaseManager():
    update_sql = 'UPDATE {} SET {} WHERE id = {}'
    update_sql_set = ' {0} = {1} '
    insert_sql = 'INSERT INTO {} VALUES ({})'
    insert_sql_values = '{1}'

    def __init__(self, class_model=None):
        self.object = class_model()
        self._table_to_update = []

    def itemToUpdate(self):
        atoms = self.object.atoms()
        result = []
        for item in atoms:
            if item.field.typeclass != One2One:
                result.append(item.name)
        return result

    def _chooseTemp(self, item):
        if isinstance(item, type(None)):
            return 'NULL'
        elif isinstance(item, dict):
            return item['id']
        elif isinstance(item, int):
            return item
        elif isinstance(item, ModelType):
            return item.id
        return repr(str(item))

    def _sqlValues(self, template):
        keys = self.itemToUpdate()
        primitive = self.object.to_primitive()
        result = '{},' * len(keys)
        result = result.rstrip(',')
        return result.format(*[template.format(key, self._chooseTemp(primitive[key])) for key in keys])

    def save(self):
        atoms = self.object.atoms()
        for atom in atoms:
            if atom.field.typeclass == ModelType:
                man = SNBaseManager(atom.field.model_class)
                man.object = atom.value
                man.save()
            elif atom.field.typeclass == One2One:
                man = SNBaseManager(atom.field.model_class)
                man.object = atom.value
                self._table_to_update.append(man)
            elif atom.field.typeclass == One2Many:
                for mod in atom.value:
                    print('mod = {}'.format(mod))
                    man = SNBaseManager(mod)
                    man.object = mod
                    self._table_to_update.append(man)

        if not self.object.id:
            id = self._save()
            self.object.id = id
        else:
            id = self.object.id
            self._save()
        self._update_child(self.object._name, id)
        return True

    def _update_child(self, table, id):
        for man in self._table_to_update:
            if man.object:
                man.object[table] = id
                man.save()

    def _save(self):
        if self.object.id:
            sql = self.update_sql.format(self.object._name,
                                         self._sqlValues(self.update_sql_set),
                                         self.object.id)
        else:
            sql = self.insert_sql.format(self.object._name,
                                         self._sqlValues(self.insert_sql_values))
        print(sql)
        return self.executeSQL(sql)

    def executeSQL(self, sql):
        return executeSQL(sql)

    def executeSelect(self, sql, all=False):
        return executeSelectAll(sql)

    def update(self):
        sql = self.update_sql.format(self.object._name, self._sqlValues(self.update_sql_set), self.object.id)

    def delete(self):
        return BoolWhereDelete(self)

    def _delete(self, sql):
        return executeSQL(sql)

    def _import_data(self, model_class, value='',sql=None, all=False):
        man = SNBaseManager(model_class)
        class_obj = model_class()
        if not sql:
            sql = man.select().And([('id', '=', value)]).sql
        raw_data = self.executeSelect(sql)
        if raw_data and not all:
            import_data = self.fillData(raw_data[0], class_obj.atoms())
            print('import_data = {}'.format(import_data))
            return class_obj.import_data(raw_data=import_data)
        elif raw_data:
            res = []
            for i in raw_data:
                class_obj = model_class()
                data = class_obj.import_data(self.fillData(i, class_obj.atoms()))
                res.append(data)
            return res
        elif all:
            return []
        else:
            print('return class_obj')
            return class_obj


    def fillData(self, data, atoms):
        resultd = {}
        for atom in atoms:
            model_type = atom.field.typeclass
            if model_type == ModelType:
                resultd[atom.name] = self._import_data(atom.field.model_class, data[atom.name])
            elif model_type == One2One:
                resultd[atom.name] = self._import_data(atom.field.model_class, data['id'])
            elif model_type == One2Many:
                resultd[atom.name] = self._import_data(atom.field.model_class, data['id'], all=True)
            else:
                resultd[atom.name] = data[atom.name]
        return resultd

    def fillModel(self, sql):
        model_class = self.object.__class__
        all = False
        if 'LIMIT' not in sql:
            all = True
        self.object = self._import_data(model_class, sql=sql,all=all)

    def select(self, sql=None):
        if not sql:
            sql = '1=1'
        return BoolWhereSelect(self, sql)


if __name__ == '__main__':
    man = SNBaseManager(UserModel)

