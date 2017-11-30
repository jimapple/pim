import logging

from flask import request

from app.main import main, AddLooseError
from app.models import LooseInfo, InputLoose
from app.tools import messages
from app.tools.common import get_session
from app.tools.serializer import serializer
from app.tools.util import api_result

logger = logging.getLogger()


# 获取松布信息
@main.route("/pim_api/loose_info", methods=['POST'])
def loose_info():
    data = request.get_json()
    if 'user_id' in data and 'code_number' in data:
        try:
            info = LooseInfo.query.filter_by(code_number=data.get('code_number', 0)).first()
            if info:
                return api_result(status_code=1, data={'result': serializer(info, exclude=[
                    'extend', 'user_id', 'code_number'])})
        except Exception as e:
            logger.error(e)
    return api_result(status_code=0, message=messages.loose_info_none)


# 获取文本框信息
@main.route("/pim_api/input_loose", methods=['POST'])
def input_loose():
    data = request.get_json()
    if 'user_id' in data and 'code_number' in data:
        try:
            info = InputLoose.query.filter_by(code_number=data.get('code_number', 0)).first()
            if info:
                return api_result(status_code=1, data={'result': serializer(info, exclude=[
                    'extend', 'user_id', 'code_number', 'input_loose_id'])})
        except Exception as e:
            logger.error(e)
    return api_result(status_code=0, message=messages.info_none)


# 保存文本框输入信息
@main.route("/pim_api/save_input_loose", methods=['POST'])
def save_input_loose():
    data = request.get_json()
    session = get_session()
    if 'user_id' in data and 'code_number' in data and 'check_color' in data \
            and 'feel' in data and 'weight' in data and 'head' in data \
            and 'middle' in data and 'tail' in data \
            and 'width_cut' in data and 'time_cut' in data:
        try:
            logger.info(data)
            loose = session.query(InputLoose).filter_by(code_number=data.get('code_number')).first()
            if not loose:
                input_model = InputLoose(**data)
                input_model.save(session)
                return api_result(status_code=1, data={'input_infoId': input_model.input_loose_id})

            else:
                loose.update(data)
                loose.save(session)
                return api_result(status_code=1, data={'input_infoId': loose.input_loose_id})

        except Exception as e:
            logger.error(e)
            session.rollback()
            raise AddLooseError
    return api_result(status_code=0, message=messages.wrong_params)

