# -*- coding:utf-8 -*-
from sqlalchemy.dialects.postgresql import JSONB

from app import db, douwa
from app.tools.common import TimestampMixin


class LooseInfo(TimestampMixin, db.Model):
    """ 松布信息 """

    loose_info_id = db.Column(db.String(50), primary_key=True, default=douwa.generator_id)  # 松布信息Id
    code_number = db.Column(db.String(40), nullable=False, unique=True)  # 布匹二维码编码号
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    order_num = db.Column(db.String(40), nullable=False)  # 订单号Id(以后可能是FK)
    cloth_num = db.Column(db.String(40), nullable=False)  # 布号Id(以后可能是FK)
    species_name = db.Column(db.String(40), nullable=False)  # 布种名称
    color_num = db.Column(db.String(40), nullable=False)  # 色号
    color_name = db.Column(db.String(40), nullable=False)  # 颜色名称
    count = db.Column(db.String(40), nullable=False)  # 数量
    produ_line = db.Column(db.String(40), nullable=False)  # 生产线
    door = db.Column(db.String(40), nullable=False)  # 门封
    cyli_num = db.Column(db.String(40), nullable=False)  # 缸号
    wegiht = db.Column(db.String(40), nullable=False)  # 重量
    volu_num = db.Column(db.String(40), nullable=False)  # 卷号
    materials_count = db.Column(db.String(40), nullable=False)  # 物料数量
    act_count = db.Column(db.String(40), nullable=False)  # 实际数量
    loose_time = db.Column(db.DateTime, nullable=False)  # 松布时间
    loose_date = db.Column(db.DateTime, nullable=False)  # 松布日期
    looser = db.Column(db.String(40), nullable=False)  # 松布员
    loose = db.Column(db.String(40), nullable=False)  # 松布
    extend = db.Column(JSONB)


class InputLoose(TimestampMixin, db.Model):
    """保存文本框输入信息"""

    input_loose_id = db.Column(db.String(50), primary_key=True, default=douwa.generator_id)  # 文本框输入信息Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    code_number = db.Column(db.String(40), nullable=False, unique=True)  # 布匹二维码编码号
    check_color = db.Column(db.String(40), nullable=False)  # 对色(true:正常/flase:不正常)
    feel = db.Column(db.String(40), nullable=False)  # 手感(true:正常/flase:不正常)
    weight = db.Column(db.String(40), nullable=False)  # 重量
    head = db.Column(db.String(40), nullable=False)  # 头
    middle = db.Column(db.String(40), nullable=False)  # 中
    tail = db.Column(db.String(40), nullable=False)  # 尾
    speed = db.Column(db.String(40))  # 速度
    length = db.Column(db.String(40))  # 长度
    width_cut = db.Column(db.String(40), nullable=False)  # 可裁幅宽
    time_cut = db.Column(db.DateTime, nullable=False)  # 可裁时间
    first_length = db.Column(db.String(40))  # 驳布长度1
    second_length = db.Column(db.String(40))  # 驳布长度2
    third_length = db.Column(db.String(40))  # 驳布长度3
    extend = db.Column(JSONB)
