import json

from sqlalchemy import inspect
from sqlalchemy.orm.interfaces import (ONETOMANY, MANYTOMANY)
import decimal


__all__ = ['serializer']

class Serializer(object):
    def __init__(self,
                 instance,
                 many=False,
                 include=[],
                 exclude=[],
                 exclude_dict=dict(),
                 extra=[],
                 depth=2):
        self.instance = instance
        self.many = many
        self.depth = depth
        self.include = include
        self.exclude = exclude
        self.extra = extra
        self.exclude_dict = exclude_dict
        if isinstance(instance, list):
            self.many = True

    @property
    def data(self):
        if self.include and self.exclude:
            raise ValueError('include and exclude can\'t work together')
        if self.many:
            return self._serializerlist(self.instance, self.depth)
        return self._serializer(self.instance, self.depth)

    def _serializerlist(self, instances, depth):
        results = []
        for instance in instances:
            result = self._serializer(instance, depth)
            if result:
                results.append(result)
        return results

    def _serializer(self, instance, depth):
        result = {}
        if depth == 0:
            return result
        depth -= 1
        model_class = self.get_model_class(instance)
        inp = self.get_inspect(model_class)
        model_data = self._serializer_model(inp, instance, depth)
        relation_data = self._serializer_relation(inp, instance, depth)
        extra_data = self._serializer_extra(instance)
        result.update(model_data)
        result.update(relation_data)
        result.update(extra_data)
        return result

    def _serializer_extra(self, instance):
        extra = self.extra
        result = {}
        for e in extra:
            # extra_column = getattr(self, e)
            # if isinstance(extra_column, Field):
            #     result[e] = extra_column.data(instance)
            # else:
            extra_column = getattr(instance, e)
            result[e] = extra_column if not callable(
                extra_column) else extra_column()
        return result

    def _serializer_model(self, inp, instance, depth):
        result = {}
        model_columns = self.get_model_columns(inp)
        for column in model_columns:
            data = getattr(instance, column)
            #if isinstance(data, datetime.date):
            #    result[column] = "{}-{}-{}".format(data.year, data.month, data.day)
            if isinstance(data, decimal.Decimal):
                result[column] = float(data)
            else:
                result[column] = data
        return result

    def _serializer_relation(self, inp, instance, depth):
        result = {}
        relation_columns = self.get_relation_columns(inp)
        for relation in relation_columns:
            column = relation.key
            if relation.direction in [ONETOMANY, MANYTOMANY
                                      ] and relation.uselist:
                children = getattr(instance, column)
                if relation.lazy == 'dynamic':
                    children = children.all()
                if children:
                    ex = self.exclude_dict.get(column, list())
                    eex = [relation.back_populates]
                    eex.extend(ex)
                    result[column] = Serializer(
                        children,
                        many=True,
                        exclude=eex,
                        depth=depth).data
                else:
                    result[column] = []
            else:
                child = getattr(instance, column)
                if relation.lazy == 'dynamic':
                    child = child.first()
                if child:
                    ex = self.exclude_dict.get(column, list())
                    eex = [relation.back_populates]
                    eex.extend(ex)
                    result[column] = Serializer(
                        child,
                        many=False,
                        exclude=eex,
                        depth=depth).data
                else:
                    result[column] = {}
        return result

    def get_model_class(self, instance):
        return getattr(instance, '__class__')

    def get_inspect(self, model_class):
        return inspect(model_class)

    def get_model_columns(self, inp):
        if self.include:
            model_columns = [
                column.name for column in inp.columns
                if column.name in self.include
            ]
        elif self.exclude:
            model_columns = [
                column.name for column in inp.columns
                if column.name not in self.exclude
            ]
        else:
            model_columns = [column.name for column in inp.columns]

        return model_columns

    def get_relation_columns(self, inp):
        if self.include:
            relation_columns = [
                relation for relation in inp.relationships
                if relation.key in self.include
            ]
        elif self.exclude:
            relation_columns = [
                relation for relation in inp.relationships
                if relation.key not in self.exclude
            ]
        else:
            relation_columns = [relation for relation in inp.relationships]
        return relation_columns


def serializer(instance,
               include=[],
               exclude=[],
               exclude_dict=dict(),
               depth=2):
    return Serializer(instance, include=include, exclude=exclude, exclude_dict=exclude_dict, depth=depth).data
