# class ReplicaRouter:
#     """
#     Use the primary database for all reads and writes
#     until the replica is synchronized.
#     """

#     def db_for_read(self, model, **hints):
#         return "default"

#     def db_for_write(self, model, **hints):
#         return "default"

#     def allow_relation(self, obj1, obj2, **hints):
#         db1 = obj1._state.db
#         db2 = obj2._state.db

#         if db1 and db2 and db1 != db2:
#             return False

#         return True
#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         return db == "default"
