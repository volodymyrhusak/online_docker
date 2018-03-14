# -*- coding:utf-8 -*-


from models.model import UserRelation

from models.base_manager import SNBaseManager

class UserRelationManager(SNBaseManager):


    def __init__(self):
        self.object = UserRelation()

    def addFriend(self,user,friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return
        if self.getFriend(user, friend):
            return
        self.object.user1 = user
        self.object.user2 = friend

        return self.saveFriends()

    def saveFriends(self):
        sql = self.insert_sql.format(self.object._name, self._sqlValues(self.insert_sql_values))
        return self._executeSQL(sql)

    def delFriend(self, user, friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return

        return self.delete().And([('user1','=',user),('user2','=',friend)])\
            .Or([('user1','=',friend),('user2','=',user)]).run()

    def getFriends(self, user):
        if not isinstance(user, int):
            return

        self.select().And([('user1','=',user)]).Or([('user2','=',user)]).run(all=True)

    def getFriend(self, user, friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return

        self.select().And([('user1', '=', user), ('user2', '=', friend)]) \
            .Or([('user1', '=', friend), ('user2', '=', user)]).run()


    def isFriend(self, user, friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return

        self.select().And([('user1', '=', user), ('user2', '=', friend)]) \
            .Or([('use1r', '=', friend), ('user2', '=', user)]).run()

        if self.object.id:
            return True
        return False

    def blockFriend(self,user, friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return

        relation = self.getFriend(user,friend)
        relation.object.block = 1
        relation.save()
