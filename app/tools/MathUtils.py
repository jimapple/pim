from datetime import datetime
from app.models import PimTask
from app.tools.common import get_session

NOW = datetime.utcnow()


# 昨日工作评价
# 一天完成检验布匹数量/该日总的布匹任务数量
def yesterday_work_state(cel_species_count=None, yel_species_count=None):
    if yel_species_count == 0 or round(cel_species_count / yel_species_count, 2) < 0.8:
        return '您昨天表现不好哦，今天补回来哦！'
    elif round(cel_species_count / yel_species_count , 2) < 1 and round(cel_species_count / yel_species_count, 2) > 0.8:
        return '您昨天表现一般，今天加吧劲哦！'
    else:
        return '您昨天表现很好哦，继续加油哦！'


# 工作完成百分比
# 根据需要抽检布匹总长度和已经抽检总长度数量
# 核算工作完成百分比（已经抽检总长度/需要抽检总长度*100%），显示今天工作完成   0 %！
def work_complete_percent(complete_length=None, need_length=None):
    if need_length == 0:
        return 0
    return round(complete_length / need_length, 2) * 100


# 每小时工作效率显示
# 该小时验完的布匹数量/（本日工作总量/总工作时数）
def per_hour_efficiency(per_hour_species=None, today_work_count=None, total_work_count=None):
    if today_work_count == 0 or total_work_count == 0:
        return 0
    half = round(today_work_count / total_work_count, 3)
    return round(per_hour_species / half, 2) * 100


# 昨日一天完成检验布匹数量
# typeaccount=0 昨天一天完成检验布匹数量
# typeaccount=1 该日总的布匹任务数量
def yesterday_complete_species(userid, typeaccount=None):
    data = datetime.now()
    datetime(data.year, data.month, data.day - 1, 0, 0, 0)
    session = get_session()
    count = None

    if typeaccount == 0:
        count = session.query(PimTask).filter_by(user_id=userid).filter_by(work_status=3).filter(
            PimTask.updated_at.between(
                datetime(data.year, data.month, data.day - 1, 0, 0, 0),
                datetime(data.year, data.month, data.day, 0, 0, 0)
            )).count()

    elif typeaccount == 1:
        all_count = session.query(PimTask).filter_by(user_id=userid).count()
        yes_count_before = session.query(PimTask).filter_by(user_id=userid).filter_by(work_status=3).filter(
            PimTask.updated_at < datetime(data.year, data.month, data.day - 1, 0, 0, 0)).count()

        count = all_count - yes_count_before
    return count


# 核算工作完成百分比（已经抽检总长度/需要抽检总长度*100%)
def cel_check_length(userid, typeaccount=None):
    data = datetime.now()
    datetime(data.year, data.month, data.day - 1, 0, 0, 0)
    session = get_session()
    complete_total_specie = 0
    need_total_specie = 0

    # 已经抽检总长度
    if typeaccount == 0:
        complete_specie = session.query(PimTask).filter_by(user_id=userid).filter_by(work_status=3).all()
        if len(complete_specie) == 0:
            complete_total_specie = 0
        else:
            for specie in complete_specie:
                complete_total_specie += int(specie.volu_num.split('/')[1])
        return complete_total_specie
    # 需要抽检总长度
    elif typeaccount == 1:
        yes_all = session.query(PimTask).filter_by(user_id=userid).all()
        yes_complete = session.query(PimTask).filter_by(user_id=userid).filter_by(work_status=3).all()
        need_specie = list(set(yes_all)-set(yes_complete))
        if len(need_specie) == 0:
            need_total_specie = 0
        else:
            for specie in need_specie:
                need_total_specie += int(specie.volu_num.split('/')[1])
        return need_total_specie


# 该小时验完的布匹数量
def per_hour_species(userid=None, hour=None):
    data = datetime.now()

    count = PimTask.query.filter_by(user_id=userid).filter_by(work_status=3).filter(
        PimTask.updated_at.between(
            datetime(data.year, data.month, data.day, hour, 0, 0),
            datetime(data.year, data.month, data.day, hour + 1, 0, 0)
        )
    ).count()

    return count


# 获取工作鼓励
def work_encourage(username=None, userid=None, yesterday_work=None):
    now_hour = datetime.now().strftime('%H')
    all_title = {
        '01':'清晨好',
        '02':'清晨好',
        '03':'清晨好',
        '04':'清晨好',
        '05':'清晨好',
        '06':'早上好',
        '07':'早上好',
        '08':'早上好',
        '09':'上午好',
        '10':'上午好',
        '11':'上午好',
        '12':'中午好',
        '13':'下午好',
        '14':'下午好',
        '15':'下午好',
        '16':'下午好',
        '17':'下午好',
        '18':'晚上好',
        '19':'晚上好',
        '20':'晚上好',
        '21':'晚上好',
        '22':'晚上好',
        '23':'晚上好',
        '24':'晚上好'
    }

    # 现在的时间提示
    now_title = all_title.get(now_hour)
    # 所有完成的-包括昨天之前左右完成的
    all_count = PimTask.query.filter_by(user_id=userid).count()
    yes_count_before = PimTask.query.filter_by(user_id=userid).filter_by(work_status=3).filter(
        PimTask.updated_at < datetime(NOW.year, NOW.month, NOW.day, 0, 0, 0)).count()

    if yesterday_work is None:
        return_work = now_title + '!' + \
                      username + ',' + \
                      '新的一天开始，祝你开心工作!'
    else:
        if all_count > yes_count_before:
            return_work = now_title + '!' + \
                        username + ',' + \
                        '新的一天开始，祝你开心工作!' + \
                        yesterday_work + \
                        '您今天有以下工作要完成!'
        else:
            return_work = now_title + '!' + \
                      username + ',' + \
                      '新的一天开始，祝你开心工作!' + \
                      yesterday_work

    return return_work
