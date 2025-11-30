from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QListWidget, QListWidgetItem, QDialog, 
                             QLineEdit, QComboBox, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

from .database import init_db, add_task, get_due_tasks, complete_task, get_completed_tasks, delete_task, update_task, add_person, get_people, delete_person
from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme

"""
Task Board Application Module.

This module handles the Task Board. It helps you track what needs to be done.
"""

class TaskBoardApp(QWidget):
    """
    The main view for the Task Board.

    It shows your tasks and lets you add new ones.
    """
    def __init__(self, language_manager=None):
        """Sets up the task board, loads your tasks, and gets the UI ready."""
        super().__init__()
        self.language_manager = language_manager
        init_db()
        self.res_manager = ResolutionManager()
        self.show_completed = False
        self.setup_ui()
        
        title = "Task Board"
        if self.language_manager:
            title = self.language_manager.translate("task_board", "Task Board")
        self.setWindowTitle(title)
        
        self.refresh_tasks()

    def setup_ui(self):
        """
        Builds the UI, including the header and the task list.
        """
        # Set background to ensure previews are not white
        self.setStyleSheet(f"background-color: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(self.res_manager.scale(15))
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(self.res_manager.scale(15))
        
        self.title_label = QLabel()
        title_font = self.res_manager.scale(24)
        self.title_label.setStyleSheet(f"font-size: {title_font}px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        header_layout.addWidget(self.title_label)
        
        btn_width = self.res_manager.scale(160)
        btn_height = self.res_manager.scale(60)
        btn_font = self.res_manager.scale(18)
        btn_radius = self.res_manager.scale(10)
        
        # Manage People Button
        people_text = "People"
        if self.language_manager:
            people_text = self.language_manager.translate("people_management", "People")
            
        self.people_btn = QPushButton(people_text)
        self.people_btn.setFixedSize(btn_width, btn_height)
        self.people_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #9C27B0; 
                color: white; 
                font-size: {btn_font}px; 
                border-radius: {btn_radius}px;
            }}
            QPushButton:hover {{
                background-color: #7B1FA2;
            }}
        """)
        self.people_btn.clicked.connect(self.open_people_manager)
        header_layout.addWidget(self.people_btn)

        self.add_btn = QPushButton()
        self.add_btn.setFixedSize(btn_width, btn_height)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4CAF50; 
                color: white; 
                font-size: {btn_font}px; 
                border-radius: {btn_radius}px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.add_btn.clicked.connect(self.open_add_task_dialog)
        header_layout.addWidget(self.add_btn)

        self.completed_btn = QPushButton()
        self.completed_btn.setCheckable(True)
        self.completed_btn.setFixedSize(btn_width, btn_height)
        self.completed_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2196F3; 
                color: white; 
                font-size: {btn_font}px; 
                border-radius: {btn_radius}px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
            QPushButton:checked {{
                background-color: #1565C0;
                border: 2px solid #90CAF9;
            }}
        """)
        self.completed_btn.clicked.connect(self.toggle_completed_tasks)
        header_layout.addWidget(self.completed_btn)
        
        layout.addLayout(header_layout)
        
        # Task List
        self.task_list = QListWidget()
        self.task_list.setSpacing(self.res_manager.scale(10)) # Spacing between items
        self.task_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
            QListWidget::item:selected {{
                background-color: transparent;
            }}
            QListWidget::item:hover {{
                background-color: transparent;
            }}
        """)
        layout.addWidget(self.task_list)

        self.update_texts()
        if self.language_manager:
            self.language_manager.language_changed.connect(self.update_texts)

    def update_texts(self, lang_code=None):
        """Updates UI texts based on current language."""
        title = "Task Board"
        add_text = "+ Add Task"
        comp_text = "Show Completed"
        
        if self.language_manager:
            title = self.language_manager.translate("task_board", "Task Board")
            add_text = self.language_manager.translate("add_task", "+ Add Task")
            comp_text = self.language_manager.translate("show_completed", "Show Completed")
            
        self.setWindowTitle(title)
        self.title_label.setText(title)
        self.add_btn.setText(add_text)
        self.completed_btn.setText(comp_text)
        
        people_text = "People"
        if self.language_manager:
            people_text = self.language_manager.translate("people_management", "People")
        self.people_btn.setText(people_text)
        
        self.refresh_tasks()

    def refresh_tasks(self):
        """
        Reloads tasks from the database. It separates them into 'due' and 
        'completed'.
        """
        self.task_list.clear()
        
        # Due Tasks
        tasks = get_due_tasks()
        for task in tasks:
            self.add_task_item(task, is_completed=False)

        # Completed Tasks
        if self.show_completed:
            completed_tasks = get_completed_tasks()
            for task in completed_tasks:
                self.add_task_item(task, is_completed=True)

    def add_task_item(self, task, is_completed):
        """
        Creates a widget for a single task and adds it to the list.

        Args:
            task (dict): The task data.
            is_completed (bool): Whether the task is done.
        """
        item = QListWidgetItem(self.task_list)
        widget = TaskItemWidget(
            task, 
            self.on_task_complete, 
            self.on_task_edit,
            self.on_task_delete,
            is_completed=is_completed, 
            res_manager=self.res_manager,
            language_manager=self.language_manager
        )
        item.setSizeHint(widget.sizeHint())
        self.task_list.setItemWidget(item, widget)

    def open_people_manager(self):
        dialog = ManagePeopleDialog(self, self.language_manager)
        dialog.exec()

    def on_task_edit(self, task):
        dialog = AddTaskDialog(self, task, self.language_manager)
        if dialog.exec():
            self.refresh_tasks()

    def on_task_delete(self, task_id):
        title = "Delete Task"
        msg = "Are you sure you want to delete this task?"
        if self.language_manager:
            title = self.language_manager.translate("delete_task", title)
            msg = self.language_manager.translate("delete_task_confirm", msg)
            
        reply = QMessageBox.question(
            self, title, msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_task(task_id)
            self.refresh_tasks()

    def toggle_completed_tasks(self):
        self.show_completed = self.completed_btn.isChecked()
        self.refresh_tasks()

    def on_task_complete(self, task_id):
        # Check if we need to ask "Who are you?"
        # We need to know the task details first. 
        # Since we don't have the task object here easily (only ID), let's fetch it or pass it.
        # Actually, complete_task in DB handles logic, but we need UI for person selection if needed.
        # For now, let's just show a dialog to select person if there are people.
        
        people = get_people()
        if not people:
            # No people defined, just complete it
            complete_task(task_id)
            self.refresh_tasks()
            return

        # Ask who is completing it
        dialog = WhoAreYouDialog(self, people, self.language_manager)
        if dialog.exec():
            person_id = dialog.get_selected_person_id()
            complete_task(task_id, person_id)
            self.refresh_tasks()

    def open_add_task_dialog(self):
        dialog = AddTaskDialog(self, task=None, language_manager=self.language_manager)
        if dialog.exec():
            self.refresh_tasks()

class TaskItemWidget(QFrame):
    """
    A widget for a single task.

    It shows details and has buttons to edit, delete, or complete it.
    """
    def __init__(self, task, complete_callback, edit_callback, delete_callback, is_completed=False, res_manager=None, language_manager=None):
        super().__init__()
        self.task = task
        self.complete_callback = complete_callback
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        self.is_completed = is_completed
        self.res_manager = res_manager or ResolutionManager()
        self.language_manager = language_manager
        
        # Styled Frame
        self.setObjectName("TaskItem")
        bg_color = "rgba(255, 255, 255, 0.05)" if not is_completed else "rgba(255, 255, 255, 0.02)"
        border_color = "rgba(255, 255, 255, 0.1)"
        
        self.setStyleSheet(f"""
            #TaskItem {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {self.res_manager.scale(10)}px;
            }}
            #TaskItem:hover {{
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        """)

        layout = QHBoxLayout(self)
        padding = self.res_manager.scale(15)
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(self.res_manager.scale(15))
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(self.res_manager.scale(5))
        
        name_font = self.res_manager.scale(18)
        name_label = QLabel(task['name'])
        if self.is_completed:
            # Improved readability for completed tasks
            name_label.setStyleSheet(f"font-size: {name_font}px; font-weight: bold; text-decoration: line-through; color: #888;")
        else:
            name_label.setStyleSheet(f"font-size: {name_font}px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        
        
        details_font = self.res_manager.scale(14)
        
        # Assignment Text
        assign_text = ""
        atype = task.get('assignment_type', 'specific')
        aval = task.get('assignment_value')
        
        if atype == 'all':
            assign_text = "All People"
            if self.language_manager:
                assign_text = self.language_manager.translate("all_people", "All People")
        elif atype == 'any_n':
            assign_text = f"Any {aval} People"
            if self.language_manager:
                assign_text = self.language_manager.translate("any_n_people", "Any N People").replace("N", str(aval))
        else:
            # Specific
            # We need to resolve IDs to names ideally, but for now let's just show "Specific" or try to parse if we had names.
            # In DB we stored IDs. We might want to fetch names or just show "Specific People".
            assign_text = "Specific People" 
            if self.language_manager:
                assign_text = self.language_manager.translate("specific_people", "Specific People")

        freq_lbl = "Frequency"
        if self.language_manager:
            freq_lbl = self.language_manager.translate("frequency", freq_lbl)
            
        # Completion Status
        status_text = ""
        if not is_completed:
            req = task.get('required_completions', 1)
            curr = task.get('current_completions', 0)
            if req > 1:
                status_text = f" | {curr}/{req}"
        
        details_label = QLabel(f"{assign_text} | {freq_lbl}: {task['frequency']}{status_text}")
        details_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: {details_font}px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(details_label)
        layout.addLayout(info_layout)
        
        # Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(self.res_manager.scale(10))
        btn_layout.setContentsMargins(0, 0, 0, 0)

        # Edit Button
        edit_text = "Edit"
        if self.language_manager:
            edit_text = self.language_manager.translate("edit", edit_text)
        edit_btn = QPushButton(edit_text)
        edit_btn.setFixedSize(self.res_manager.scale(80), self.res_manager.scale(50))
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFC107;
                color: black;
                font-size: {self.res_manager.scale(16)}px;
                border-radius: {self.res_manager.scale(8)}px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #FFB300;
            }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_callback(task))
        btn_layout.addWidget(edit_btn)

        # Delete Button
        del_text = "Del"
        if self.language_manager:
            del_text = self.language_manager.translate("del", del_text)
        delete_btn = QPushButton(del_text)
        delete_btn.setFixedSize(self.res_manager.scale(80), self.res_manager.scale(50))
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #F44336;
                color: white;
                font-size: {self.res_manager.scale(16)}px;
                border-radius: {self.res_manager.scale(8)}px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #D32F2F;
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_callback(task['id']))
        btn_layout.addWidget(delete_btn)

        # Complete Button
        if not self.is_completed:
            done_text = "Done"
            if self.language_manager:
                done_text = self.language_manager.translate("done", done_text)
            done_btn = QPushButton(done_text)
            done_btn.setFixedSize(self.res_manager.scale(100), self.res_manager.scale(50))
            done_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #2196F3;
                    color: white;
                    font-size: {self.res_manager.scale(16)}px;
                    border-radius: {self.res_manager.scale(8)}px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: #1976D2;
                }}
            """)
            done_btn.clicked.connect(lambda: self.complete_callback(task['id']))
            btn_layout.addWidget(done_btn)
        
        layout.addLayout(btn_layout)

class AddTaskDialog(QDialog):
    """
    A popup dialog for creating or editing a task.
    """
    def __init__(self, parent=None, task=None, language_manager=None):
        super().__init__(parent)
        self.language_manager = language_manager
        self.res_manager = ResolutionManager()
        self.task = task
        
        title = "Edit Task" if task else "Add New Task"
        if self.language_manager:
            if task:
                title = self.language_manager.translate("edit", "Edit")
            else:
                title = self.language_manager.translate("add_task", "Add Task").replace("+ ", "")
        self.setWindowTitle(title)
        
        width = self.res_manager.scale(500)
        height = self.res_manager.scale(600)
        self.setFixedSize(width, height)
        
        self.setStyleSheet(f"background-color: #2b2b2b; color: {Theme.TEXT_PRIMARY}; font-size: {self.res_manager.scale(16)}px;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(self.res_manager.scale(15))
        
        # Name
        lbl_name = "Task Name:"
        if self.language_manager:
            lbl_name = self.language_manager.translate("task_name", "Task Name") + ":"
        layout.addWidget(QLabel(lbl_name))
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(f"padding: {self.res_manager.scale(5)}px; font-size: {self.res_manager.scale(16)}px;")
        layout.addWidget(self.name_input)
        
        # Assignment Type
        lbl_assign = "Assignment Type:"
        if self.language_manager:
            lbl_assign = self.language_manager.translate("assignment_type", "Assignment Type") + ":"
        layout.addWidget(QLabel(lbl_assign))
        
        self.assign_type_combo = QComboBox()
        types = [
            ("Specific People", "specific"),
            ("Any N People", "any_n"),
            ("All People", "all")
        ]
        for label, data in types:
            trans_label = label
            if self.language_manager:
                if data == "specific": trans_label = self.language_manager.translate("specific_people", label)
                elif data == "any_n": trans_label = self.language_manager.translate("any_n_people", label).replace("N", "N")
                elif data == "all": trans_label = self.language_manager.translate("all_people", label)
            self.assign_type_combo.addItem(trans_label, data)
            
        self.assign_type_combo.setStyleSheet(f"padding: {self.res_manager.scale(5)}px; font-size: {self.res_manager.scale(16)}px;")
        self.assign_type_combo.currentIndexChanged.connect(self.update_assignment_ui)
        layout.addWidget(self.assign_type_combo)
        
        # Dynamic Assignment UI Container
        self.assign_container = QWidget()
        self.assign_layout = QVBoxLayout(self.assign_container)
        self.assign_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.assign_container)
        
        # Frequency
        lbl_freq = "Frequency:"
        if self.language_manager:
            lbl_freq = self.language_manager.translate("frequency", "Frequency") + ":"
        layout.addWidget(QLabel(lbl_freq))
        self.freq_input = QComboBox()
        self.freq_input.addItems(["Daily", "Weekly", "Every 3 Days"])
        self.freq_input.setEditable(True) 
        self.freq_input.setStyleSheet(f"padding: {self.res_manager.scale(5)}px; font-size: {self.res_manager.scale(16)}px;")
        layout.addWidget(self.freq_input)

        # Pre-fill if editing
        if self.task:
            self.name_input.setText(self.task['name'])
            self.freq_input.setCurrentText(self.task['frequency'])
            
            atype = self.task.get('assignment_type', 'specific')
            index = self.assign_type_combo.findData(atype)
            if index >= 0:
                self.assign_type_combo.setCurrentIndex(index)
        
        self.update_assignment_ui()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(self.res_manager.scale(10))
        
        save_text = "Save"
        cancel_text = "Cancel"
        if self.language_manager:
            save_text = self.language_manager.translate("save", save_text)
            cancel_text = self.language_manager.translate("cancel", cancel_text)
            
        save_btn = QPushButton(save_text)
        save_btn.clicked.connect(self.save_task)
        save_btn.setStyleSheet(f"background-color: #4CAF50; color: white; padding: {self.res_manager.scale(10)}px; border-radius: {self.res_manager.scale(5)}px;")
        
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"background-color: #f44336; color: white; padding: {self.res_manager.scale(10)}px; border-radius: {self.res_manager.scale(5)}px;")
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def update_assignment_ui(self):
        # Clear existing
        while self.assign_layout.count():
            item = self.assign_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        atype = self.assign_type_combo.currentData()
        people = get_people()
        
        if atype == 'specific':
            # Checkboxes for each person
            self.people_checks = []
            for person in people:
                chk = QCheckBox(person['name'])
                chk.setProperty('person_id', person['id'])
                self.assign_layout.addWidget(chk)
                self.people_checks.append(chk)
                
                # Pre-check if editing
                if self.task and self.task.get('assignment_type') == 'specific':
                    # assignment_value is string of IDs like "1,2"
                    ids = str(self.task.get('assignment_value', '')).split(',')
                    if str(person['id']) in ids:
                        chk.setChecked(True)
                        
        elif atype == 'any_n':
            # Number spinner
            lbl = QLabel("Number of People:")
            if self.language_manager:
                lbl.setText(self.language_manager.translate("number_of_people", "Number of People") + ":")
            self.assign_layout.addWidget(lbl)
            
            self.n_spinner = QSpinBox()
            self.n_spinner.setMinimum(1)
            self.n_spinner.setMaximum(len(people) if people else 1)
            self.assign_layout.addWidget(self.n_spinner)
            
            if self.task and self.task.get('assignment_type') == 'any_n':
                try:
                    self.n_spinner.setValue(int(self.task.get('assignment_value', 1)))
                except:
                    pass

    def save_task(self):
        name = self.name_input.text().strip()
        if not name:
            msg = "Task name cannot be empty"
            if self.language_manager:
                msg = self.language_manager.translate("task_name_empty", msg)
            QMessageBox.warning(self, "Error", msg)
            return
            
        atype = self.assign_type_combo.currentData()
        aval = None
        
        if atype == 'specific':
            selected_ids = [str(chk.property('person_id')) for chk in self.people_checks if chk.isChecked()]
            aval = ",".join(selected_ids)
        elif atype == 'any_n':
            aval = str(self.n_spinner.value())
            
        frequency = self.freq_input.currentText()
        
        if self.task:
            update_task(self.task['id'], name, atype, aval, frequency)
        else:
            add_task(name, atype, aval, frequency)
        self.accept()

class ManagePeopleDialog(QDialog):
    def __init__(self, parent=None, language_manager=None):
        super().__init__(parent)
        self.language_manager = language_manager
        self.res_manager = ResolutionManager()
        
        title = "Manage People"
        if self.language_manager:
            title = self.language_manager.translate("people_management", "Manage People")
        self.setWindowTitle(title)
        
        self.setFixedSize(self.res_manager.scale(400), self.res_manager.scale(500))
        self.setStyleSheet(f"background-color: #2b2b2b; color: {Theme.TEXT_PRIMARY}; font-size: {self.res_manager.scale(16)}px;")
        
        layout = QVBoxLayout(self)
        
        # List
        self.people_list = QListWidget()
        self.people_list.setStyleSheet("background-color: rgba(255,255,255,0.05); border: none;")
        layout.addWidget(self.people_list)
        
        # Add Input
        input_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")
        input_layout.addWidget(self.name_input)
        
        add_btn = QPushButton("+")
        add_btn.setFixedSize(self.res_manager.scale(40), self.res_manager.scale(40))
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px;")
        add_btn.clicked.connect(self.add_person)
        input_layout.addWidget(add_btn)
        
        layout.addLayout(input_layout)
        
        # Delete Button
        del_btn = QPushButton("Delete Selected")
        if self.language_manager:
            del_btn.setText(self.language_manager.translate("delete_selected", "Delete Selected"))
        del_btn.setStyleSheet("background-color: #F44336; color: white; padding: 10px; border-radius: 5px;")
        del_btn.clicked.connect(self.delete_person)
        layout.addWidget(del_btn)
        
        self.refresh_list()
        
    def refresh_list(self):
        self.people_list.clear()
        people = get_people()
        for p in people:
            item = QListWidgetItem(p['name'])
            item.setData(Qt.ItemDataRole.UserRole, p['id'])
            self.people_list.addItem(item)
            
    def add_person(self):
        name = self.name_input.text().strip()
        if name:
            add_person(name)
            self.name_input.clear()
            self.refresh_list()
            
    def delete_person(self):
        item = self.people_list.currentItem()
        if item:
            pid = item.data(Qt.ItemDataRole.UserRole)
            delete_person(pid)
            self.refresh_list()

class WhoAreYouDialog(QDialog):
    def __init__(self, parent=None, people=None, language_manager=None):
        super().__init__(parent)
        self.language_manager = language_manager
        self.res_manager = ResolutionManager()
        self.people = people or []
        
        title = "Who are you?"
        if self.language_manager:
            title = self.language_manager.translate("who_are_you", "Who are you?")
        self.setWindowTitle(title)
        
        self.setStyleSheet(f"background-color: #2b2b2b; color: {Theme.TEXT_PRIMARY}; font-size: {self.res_manager.scale(16)}px;")
        
        layout = QVBoxLayout(self)
        
        lbl = QLabel("Select your name:")
        if self.language_manager:
            lbl.setText(self.language_manager.translate("select_your_name", "Select your name:"))
        layout.addWidget(lbl)
        
        self.combo = QComboBox()
        for p in self.people:
            self.combo.addItem(p['name'], p['id'])
        layout.addWidget(self.combo)
        
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(btn)
        
    def get_selected_person_id(self):
        return self.combo.currentData()




