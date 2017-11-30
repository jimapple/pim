# -*- coding:utf8 -*-
from datetime import datetime
from app.tools.MathUtils import cel_check_length, work_complete_percent, yesterday_complete_species, \
    yesterday_work_state, per_hour_efficiency, per_hour_species, work_encourage
from app.tools.common import get_session, add
from . import main, LeavingError
from app.models import PimTask, PimClothInfo, PimDefect, PimDefectType, PimLeave, PimLeaveReceiver, \
    PimLeaveType, PimLeaveWorkHandType, PimLocationType, PimReport, PimSaveInputInfo, PimSize
from flask import flash, request
from flask.ext.login import login_required, logout_user
from app.tools.util import api_result, Weather, Pagenator, DateTimeFormat, url_host, PagenatorFlaskSqlalchemy
from app.tools import messages
from app.tools.serializer import serializer
import logging
import math

logger = logging.getLogger()


# 用户登录
@main.route("/pim_api/user_login", methods=['POST'])
def login():
    pass
    return api_result(status_code=1, message=messages.status_ok)


# 用户退出
@main.route("/pim_api/user_logout")
# @login_required
def logout():
    logout_user()
    flash(messages.log_out)
    return api_result(status_code=1, message=messages.status_ok)


# 获取用户信息
@main.route("/pim_api/user_info", methods=['POST'])
def user_info():
    pass
    return


# 修改用户密码
@main.route("/pim_api/user_change_pwd", methods=['POST'])
# @login_required
def chang_pwd():
    pass
    return api_result(status_code=1, message=messages.status_ok)


# 获取当日天气
@main.route("/pim_api/today_weather", methods=['POST'])
def today_weather():
    request_data = request.get_json()
    try:
        city = request_data.get('city')
        if city:
            resp = Weather(city=city)
            if resp.get('message'):
                return api_result(status_code=0, message=messages.city_not_found)
            else:
                return api_result(status_code=1, data=resp)
        return api_result(status_code=0, message=messages.wrong_params)
    except Exception as e:
        logger.error(e)


# 获取工作鼓励
@main.route("/pim_api/work_encour", methods=['POST'])
def work_encour():
    request_data = request.get_json()
    try:
        userid = request_data.get('user_id')
        username = "张三"
        count = PimTask.query.filter_by(user_id=userid).count()
        if count != 0:
            yesterday_complete = yesterday_complete_species(userid=userid, typeaccount=0)
            yesterday_all = yesterday_complete_species(userid=userid, typeaccount=1)
            title = yesterday_work_state(cel_species_count=yesterday_complete, yel_species_count=yesterday_all)
            result = work_encourage(username=username, userid=userid, yesterday_work=title)
            return api_result(status_code=1, data={'message': result})
        return api_result(status_code=0, message=messages.user_not_found)
    except Exception as e:
        logger.error(e)


# 获取工作任务进度百分比
@main.route("/pim_api/work_task_schedule", methods=['POST'])
def work_task_schedule():
    request_data = request.get_json()
    try:
        pimtask = PimTask.query.filter_by(user_id=request_data['user_id']).count()
        if 'user_id' in request_data and pimtask != 0:
            userid = request_data['user_id']
            # 今天已验过的布料
            complete_length = cel_check_length(userid=userid, typeaccount=0)
            # 总共需要验的布料
            need_total_specie = cel_check_length(userid=userid, typeaccount=1)
            # 工作完成百分比
            work_percent = work_complete_percent(complete_length=complete_length, need_length=need_total_specie)
            return api_result(status_code=1, data={'task_prece': work_percent})
        return api_result(status_code=0, message=messages.user_not_found)
    except Exception as e:
        logger.error(e)


# 获取我的任务列表
@main.route("/pim_api/task_list", methods=['POST'])
def task_list():
    request_data = request.get_json()
    try:
        NOW = datetime.utcnow()
        pimtask = PimTask.query.filter_by(user_id=request_data['user_id']).all()
        yestodaypimtask = PimTask.query.filter_by(user_id=request_data['user_id']).filter_by(work_status=3).filter \
            (PimTask.updated_at < datetime(NOW.year, NOW.month, NOW.day, 0, 0, 0)).all()
        # 剔除昨天之前已完成的任务
        today_pimtask = list(set(pimtask) - set(yestodaypimtask))
        if today_pimtask:
            task_context = []
            location_list = []
            for task1 in today_pimtask:
                location_list.append(task1.location)
            location_list_set = set(location_list)
            for locat in location_list_set:
                location_value = []
                for task2 in today_pimtask:
                    if locat == task2.location:
                        location_value.append({'volu_num': task2.volu_num, 'wrok_status': task2.work_status})
                # 以wrok_status进行排序（包含字典的列表按字典值排序的方法）
                task_context.append({'location': locat, 'location_value': sorted(location_value,
                                                                                 key=lambda location_value: location_value[
                                                                                     'wrok_status'])})
            # 获取完数据后按布匹位置分页
            # pagnator = Pagenator(request_data=request_data,
            #                      queryset=sorted(task_context, key=lambda task_context: task_context['location']))
            # task_context = pagnator.paging()
            # total_number = pagnator.total_number
            # total_page = pagnator.total_page
            # resp = {'total_number': total_number, 'total_page': total_page,
            #         'task_context': task_context}
            resp = {'task_context': sorted(task_context, key=lambda task_context: task_context['location'])}
            return api_result(status_code=1, data=resp)
        return api_result(status_code=0, message=messages.user_not_found)
    except Exception as e:
        logger.error(e)


# 获取每小时工作效率
@main.route("/pim_api/work_bast", methods=['POST'])
def work_bast():
    request_data = request.get_json()
    if 'user_id' in request_data:
        try:
            userid = request_data['user_id']
            data = datetime.now()
            # 今日完成验布总数
            update_at = PimTask.query.filter_by(user_id=userid).filter(
                PimTask.updated_at.between(
                    datetime(data.year, data.month, data.day, 0, 0, 0),
                    datetime(data.year, data.month, data.day + 1, 0, 0, 0)
                )).all()
            time_list = []
            for i in update_at:
                time_list.append(i.updated_at.strftime('%H,%M,%S'))
            # 将所有验布完成时间按照算法进行时间先后排序
            time_list.sort(key=lambda item: int(item[:2]) * 60 + int(item[3:5]))

            if len(time_list) == 0:
                empty_list = [{'grid': i, 'rate': 0} for i in range(1, 13)]
                return api_result(status_code=1, data={'result': empty_list})

            start = int(time_list[0][:2])
            end = int(time_list[-1][:2])
            hour_list = []
            # 组成一天验布所有完成时间的小时列表
            if end > start:
                hour_list = [(start + time) for time in range(end - start)]
            else:
                hour_list.append(start)
            efficiency_list = []
            # 今日完成工作总量
            today_work_count = PimTask.query.filter_by(user_id=userid).filter_by(work_status=3).filter(
                PimTask.updated_at.between(
                    datetime(data.year, data.month, data.day, 0, 0, 0),
                    datetime(data.year, data.month, data.day + 1, 0, 0, 0)
                )).count()
            # 今日总共工作的小时数
            total_work_count = end - start + 1
            num = 1

            # 计算每个小时的工作效率
            for hour in hour_list:
                if today_work_count == 0:
                    efficiency_list = [{'grid': i, 'rate': 0} for i in range(1, 13)]
                else:
                    hour_efficiency = per_hour_efficiency(
                        per_hour_species(userid=userid, hour=hour),
                        today_work_count=today_work_count,
                        total_work_count=total_work_count)
                    efficiency_list.append({'grid': num, 'rate': hour_efficiency})
                    num += 1

            if len(efficiency_list) < 12:
                for num in range(len(efficiency_list) + 1, 13):
                    efficiency_list.append({'grid': num, 'rate': 0})
            elif len(efficiency_list) > 12:
                count = len(efficiency_list) - 12
                for num in range(count):
                    efficiency_list.pop()

            return api_result(status_code=1, data={'result': efficiency_list})
        except Exception as e:
            logger.error(e)
    return api_result(status_code=0, message=messages.user_not_found)


# 请假
@main.route("/pim_api/leaving", methods=['POST'])
def leaving():
    session = get_session()
    request_data = request.get_json()
    if request_data.get('leave_reason') \
            and request_data.get('start_time') and request_data.get('end_time') \
            and request_data.get('work_hand_id') and request_data.get('receiver_id') \
            and request_data.get('leave_type_id') and request_data.get('user_id'):
        # logger.info(PimLeaveWorkHandType.query.all()[0].work_hang_type_id)
        # print(PimLeaveReceiver.query.all()[0].leave_receiver_id)
        # print(PimLeaveType.query.all()[0].leave_type_id)
        try:
            leave = PimLeave(**request_data)
            leave.save(session)
            return api_result(status_code=1, data={"message": "ok"})
        except Exception as e:
            logger.error(e)
            session.rollback()
            raise LeavingError("请假参数错误!")
    else:
        return api_result(status_code=0, data={"message": "failed"})


# 获取请假工作交接类型
@main.route("/pim_api/leave_workhand_type", methods=['POST'])
def leave_workhand_type():
    session = get_session()

    try:
        pim_leave_work_hand_type = session.query(PimLeaveWorkHandType).all()
        return api_result(status_code=1, data={
            "result": serializer(
                pim_leave_work_hand_type,
                exclude=[
                    "user_id", "spec", "extend", "created_at","updated_at"]
            )
        })
    except Exception as e:
        logger.error(e)


# 获取请假交接人
@main.route("/pim_api/leave_receiver", methods=['POST'])
def leave_receiver():
    session = get_session()
    try:
        pim_leave_receiver = session.query(PimLeaveReceiver).all()
        return api_result(status_code=1, data={"result": serializer(pim_leave_receiver,
                                                                    exclude=["user_id", "spec", "extend", "created_at",
                                                                             "updated_at"])})
    except Exception as e:
        logger.error(e)


# 获取请假类型
@main.route("/pim_api/leave_type", methods=['POST'])
def leave_type():
    session = get_session()
    try:
        pim_leave_type = session.query(PimLeaveType).all()
        return api_result(status_code=1, data={
            "result": serializer(pim_leave_type, exclude=["user_id", "spec", "extend", "created_at", "updated_at"])})
    except Exception as e:
        logger.error(e)


# 获取请假记录
@main.route("/pim_api/leave_record", methods=['POST'])
def leave_record():
    request_data = request.get_json()
    if 'user_id' in request_data:
        try:
            pimleave = PimLeave.query.filter_by(user_id=request_data['user_id']).order_by(PimLeave.created_at.desc())
            pagnator = PagenatorFlaskSqlalchemy(request_data=request_data, queryset=pimleave)
            querysetlist, total_number, total_page = pagnator.paging()

            task_context = []
            for task in querysetlist:
                logger.info(task)
                task_context.append({'leave_id': task.leave_id,
                                     'leave_type_id': task.leave_type_id,
                                     'leave_type': task.leave_type.leave_type,
                                     'create_time': str(task.start_time.strftime('%Y/%m/%d %H:%M'))
                                                    + '--'+str(task.end_time.strftime('%Y/%m/%d %H:%M')),
                                     'leave_reason': task.leave_reason,
                                     'result': task.result})
            resp = {'total_number': total_number, 'total_page': total_page, 'result': task_context}
            return api_result(status_code=1, data=resp)
        except Exception as e:
            logger.error(e)

    return api_result(status_code=0, message=messages.user_not_found)



# 获取验布报告
@main.route("/pim_api/check_cloth_report", methods=['POST'])
def check_cloth_report():
    request_data = request.get_json()
    session = get_session()
    try:
        datetimestr = request_data['datetime']
        cyli_num = request_data['cyli_num']
        datetimeformat = DateTimeFormat(datetimestr)
        datetime = datetimeformat.date2ymd2datetime()
        page_size = request_data["page_size"]
        page_index = request_data["page_index"]
        reportSQL = "select * from pim_report WHERE pim_report.user_id = '" + request_data["user_id"] + "' AND pim_report.date_time BETWEEN '" + datetime[0] + "' AND '" + datetime[1] + "'"
        if cyli_num:
            reportSQL = "select * from pim_report WHERE pim_report.user_id = '" + request_data["user_id"] + "' AND pim_report.date_time BETWEEN '" + datetime[0] + "' AND '" + datetime[1] + "' AND pim_report.cyli_num = '" + request_data["cyli_num"] + "'"
        if page_size == '' and page_index == '':
            page_index = 1
            page_size = 7
        reportlimit = "LIMIT %s" %(int(page_size))+" OFFSET %s" %((int(page_index)-1))+";"
        test1 = session.execute(reportSQL)
        test2 = session.execute(reportSQL+reportlimit)
        total_number = len(test1.fetchall())
        querysetlist = test2.fetchall()
        total_page = math.ceil(int(total_number) / int(page_size))
        # report = PimReport.query.filter_by(user_id=request_data['user_id']). \
        #     filter(PimReport.date_time.between(datetime[0], datetime[1])).filter(PimReport.report_type == 1)
        # if cyli_num:
        #     report = report.filter(PimReport.cyli_num == cyli_num)
        # pagnator = PagenatorFlaskSqlalchemy(request_data=request_data, queryset=report)
        # querysetlist, total_number, total_page = pagnator.paging()
        if querysetlist:
            result = []
            for report in querysetlist:
                result.append(
                    {'check_cloth_report_id': report.report_id, 'check_cloth_report_pdf': url_host + report.pdf_url})
                resp = {'total_number': total_number, 'total_page': total_page, 'result': result}
            return api_result(status_code=1, data=resp)
        return api_result(status_code=0, message=messages.user_not_found)
    except Exception as e:
        logger.error(e)


# 更新验布报告
@main.route("/pim_api/update_check_cloth_report", methods=['POST'])
def update_check_cloth_report():
    pass
    # TODO:
    return


# 打印验布报告
@main.route("/pim_api/print_check_cloth_report", methods=['POST'])
def print_check_cloth_ceport():
    pass
    # TODO:
    return


# 获取抽检批报
@main.route("/pim_api/spot_check_report", methods=['POST'])
def spot_check_report():
    request_data = request.get_json()
    try:
        datetimestr = request_data['datetime']
        cyli_num = request_data['cyli_num']
        datetimeformat = DateTimeFormat(datetimestr)
        datetime = datetimeformat.date2ymd2datetime()
        report = PimReport.query.filter_by(user_id=request_data['user_id']). \
            filter(PimReport.date_time.between(datetime[0], datetime[1])).filter(PimReport.report_type == 2)
        if cyli_num:
            report = report.filter(PimReport.cyli_num == cyli_num)
        pagnator = PagenatorFlaskSqlalchemy(request_data=request_data, queryset=report)
        querysetlist, total_number, total_page = pagnator.paging()
        if querysetlist:
            result = []
            for report in querysetlist:
                result.append(
                    {'check_cloth_report_id': report.report_id, 'check_cloth_report_pdf': url_host + report.pdf_url})
            resp = {'total_number': total_number, 'total_page': total_page, 'result': result}
            return api_result(status_code=1, data=resp)
        return api_result(status_code=0, message=messages.user_not_found)
    except Exception as e:
        logger.error(e)


# 更新抽检批报
@main.route("/pim_api/update_spot_check_report", methods=['POST'])
def update_spot_check_report():
    pass
    # TODO:
    return


# 打印抽检批报
@main.route("/pim_api/print_spot_check_report", methods=['POST'])
def print_spot_check_report():
    pass
    # TODO:
    return


# 获取抽检日报
@main.route("/pim_api/spot_check_daily", methods=['POST'])
def spot_check_daily():
    request_data = request.get_json()
    try:
        datetimestr = request_data['datetime']
        cyli_num = request_data['cyli_num']
        datetimeformat = DateTimeFormat(datetimestr)
        datetime = datetimeformat.date2ymd2datetime()
        report = PimReport.query.filter_by(user_id=request_data['user_id']). \
            filter(PimReport.date_time.between(datetime[0], datetime[1])).filter(PimReport.report_type == 3)
        if cyli_num:
            report = report.filter(PimReport.cyli_num == cyli_num)
        pagnator = PagenatorFlaskSqlalchemy(request_data=request_data, queryset=report)
        querysetlist, total_number, total_page = pagnator.paging()
        if querysetlist:
            result = []
            for report in querysetlist:
                result.append(
                    {'check_cloth_report_id': report.report_id, 'check_cloth_report_pdf': url_host + report.pdf_url})
            resp = {'total_number': total_number, 'total_page': total_page, 'result': result}
            return api_result(status_code=1, data=resp)
        return api_result(status_code=0, message=messages.user_not_found)
    except Exception as e:
        logger.error(e)


# 更新抽检日报
@main.route("/pim_api/update_spot_check_daily", methods=['POST'])
def update_spot_check_daily():
    pass
    # TODO:
    return


# 打印抽检日报
@main.route("/pim_api/print_spot_check_daily", methods=['POST'])
def print_spot_check_daily():
    pass
    # TODO:
    return


# 请假流程
@main.route("/pim_api/my_leave_proce", methods=['POST'])
def my_leave_proce():
    pass
    # TODO:
    return


# 获取扫描编码号基本信息
@main.route("/pim_api/qrcode_info", methods=['POST'])
def qrcode_info():
    request_data = request.get_json()
    try:
        clothInfo = PimClothInfo.query.filter_by(user_id=request_data['user_id']). \
            filter(PimClothInfo.code_number == request_data['code_number']).all()
        if clothInfo:
            return api_result(status_code=1, data={"result": serializer(clothInfo,
                                                             exclude=["spec", "extend", "code_number", "created_at",
                                                                      "updated_at"])})
        return api_result(status_code=0, message=messages.user_not_found)
    except Exception as e:
        logger.error(e.args)


# 获取疵点类型
@main.route("/pim_api/defect_type", methods=['POST'])
def defect_type():
    try:
        pim_defect_type = PimDefectType.query.filter_by().all()
        return api_result(status_code=1, data={
            'result': serializer(pim_defect_type, exclude=["user_id", "spec", "extend", "created_at", "updated_at"])})
    except Exception as e:
        logger.error(e)


# 获取位置类型
@main.route("/pim_api/location_type", methods=['POST'])
def location_type():
    try:
        pim_location_type = PimLocationType.query.filter_by().all()
        return api_result(status_code=1, data={
            'result': serializer(pim_location_type, exclude=["user_id", "spec", "extend", "created_at", "updated_at"])})
    except Exception as e:
        logger.error(e)


# 获取大小类型
@main.route("/pim_api/size", methods=['POST'])
def size():
    try:
        pim_size = PimSize.query.filter_by().all()
        return api_result(status_code=1, data={
            'result': serializer(pim_size, exclude=["user_id", "spec", "extend", "created_at", "updated_at"])})
    except Exception as e:
        logger.error(e)


# 获取疵点的信息
@main.route("/pim_api/defect_info", methods=['POST'])
def defect_info():
    request_data = request.get_json()
    try:
        defectInfo = PimDefect.query.filter_by(user_id=request_data['user_id']). \
            filter(PimDefect.code_number == request_data['code_number']).order_by(PimDefect.created_at.desc()).all()
        if defectInfo:
            resp = serializer(defectInfo,
                              exclude=["user_id", "spec", "extend", "code_number",
                                       "updated_at", "location_id", "size_id", "defect_type_id"],
                              exclude_dict={
                                  "defect_type": ["user_id", "spec", "extend", "code_number", "created_at", "updated_at",
                                                  "size"],
                                  "location": ["user_id", "spec", "extend", "code_number", "created_at", "updated_at"],
                                  "size": ["user_id", "spec", "extend", "code_number", "created_at", "updated_at"]})
            return api_result(status_code=1, data={'result': resp})
        return api_result(status_code=0, message=messages.user_not_found)
    except Exception as e:
        logger.error(e)


# 添加,修改,删除疵点的信息
@main.route("/pim_api/addORupdate_defect_info", methods=['POST'])
def add_or_update_or_defect_info():
    '''
    # 添加,修改,删除疵点的信息
    # tyep: 0==删除,1==添加,2==修改
    '''
    request_data = request.get_json()
    try:
        session = get_session()
        if int(request_data['type']) == 1:
            del request_data['type']
            del request_data['defect_info_id']
            add_pimdefect = PimDefect(**request_data)
            add_pimdefect.save(session)
            return api_result(status_code=1, data={"message": messages.status_ok})
        elif int(request_data['type']) == 0:
            add_pimdefect = session.query(PimDefect).filter_by(user_id=request_data['user_id']). \
                filter(PimDefect.defect_info_id == request_data['defect_info_id']).first()
            if add_pimdefect:
                add_pimdefect.delete(session)
                return api_result(status_code=1, data={"message": messages.status_ok})
        else:
            update_pimdefect = session.query(PimDefect).filter_by(user_id=request_data['user_id']). \
                filter(PimDefect.defect_info_id == request_data['defect_info_id']).first()
            if update_pimdefect:
                del request_data['type']
                del request_data['user_id']
                del request_data['defect_info_id']
                update_pimdefect.update(request_data)
                update_pimdefect.save(session)
                return api_result(status_code=1, data={"message": messages.status_ok})
    except Exception as e:
        logger.error(e)


# 保存验布文本框输入信息
@main.route("/pim_api/save_input_info", methods=['POST'])
def save_input_info():
    request_data = request.get_json()
    try:
        session = get_session()
        if request_data["user_id"] and request_data['code_number']:
            add_saveinputinfo = session.query(PimSaveInputInfo).filter_by(user_id=request_data["user_id"]). \
                filter(PimSaveInputInfo.code_number == request_data["code_number"]).first()
            if not add_saveinputinfo:
                add_saveinputinfo = PimSaveInputInfo(**request_data)
                add_saveinputinfo.save(session)
                return api_result(status_code=1, data={'input_infoId': add_saveinputinfo.input_info_id})
            return api_result(status_code=0, message=messages.exist_params)
        return api_result(status_code=0, message=messages.wrong_params)
    except Exception as e:
        logger.error(e)


# 获取验布文本框输入信息(此接口暂时没用到)
@main.route("/pim_api/input_info", methods=['POST'])
def input_info():
    request_data = request.get_json()
    try:
        saveinputinfo = PimSaveInputInfo.query.filter_by(user_id=request_data["user_id"]). \
            filter(PimSaveInputInfo.input_info_id == request_data["input_info_id"]).all()
        if saveinputinfo:
            return api_result(status_code=1, data={'result': serializer(saveinputinfo, exclude=['spec', 'extend'])})
        return api_result(status_code=0, message=messages.user_not_found)
    except Exception as e:
        logger.error(e)


# 码米
@main.route("/pim_api/ym_is_default", methods=['POST'])
def ym_is_default():
    '''
     Y == 米, M == 码, is_default: == 'true/false'
    '''
    try:
        resp = {"code": "y", "codename": "米", "is_default": "true"}
        # resp ={"code": "m", "codename": "码", "is_default": "false"}
        return api_result(status_code=1, data=resp)
    except Exception as e:
        logger.error(e)
