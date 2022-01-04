from PyQt5.QtWidgets import QMainWindow
import sqlite3
from login_ui import Ui_MainWindow


class Login(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.log)

    def log(self):
        con = sqlite3.connect('login_db.db')
        cur = con.cursor()
        result = cur.execute("SELECT * FROM users WHERE name=?",
                             (self.lineEdit.text(),)).fetchall()
        if not result:
            cur.execute('INSERT INTO users(name, level, score, money) VALUES(?,0,0,10000)',
                        (self.lineEdit.text(),))
            name_id = cur.execute('SELECT id FROM users WHERE name=?',
                        (self.lineEdit.text(),)).fetchone()
            cur.execute('INSERT INTO passwords(id, password) VALUES(?,?)',
                        (name_id[0], self.lineEdit_2.text()))
            x = cur.execute('SELECT * FROM passwords WHERE id=?',
                            (name_id[0],)).fetchall()
            print(x)
            con.commit()
            self.close()
        else:
            password = cur.execute('SELECT password FROM passwords '
                                   'WHERE id=('
                                   'SELECT id FROM users '
                                   'WHERE name = ?)',
                                   (self.lineEdit.text(),)).fetchone()
            if str(password[0]) == self.lineEdit_2.text():
                cur.execute('UPDATE users SET score=0, level=0 WHERE name=?',
                            (self.lineEdit.text(),))
                con.commit()
                self.close()
            else:
                self.label_3.setText("Неправильный пароль")
