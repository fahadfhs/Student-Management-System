from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3
import mysql.connector


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        # creates the file and help buttons on the ---MENU BAR----
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # adds a sub item as Add Student under File menu
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)  # modified to add the icon for the
        # toolbar
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # adds sub item called About under Help
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        # line below is for mac computers
        # about_action.setMenuRole(QAction.MenuRole.NoRole)  # No role
        about_action.triggered.connect(self.about)

        # adds sub item called search under Edit
        search_section = QAction(QIcon("icons/search.png"), "Search", self)  # same modification as add_section
        search_section.triggered.connect(self.search)
        edit_menu_item.addAction(search_section)

        # since it as local variable we need to refer as self.
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)  # hides the index column in table
        # Since we're using the QMainWidow we have to specify a central main widget, in this case
        # we do that as the table
        self.setCentralWidget(self.table)

        # ----------creating a toolbar from instance and then adding it to main----------
        toolbar = QToolBar()
        toolbar.setMovable(True)  # user can move it around
        self.addToolBar(toolbar)  # adds toolbar to the self(main window)
        # adding the add and search actions
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_section)

        # ----------creating a status bar and add its elements----------------------
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # makes sure the edit and delete button are not added serially
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        # creating a connection variable and connecting with the database
        connection = DatabaseConnection().connect() # modified to use class to connect instead of repeated code
        # extracting the values and storing them in result, students is name of table
        result = connection.execute("SELECT * FROM students")
        # makes sure whenever loaded, duplicate data is not added on top of existing
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            # the function below created an empty row
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                # the function below populates the item in the created row(above)
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")

        content = """About Student Management System

    The Student Management System is a comprehensive software application designed to simplify
    the management of student records in educational institutions. This user-friendly system offers
    a seamless interface for educators and administrators to efficiently handle essential tasks
    related to student data. With this program, users can effortlessly add, search, edit, and delete
    student records, providing a centralized hub for maintaining accurate and up-to-date information."""

        self.setText(content)


class EditDialog(QDialog):  # similar to insert dialogue
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from the selected row
        index = main_window.table.currentRow()  # returns an integer
        student_name = main_window.table.item(index, 1).text()  # index from above and then index of the column after,

        # Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Adds the student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Adds the combo box widget
        course_name = main_window.table.item(index, 2).text()  # want the third column hence 2
        self.course_name = QComboBox()
        courses = ["Java Programming", "Python Programming", "Web Development", "Cloud Machine Learning",
                   "Data Structures and Algorithms", "Machine Learning", "Mobile App Development",
                   "Software Testing", "Cybersecurity", "Agile Software Development", "Math",
                   "Astronomy", "Biology", "Physics"]

        # shows the selected course item in the edit field when selected
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # shows the selected mobile item in the edit field
        mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a Update Button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)  # <---- changed to self.update here in this line
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect() # updated the code to connect using the class
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course= ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))

        connection.commit()  # commit because update and insert are write operations
        cursor.close()
        connection.close()
        # refreshing the table
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()  # message on top then yes and no on sec row
        confirmation = QLabel("Are you sure you want to delete this cell?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)  # passes on to delete student method
        no.clicked.connect(self.reject)  # Close the dialog when "No" is pressed

    def delete_student(self):
        # get selected index and student id from selected row
        index = main_window.table.currentRow()  # returns an integer
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()  # updated using class
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()  # refresh again

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The cell was deleted successfully!")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Adds the student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Adds the combo box widget
        self.course_name = QComboBox()
        courses = ["Java Programming", "Python Programming", "Web Development", "Cloud Machine Learning",
                   "Data Structures and Algorithms", "Machine Learning", "Mobile App Development",
                   "Software Testing", "Cybersecurity", "Agile Software Development", "Math",
                   "Astronomy", "Biology", "Physics"]

        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Adds the mobile Widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit Button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())  # item text as it is combo box
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect() # updated using class
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students(name, course, mobile) VALUES (?, ?, ?)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()  # refreshes the table and shows the updated data


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(150)

        layout = QVBoxLayout()  # vertical box layout

        # Adds the student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add a Search Button
        button = QPushButton("Search")
        button.clicked.connect(self.search_student)
        layout.addWidget(button)

        self.setLayout(layout)  # setting the layout

    def search_student(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()  # update the connection
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(items)
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
