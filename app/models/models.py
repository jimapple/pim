# -*- coding:utf-8 -*-
from sqlalchemy.dialects.postgresql import JSONB

from app import db, douwa
from app.tools.common import TimestampMixin


class PimReport(TimestampMixin, db.Model):
    """ 报告表"""

    report_id = db.Column(db.String(50), primary_key=True, default=douwa.generator_id)  # 报告Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    pdf_url = db.Column(db.String(200), nullable=False)  # pdf_URL
    report_type = db.Column(db.Integer, nullable=False)  # 报告类型
    date_time = db.Column(db.DateTime, nullable=False)  # 添加日期
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)
    cyli_num = db.Column(db.String(40), nullable=False)  # 缸号


class PimTask(TimestampMixin, db.Model):
    """任务表"""

    task_id = db.Column(db.String(50), primary_key=True, default=douwa.generator_id)  # 任务Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    location = db.Column(db.String(40),  nullable=False)  # 布匹位置
    volu_num = db.Column(db.String(40), nullable=False)  # 布匹卷号和长度
    work_status = db.Column(db.Integer, nullable=False,default=1)  # 操作状态值(1:无操作/2:取布后/3:验过布匹)
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)


class PimLeaveReceiver(TimestampMixin, db.Model):
    """请假交接人表"""

    leave_receiver_id = db.Column(db.Integer, primary_key=True)  # 请假交接人Id
    leave_receiver_name = db.Column(db.String(40), nullable=False)  # 请假交接人名称
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)


class PimLeaveType(TimestampMixin, db.Model):
    """请假类型表"""

    leave_type_id = db.Column(db.Integer, primary_key=True)  # 请假类型Id
    leave_type = db.Column(db.String(40), nullable=False, unique=True)  # 请假类型
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)


class PimLeaveWorkHandType(TimestampMixin, db.Model):
    """请假工作交接类型表"""

    work_hang_type_id = db.Column(db.Integer, primary_key=True)  # 工作交接类型Id
    work_hang_type = db.Column(db.String(40), nullable=False, unique=True)  # 工作交接类型
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)


class PimLeave(TimestampMixin, db.Model):
    """请假表"""

    leave_id = db.Column(db.String(50), primary_key=True ,default=douwa.generator_id)  # 请假Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    leave_reason = db.Column(db.String(40), nullable=False)  # 请假事由
    start_time = db.Column(db.DateTime, nullable=False)  # 开始时间
    end_time = db.Column(db.DateTime, nullable=False)  # 结束时间
    work_hand_id = db.Column(db.Integer, db.ForeignKey("pim_leave_work_hand_type.work_hang_type_id"), nullable=False)  # 工作交接类型Id
    receiver_id = db.Column(db.Integer, db.ForeignKey("pim_leave_receiver.leave_receiver_id"), nullable=False)  # 交接人Id
    leave_type_id = db.Column(db.Integer, db.ForeignKey("pim_leave_type.leave_type_id"), nullable=False)  # 请假类型Id
    work_hand = db.relationship('PimLeaveWorkHandType')
    receiver = db.relationship('PimLeaveReceiver')
    leave_type = db.relationship('PimLeaveType')
    num_day = db.Column(db.String(40))  # 调休天数(当选择调休时,计算调休天数)
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)
    result = db.Column(db.String(40), default='0')  # 审批结果


class PimClothInfo(TimestampMixin, db.Model):
    """布匹信息"""

    clothinfo_id = db.Column(db.String(50), primary_key=True, default=douwa.generator_id)  # 布匹信息Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    order_num = db.Column(db.String(40), nullable=False)  # 订单号Id(以后可能是FK)
    cloth_num = db.Column(db.String(40), nullable=False)  # 布号Id(以后可能是FK)
    species_name = db.Column(db.String(40), nullable=False)  # 布种名称
    color_num = db.Column(db.String(40), nullable=False)  # 色号
    color_name = db.Column(db.String(40), nullable=False)  # 颜色名称
    count = db.Column(db.Integer, nullable=False)  # 数量
    produ_line = db.Column(db.String(40), nullable=False)  # 生产线
    door = db.Column(db.String(40), nullable=False)  # 门封
    cyli_num = db.Column(db.String(40), nullable=False)  # 缸号
    wegiht = db.Column(db.Integer, nullable=False)  # 重量
    volu_num = db.Column(db.String(40), nullable=False)  # 卷号
    sam = db.Column(db.Integer, nullable=False)  # 抽检
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)
    code_number = db.Column(db.String(40), nullable=False, unique=True)  # 布匹二维码编码号


class PimDefectType(TimestampMixin, db.Model):
    """疵点类型表"""

    defect_id = db.Column(db.Integer, primary_key=True)  # 疵点类型Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    defect_name = db.Column(db.String(40), nullable=False, unique=True)  # 疵点类型名称
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)


class PimLocationType(TimestampMixin, db.Model):
    """疵点位置类型表"""

    position_id = db.Column(db.Integer, primary_key=True)  # 疵点位置类型Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    position_name = db.Column(db.String(40), nullable=False, unique=True)  # 疵点位置类型名称
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)


class PimSize(TimestampMixin, db.Model):
    """疵点大小类型表"""

    size_id = db.Column(db.Integer, primary_key=True)  # 疵点大小Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    size_name = db.Column(db.String(40), nullable=False, unique=True)  # 疵点大小名称
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)


class PimDefect(TimestampMixin, db.Model):
    """疵点信息表"""

    defect_info_id = db.Column(db.String(50), primary_key=True, default=douwa.generator_id)  # 疵点信息Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    length = db.Column(db.Float, nullable=False)  # 长度
    defect_type_id = db.Column(db.Integer, db.ForeignKey("pim_defect_type.defect_id"), nullable=False)  # 疵点类型Id
    location_id = db.Column(db.Integer, db.ForeignKey("pim_location_type.position_id"), nullable=False)  # 疵点位置类型Id
    size_id = db.Column(db.Integer, db.ForeignKey("pim_size.size_id"), nullable=False)  # 疵点大小类型Id
    defect_type = db.relationship('PimDefectType')
    location = db.relationship('PimLocationType')
    size = db.relationship('PimSize')
    points = db.Column(db.Integer, nullable=False)  # 扣分
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)
    code_number = db.Column(db.String(40), nullable=False)  # 布匹二维码编码号


class PimSaveInputInfo(TimestampMixin, db.Model):
    """保存文本框输入信息"""

    input_info_id = db.Column(db.String(50), primary_key=True, default=douwa.generator_id)  # 文本框输入信息Id
    user_id = db.Column(db.String(40), nullable=False)  # 用户Id
    code_number = db.Column(db.String(40), nullable=False, unique=True)  # 检验码
    check_color = db.Column(db.String(40), nullable=False)  # 对色(true:正常/flase:不正常)
    feel = db.Column(db.String(40), nullable=False)  # 手感(true:正常/flase:不正常)
    weight = db.Column(db.Integer, nullable=False)  # 重量
    head = db.Column(db.String(40), nullable=False)  # 头
    middle = db.Column(db.String(40), nullable=False)  # 中
    tail = db.Column(db.String(40), nullable=False)  # 尾
    act_quant = db.Column(db.Integer, nullable=False)  # 实际数量
    width_cut = db.Column(db.Integer, nullable=False)  # 可裁幅宽
    whm_color = db.Column(db.String(40), nullable=False)  # 头中尾色
    marg_color = db.Column(db.String(40), nullable=False)  # 边中色
    check_date = db.Column(db.DateTime)  # 检验日期
    checker = db.Column(db.String(40), nullable=False)  # 检验员
    total_deduct = db.Column(db.Integer, nullable=False)  # 总扣分
    hunard_numvalue = db.Column(db.DECIMAL, nullable=False)  # 百平码值
    result = db.Column(db.String(40), nullable=False)  # 结果判定(true:/合格,false/不合格)
    spec = db.Column(JSONB)
    extend = db.Column(JSONB)