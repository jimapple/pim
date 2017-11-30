from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config
from app.tools.base import Model
from app.tools.cache import RedisCache
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_logconfig import LogConfig
import os

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from flask_douwa import Douwa

db = SQLAlchemy(model_class=Model)
douwa = Douwa()
redis = RedisCache()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SQLALCHEMY_ECHO"] = True

    config[config_name].init_app(app)
    # flask 后台自定义后台管理
    admin = Admin(app, name='pim_admin', template_mode='bootstrap2')
    db.init_app(app)
    douwa.init_app(app)
    LogConfig(app)
    redis.connect(app.config["REDIS_HOST"], app.config["REDIS_PORT"], app.config["REDIS_DB"])

    # Create app blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.models import PimTask, PimClothInfo, PimDefect, PimDefectType, PimLeave, PimLeaveReceiver, \
        PimLeaveType, PimLeaveWorkHandType, PimLocationType, PimReport, PimSaveInputInfo, PimSize

    from app.models import LooseInfo, InputLoose

    class PimTaskModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        column_searchable_list = ('location', 'volu_num', 'work_status')

    class PimClothInfoModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        column_searchable_list = ('order_num', 'cloth_num', 'species_name')

    class PimDefectModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        form_columns = ['user_id', 'length', 'defect_type', 'location', 'size',
                        'points', 'spec', 'extend', 'code_number']
        column_searchable_list = ('user_id', 'length')

    class PimDefectTypeModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        column_searchable_list = ('defect_name',)

    class PimLeaveModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        form_columns = ['user_id', 'leave_reason', 'start_time', 'end_time', 'work_hand',
                        'receiver', 'leave_type', 'num_day', 'spec', 'extend', 'result']
        column_searchable_list = ('user_id', 'leave_reason')

    class PimLeaveReceiverModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        form_columns = ['leave_receiver_name', 'user_id']
        column_searchable_list = ('user_id', 'leave_receiver_name')

    class PimLeaveTypeModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        form_columns = ['leave_type', 'user_id']

        column_searchable_list = ('user_id', 'leave_type')

    class PimLeaveWorkHandTypeModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        form_columns = ['work_hang_type', 'user_id']

        column_searchable_list = ('user_id', 'work_hang_type')

    class PimLocationTypeModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        column_searchable_list = ('user_id', 'position_name')

    class PimReportModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        column_searchable_list = ('user_id', 'report_type', 'date_time')

    class PimSaveInputInfoModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        column_searchable_list = ('user_id', 'code_number')

    class PimSizeModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        column_searchable_list = ('user_id', 'size_name')

    class LooseInfoModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        column_searchable_list = ('user_id', 'code_number')

    class InputLooseModelView(ModelView):
        can_delete = False  # disable model deletion
        page_size = 5  # the number of entries to display on the list view
        column_searchable_list = ('user_id', 'code_number')

    admin.add_view(PimTaskModelView(PimTask, db.session))
    admin.add_view(PimClothInfoModelView(PimClothInfo, db.session))
    admin.add_view(PimDefectModelView(PimDefect, db.session))
    admin.add_view(PimDefectTypeModelView(PimDefectType, db.session))
    admin.add_view(PimLeaveModelView(PimLeave, db.session))
    admin.add_view(PimLeaveReceiverModelView(PimLeaveReceiver, db.session))
    admin.add_view(PimLeaveTypeModelView(PimLeaveType, db.session))
    admin.add_view(PimLeaveWorkHandTypeModelView(PimLeaveWorkHandType, db.session))
    admin.add_view(PimLocationTypeModelView(PimLocationType, db.session))
    admin.add_view(PimReportModelView(PimReport, db.session))
    admin.add_view(PimSaveInputInfoModelView(PimSaveInputInfo, db.session))
    admin.add_view(PimSizeModelView(PimSize, db.session))
    admin.add_view(LooseInfoModelView(LooseInfo, db.session))
    admin.add_view(InputLooseModelView(InputLoose, db.session))

    return app



