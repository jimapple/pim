# import iso8601
import iso8601 as iso8601

from app import db, douwa
# from app import douwa
import datetime


def get_session():
    # return db.create_session(options={})
    return db.create_scoped_session(options={'autocommit': True, 'autoflush': False})
    # return db.create_scoped_session(options={})


def add(model=None, data=None,session=None, error=None):
    try:

        instance = model(**data)
        app = instance.save(session)
    except Exception as e:
        session.rollback()
        raise error


def update(session=None, error=None):
    try:
        pass
    except Exception as e:
        session.rollback()
        raise error


def delete(model=None, data=None,session=None, error=None):
    try:
        instance = model(**data)
        instance.delete(session)

    except Exception as e:
        session.rollback()
        raise error


def utcnow(with_timezone=False):
    if with_timezone:
        return datetime.datetime.now(tz=iso8601.iso8601.UTC)
    return datetime.datetime.utcnow()


class TimestampMixin(object):
    created_at = db.Column(db.DateTime, default=lambda: utcnow())
    updated_at = db.Column(db.DateTime, onupdate=lambda: utcnow())


class SoftDeleteMixin(object):
    deleted_at = db.Column(db.DateTime)
    deleted = db.Column(db.Integer, default=0)

    def soft_delete(self, session):
        self.deleted = self.id
        self.deleted_at = utcnow()
        self.save(session=session)


class LookupTableMixin(object):
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text(), nullable=True)


class IdMixin(object):
    id = db.Column(db.String(20),
                     nullable=True,
                     default=douwa.generator_id,
                     primary_key=True)

