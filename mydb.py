# DB code
from flask_sqlalchemy import SQLAlchemy

from .__init__ import db



class UserTable(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4096))
    user_id = db.Column(db.String(4096))
    authkey = db.Column(db.String(4096))
    login = db.Column(db.Integer)
    read_access = db.Column(db.Integer)
    write_access = db.Column(db.Integer)

    def __init__(self, name, user_id, authkey, login, read_access, write_access):
        self.name = name
        self.user_id = user_id
        self.authkey = authkey
        self.login = login
        self.read_access = read_access
        self.write_access = write_access


def delete_all():
    try:
        db.session.query(UserTable).delete()
        db.session.commit()
        print("Delete all")
    except Exception as e:
        print("Failed " + str(e))
        db.session.rollback()


def get_user_row_if_exists(user_id):
    get_user_row = UserTable.query.filter_by(user_id=user_id).first()
    if get_user_row is not None:
        return get_user_row
    else:
        print("That user does not exist")
        return False


def add_user_and_login(name, user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.login = 1
        db.session.commit()
    else:
        print("Adding user " + name)
        new_user = UserTable(name, user_id, None, 1, 0, 0)
        db.session.add(new_user)
        db.session.commit()


def user_logout(user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.login = 0
        db.session.commit()
        print("User " + row.name + " logged out")


def add_auth_key(user_id, auth_key):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.authkey = auth_key
        db.session.commit()
        print("User " + row.name + "authkey added")


def get_auth_key(user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        return row.authkey
    else:
        print("User with id: " + user_id + " doesn't exist")


def view_all():
    row = UserTable.query.all()
    for n in range(0, len(row)):
        print(str(row[n].id) + " | " +
                row[n].name + " | " +
                str(row[n].user_id) + " | " +
                str(row[n].authkey) + " | " +
                str(row[n].login))


def get_all_logged_in_users():
    row = UserTable.query.filter_by(login=1).all()
    online_user_record = {"user_record": []}
    print("Logged in users: ")
    for n in range(0, len(row)):
        if row[n].read_access:
            read = "checked"
        else:
            read = "unchecked"
        if row[n].write_access:
            write = "checked"
        else:
            write = "unchecked"
        online_user_record["user_record"].append([row[n].name, row[n].user_id, read, write])
        print(str(row[n].id) + " | " +
                row[n].name + " | " +
                str(row[n].user_id) + " | " +
                str(row[n].authkey) + " | " +
                str(row[n].login))
    return online_user_record


def bool_to_int(v):
    if 'true' in str(v):
        return 1
    elif 'false' in str(v):
        return 0
    else:
        raise ValueError


def add_user_permission(user_id, read, write):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.read_access = bool_to_int(read)
        row.write_access = bool_to_int(write)
        db.session.commit()

def get_user_access(user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        get_user_row = UserTable.query.filter_by(user_id=user_id).first()
        read = get_user_row.read_access
        if read == 1:
            read = True
        else:
            read = False
        write = get_user_row.write_access
        if write == 1:
            write = True
        else:
            write = False
    return read, write

