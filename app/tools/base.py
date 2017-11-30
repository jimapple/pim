import re
import six
import sqlalchemy
from sqlalchemy.ext.declarative import declared_attr


_camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')

def iteritems(d):
    return iter(d.items())

def _should_set_tablename(cls):

    for base in cls.__mro__:
        d = base.__dict__

        if '__tablename__' in d or '__table__' in d:
            return False

        for name, obj in iteritems(d):
            if isinstance(obj, declared_attr):
                obj = getattr(cls, name)

            if isinstance(obj, sqlalchemy.Column) and obj.primary_key:
                return True


def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1:
            return ('_%s_%s' % (word[:-1], word[-1])).lower()

        return '_' + word.lower()

    return _camelcase_re.sub(_join, name).lstrip('_')

class Model(six.Iterator):

    #: Query class used by :attr:`query`.
    #: Defaults to :class:`SQLAlchemy.Query`, which defaults to :class:`BaseQuery`.
    query_class = None

    #: Convenience property to query the database for instances of this model using the current session.
    #: Equivalent to ``db.session.query(Model)`` unless :attr:`query_class` has been changed.
    query = None

    _cached_tablename = None

    @declared_attr
    def __tablename__(cls):
        if (
            '_cached_tablename' not in cls.__dict__ and
            _should_set_tablename(cls)
        ):
            cls._cached_tablename = camel_to_snake_case(cls.__name__)

        return cls._cached_tablename

    def save(self, session):
        """Save this object."""

        # NOTE(boris-42): This part of code should be look like:
        #                       session.add(self)
        #                       session.flush()
        #                 But there is a bug in sqlalchemy and eventlet that
        #                 raises NoneType exception if there is no running
        #                 transaction and rollback is called. As long as
        #                 sqlalchemy has this bug we have to create transaction
        #                 explicitly.
        with session.begin(subtransactions=True):
            session.add(self)
            session.flush()

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):
        # Don't use hasattr() because hasattr() catches any exception, not only
        # AttributeError. We want to passthrough SQLAlchemy exceptions
        # (ex: sqlalchemy.orm.exc.DetachedInstanceError).
        try:
            getattr(self, key)
        except AttributeError:
            return False
        else:
            return True

    def get(self, key, default=None):
        return getattr(self, key, default)

    @property
    def _extra_keys(self):
        """Specifies custom fields

        Subclasses can override this property to return a list
        of custom fields that should be included in their dict
        representation.

        For reference check tests/db/sqlalchemy/test_models.py
        """
        return []

    def __iter__(self):
        columns = list(dict(object_mapper(self).columns).keys())
        # NOTE(russellb): Allow models to specify other keys that can be looked
        # up, beyond the actual db columns.  An example would be the 'name'
        # property for an Instance.
        columns.extend(self._extra_keys)

        return ModelIterator(self, iter(columns))

    def update(self, values):
        """Make the model object behave like a dict."""
        for k, v in six.iteritems(values):
            setattr(self, k, v)

    def delete(self, session):
        with session.begin(subtransactions=True):
            session.delete(self)
            session.flush()

    def _as_dict(self):
        """Make the model object behave like a dict.

        Includes attributes from joins.
        """
        local = dict((key, value) for key, value in self)
        joined = dict([(k, v) for k, v in six.iteritems(self.__dict__)
                      if not k[0] == '_'])
        local.update(joined)
        return local

    def iteritems(self):
        """Make the model object behave like a dict."""
        return six.iteritems(self._as_dict())

    def items(self):
        """Make the model object behave like a dict."""
        return self._as_dict().items()

    def keys(self):
        """Make the model object behave like a dict."""
        return [key for key, value in self.iteritems()]

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d

class ModelIterator(six.Iterator):

    def __init__(self, model, columns):
        self.model = model
        self.i = columns

    def __iter__(self):
        return self

    # In Python 3, __next__() has replaced next().
    def __next__(self):
        n = six.advance_iterator(self.i)
        return n, getattr(self.model, n)



