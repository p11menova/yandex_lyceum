class User_in:
    def __init__(self, user_id=0):
        self.user_in = False
        self.user_id = user_id

    def change_value(self, value):
        self.user_in = value

    def get_value(self):
        return self.user_in

    def change_user_id(self, id):
        self.user_id = id

    def get_user_id(self):
        return self.user_id