from typing import Dict

from tortoise import fields

from services.db_context import Model

from services.log import logger

from datetime import datetime,timedelta
import pytz

class UsersInfo(Model):

    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    user_qq = fields.BigIntField()
    """用户id"""
    group_id = fields.BigIntField()
    """群聊id"""
    body_price = fields.BigIntField(default=100)
    """身价"""
    checkin_time_last = fields.DatetimeField(auto_now_add=True,default=datetime.now(pytz.timezone('Asia/Shanghai')) - timedelta(days=12))
    """最后打工时间"""
    class Meta:
        table = "buy_users_info"
        table_description = "群友市场信息数据表"
        unique_together = ("user_qq", "group_id")

    @classmethod
    async def get_all_auser(cls, user_qq: int, group_id: int):
        """
        说明:
            获取所有奴隶
        参数:
            :param user_qq: qq号
            :param group_id: 所在群号
        """
        try:
            user = await BayUsers.filter(group_id=group_id,muser_qq=user_qq).exclude(auser_qq = 0).all()
        except Exception as e:
            logger.error(e)
            return None
        if user:
            ulist:dict[int, int]={}
            for i in user:
                auser, _ = await cls.get_or_create(user_qq=i.auser_qq, group_id=group_id)
                ulist[auser.user_qq]=auser.body_price
            return dict(sorted(ulist.items(), key=lambda item: item[1], reverse=True))
        return None

    @classmethod
    async def get_all_user(cls, group_id: int):
        """
        说明:
            获取所有群友
        参数:
            :param user_qq: qq号
            :param group_id: 所在群号
        """
        try:
            user = await cls.filter(group_id=group_id).all()
        except Exception as e:
            logger.error(e)
            return None
        if user:
            ulist: dict[int, int] = {i.user_qq: i.body_price for i in user[:80]}
            return dict(sorted(ulist.items(), key=lambda item: item[1], reverse=True))
        return None


    @classmethod
    async def work(cls, user_qq: int, group_id: int):
        """
        说明:
            打工
        参数:
            :param user_qq: qq号
            :param group_id: 所在群号
        """
        user, _ = await cls.get_or_create(user_qq=user_qq, group_id=group_id)
        user.checkin_time_last=datetime.now(pytz.timezone('Asia/Shanghai'))
        await user.save(update_fields=["checkin_time_last"])



    @classmethod
    async def add_user(cls, user_qq: int, group_id: int, auser_qq: int, num: int = 20):
        """
        说明:
            增加群友
        参数:
            :param user_qq: qq号
            :param group_id: 所在群号
            :param auser_qq: 群友qq
            :param num: 增加身价
        """
        user, _= await cls.get_or_create(user_qq=user_qq, group_id=group_id)
        user= await BayUsers.get_or_none(group_id=group_id,muser_qq=user_qq,auser_qq=auser_qq)
        if user:
            return None
        else:
            user, _= await BayUsers.get_or_create(group_id=group_id,muser_qq=user_qq,auser_qq=auser_qq)
            
        auser, _= await cls.get_or_create(user_qq=auser_qq, group_id=group_id)
        auser.body_price = auser.body_price+num
        await auser.save(update_fields=["body_price"])
        return auser.body_price - num
         
    @classmethod
    async def remove_user(cls, user_qq: int, group_id: int, auser_qq: int) -> bool:
        """
        说明:
            增加群友
        参数:
            :param user_qq: qq号
            :param group_id: 所在群号
            :param auser_qq: 群友qq
        """
        user, _= await cls.get_or_create(user_qq=user_qq, group_id=group_id)
        user= await BayUsers.get_or_none(group_id=group_id,muser_qq=user_qq,auser_qq=auser_qq)
        if not user:
            return False
        await user.delete()
        return True


        
class BayUsers(Model):

    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    group_id = fields.BigIntField()
    """群聊id"""
    muser_qq = fields.BigIntField(default=0)
    """主人id"""
    auser_qq = fields.BigIntField(default=0)
    """奴隶id"""

    class Meta:
        table = "buy_users"
        table_description = "群友市场关系数据表"
        unique_together = ("id", "group_id")
        
