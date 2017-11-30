from flask import Blueprint, jsonify

main = Blueprint('main', __name__)


class LeavingError(Exception):
    """添加请假条失败"""


@main.errorhandler(LeavingError)
def error_leaving(error):
    response = dict(status_code=0, message="请假参数错误！")
    return jsonify(response), 500


class AddLooseError(Exception):
    """添加松布信息失败"""


@main.errorhandler(AddLooseError)
def error_add_loose(error):
    response = dict(status_code=0, message="添加松布信息失败！")
    return jsonify(response), 500

# @main.errorhandler(Exception)
# def error_500(error):
#     response = dict(status=0, message="500 Error")
#     return jsonify(response), 400
from . import api, looseapi

