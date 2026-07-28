import sqlite3
import sys
from datetime import datetime
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from app_path import EMAIL_ATTACHMENT_FILE
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QPushButton, QRadioButton, QListWidget,
    QListWidgetItem, QTableWidget, QTableWidgetItem, QMessageBox, QLabel,
    QComboBox,QTabWidget
)
from PySide6.QtCore import Signal
from database.connection import main_db
from database.tables import create_table_logging, create_table_corrective_patch, create_table_analyst, create_table_coordinator
from database.create_user import create_coordinator, create_analyst, create_corrective_patch
from models.user_high_position import Coordinator
from models.user_analyst import Analyst
from automation.extract import extract_content  
from automation.email import send_email               


create_table_logging(main_db())
create_table_corrective_patch(main_db())
create_table_analyst(main_db())
create_table_coordinator(main_db())
def get_all_coordinators(db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM coordinator ORDER BY name")
    return cursor.fetchall()  # lista de tuplas (id, name)
 
 
def get_all_analysts(db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM analyst ORDER BY name")
    return cursor.fetchall()  # lista de tuplas (id, name)
 
 
def get_corrections_by_coordinator(coordinator_id: int, db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute(
        "SELECT data, machine, correction FROM corrective_patch WHERE coordinator_id = ?",
        (coordinator_id,)
    )
    return cursor.fetchall()
 
 
def get_history_by_coordinator(coordinator_id: int, db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute(
        "SELECT data, machine, correction FROM logging WHERE coordinator_id = ? ORDER BY id DESC",
        (coordinator_id,)
    )
    return cursor.fetchall()
 
 
def clear_attachment_file(filename):
    try:
        open(filename, 'w', encoding='utf-8').close()
    except OSError as e:
        print(f'Erro ao limpar arquivo de anexo: {e}')
 
 
def get_coordinator_full(coordinator_id: int, db: sqlite3.Connection):
    """Retorna (id, name, shift, function, email) - dados completos para
    instanciar o model Coordinator (que espera name/shift/function/email)."""
    cursor = db.cursor()
    cursor.execute("SELECT id, name, shift, function, email FROM coordinator WHERE id=?", (coordinator_id,))
    return cursor.fetchone()
 
 
def get_analyst_full(analyst_id: int, db: sqlite3.Connection):
    """Idem, para o model Analyst."""
    cursor = db.cursor()
    cursor.execute("SELECT id, name, shift, function, email FROM analyst WHERE id=?", (analyst_id,))
    return cursor.fetchone()
 
 
def archive_coordinator_corrections(coordinator_id: int, db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, data, machine, correction, coordinator_id, analyst_id "
        "FROM corrective_patch WHERE coordinator_id=?",
        (coordinator_id,)
    )
    rows = cursor.fetchall()
 
    if not rows:
        return 0
 
    try:
        for patch_id, data, machine, correction, c_id, a_id in rows:
            cursor.execute(
                "INSERT INTO logging "
                "(corrective_patch_id, data, machine, correction, coordinator_id, analyst_id) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (patch_id, data, machine, correction, c_id, a_id)
            )
            cursor.execute("DELETE FROM corrective_patch WHERE id=?", (patch_id,))
        db.commit()
        return len(rows)
    except sqlite3.Error:
        db.rollback()
        raise
 
 
# ============================================================
# Dialog: Criar Usuário
# ============================================================
 
class CreateUserDialog(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Criar Usuário")
        self.db = db
 
        self.name = QLineEdit()
        self.shift = QLineEdit()
        self.email = QLineEdit()
 
        self.radio_analyst = QRadioButton("Analista")
        self.radio_coordinator = QRadioButton("Coordenador")
        self.radio_analyst.setChecked(True)
 
        form = QFormLayout()
        form.addRow("Nome", self.name)
        form.addRow("Turno", self.shift)
        form.addRow("Email do Outlook", self.email)
        form.addRow(self.radio_analyst)
        form.addRow(self.radio_coordinator)
 
        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.on_save)
 
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(btn_save)
        self.setLayout(layout)
 
    def on_save(self):
        name = self.name.text().strip()
        shift = self.shift.text().strip()
        email = self.email.text().strip()
 
        if not name or not shift or not email:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha todos os campos.")
            return
 
        if self.radio_analyst.isChecked():
            create_analyst(name=name, shift=shift, function="Analista", email=email, db=self.db)
        else:
            create_coordinator(name=name, shift=shift, function="Coordinator", email=email, db=self.db)
 
        self.accept()
 
 
# ============================================================
# Dialog: Criar Correção
# ============================================================
 
class CreateCorrectionDialog(QDialog):
    # emite o id e nome do coordenador para a MainWindow atualizar a lista lateral
    correction_saved = Signal(int, str)
 
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Criar Correção")
        self.db = db
 
        self.data = QLineEdit()
        self.machine = QLineEdit()
        self.correction = QLineEdit()
 
        self.coordinator_combo = QComboBox()
        self.analyst_combo = QComboBox()
        self.load_people()
 
        form = QFormLayout()
        form.addRow("Data", self.data)
        form.addRow("Máquina", self.machine)
        form.addRow("Correção", self.correction)
        form.addRow("Coordenador", self.coordinator_combo)
        form.addRow("Analista", self.analyst_combo)
 
        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.on_save)
 
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(btn_save)
        self.setLayout(layout)
 
    def load_people(self):
        self.coordinator_combo.clear()
        for coordinator_id, name in get_all_coordinators(self.db):
            self.coordinator_combo.addItem(name, userData=coordinator_id)
 
        self.analyst_combo.clear()
        for analyst_id, name in get_all_analysts(self.db):
            self.analyst_combo.addItem(name, userData=analyst_id)
 
    def on_save(self):
        data = self.data.text().strip()
        machine = self.machine.text().strip()
        correction = self.correction.text().strip()
 
        if not all([data, machine, correction]):
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha todos os campos.")
            return
 
        if self.coordinator_combo.count() == 0 or self.analyst_combo.count() == 0:
            QMessageBox.warning(
                self, "Sem cadastro",
                "Cadastre pelo menos um coordenador e um analista antes de criar uma correção."
            )
            return
 
        coordinator_id = self.coordinator_combo.currentData()
        coordinator_name = self.coordinator_combo.currentText()
        analyst_id = self.analyst_combo.currentData()
 
        create_corrective_patch(
            data=data, machine=machine, correction=correction,
            coordinator_id=coordinator_id, analyst_id=analyst_id,
            db=self.db
        )
 
        self.correction_saved.emit(coordinator_id, coordinator_name)
 
        self.data.clear()
        self.machine.clear()
        self.correction.clear()
        
 
 
# ============================================================
# Dialog: escolher analista remetente + senha, na hora de enviar
# ============================================================
 
class SendEmailDialog(QDialog):
    """
    A senha do e-mail NUNCA é salva no banco - é pedida aqui, na hora do
    envio, e usada só em memória para autenticar no SMTP.
    """
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enviar Email")
        self.db = db
 
        self.analyst_combo = QComboBox()
        for analyst_id, name in get_all_analysts(self.db):
            self.analyst_combo.addItem(name, userData=analyst_id)
 
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
 
        form = QFormLayout()
        form.addRow("Analista (remetente)", self.analyst_combo)
        form.addRow("Senha do Outlook", self.password)
 
        btn_confirm = QPushButton("Confirmar e Enviar")
        btn_confirm.clicked.connect(self.accept)
 
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(btn_confirm)
        self.setLayout(layout)
 
    def selected_analyst_id(self):
        return self.analyst_combo.currentData()
 
    def entered_password(self):
        return self.password.text()
 
 
# ============================================================
# Janela: correções de um coordenador + botão de email
# ============================================================
 
class CoordinatorCorrectionsWindow(QWidget):
    def __init__(self, coordinator_id: int, coordinator_name: str, db: sqlite3.Connection):
        super().__init__()
        self.coordinator_id = coordinator_id
        self.coordinator_name = coordinator_name
        self.db = db
        self.setWindowTitle(f"Correções de {coordinator_name}")
        self.resize(600, 400)
 
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Data", "Máquina", "Correção"])
        self.load_corrections()
 
        btn_email = QPushButton("Enviar Email")
        btn_email.clicked.connect(self.on_send_email)
 
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(btn_email)
        self.setLayout(layout)
 
    def load_corrections(self):
        rows = get_corrections_by_coordinator(self.coordinator_id, self.db)
        self.table.setRowCount(len(rows))
        for i, (data, machine, correction) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(data)))
            self.table.setItem(i, 1, QTableWidgetItem(str(machine)))
            self.table.setItem(i, 2, QTableWidgetItem(str(correction)))
 
    def on_send_email(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Nada para enviar", "Este coordenador não tem correções registradas.")
            return
 
        cred_dialog = SendEmailDialog(self.db, parent=self)
        if not cred_dialog.exec():
            return  # usuário cancelou
 
        analyst_id = cred_dialog.selected_analyst_id()
        password = cred_dialog.entered_password()
 
        if not password:
            QMessageBox.warning(self, "Senha obrigatória", "Informe a senha do e-mail do analista.")
            return
 
        coordinator_row = get_coordinator_full(self.coordinator_id, self.db)
        analyst_row = get_analyst_full(analyst_id, self.db)
 
        if not coordinator_row or not analyst_row:
            QMessageBox.critical(self, "Erro", "Não foi possível carregar coordenador ou analista.")
            return
 
        _, c_name, c_shift, c_function, c_email = coordinator_row
        _, a_name, a_shift, a_function, a_email = analyst_row
 
        coordinator_obj = Coordinator(name=c_name, shift=c_shift, function=c_function, email=c_email)
        analyst_obj = Analyst(name=a_name, shift=a_shift, function=a_function, email=a_email)
 
        hour = datetime.now().hour
        if 6 <= hour < 13:
            greeting = "Bom dia"
        elif 13 <= hour < 18:
            greeting = "Boa tarde"
        else:
            greeting = "Boa noite"
 
        body = (
            f"{greeting}, {c_name}!\n\n"
            "Segue em anexo as correções para serem feitas na planilha de apontamento."
        )
 
        try:
            # gera o arquivo .txt com as correções desse coordenador
            extract_content(coordinator_obj, analyst_obj)
 
            # envia o email com o arquivo em anexo
            send_email(
                to_email=c_email,
                from_email=a_email,
                subject="Correção de Apontamentos",
                password_email=password,
                body=body,
                send=True
            )
 
            # move as correções enviadas para o histórico (logging) e as
            # remove de corrective_patch, pra não serem reenviadas depois
            archived_count = archive_coordinator_corrections(self.coordinator_id, self.db)
 
            clear_attachment_file(EMAIL_ATTACHMENT_FILE)
 
            QMessageBox.information(
                self, "Email",
                f"Email enviado com sucesso! {archived_count} correção(ões) movida(s) para o histórico."
            )
            self.load_corrections()  
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao enviar email: {e}")
 
 
# ============================================================
# Janela: histórico de correções já enviadas de um coordenador
# ============================================================
 
class CoordinatorHistoryWindow(QWidget):
    """Somente leitura - mostra o que já foi enviado (tabela logging)."""
 
    def __init__(self, coordinator_id: int, coordinator_name: str, db: sqlite3.Connection):
        super().__init__()
        self.coordinator_id = coordinator_id
        self.db = db
        self.setWindowTitle(f"Histórico de {coordinator_name}")
        self.resize(600, 400)
 
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Data", "Máquina", "Correção"])
        self.load_history()
 
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Correções já enviadas para {coordinator_name}"))
        layout.addWidget(self.table)
        self.setLayout(layout)
 
    def load_history(self):
        rows = get_history_by_coordinator(self.coordinator_id, self.db)
        self.table.setRowCount(len(rows))
        for i, (data, machine, correction) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(data)))
            self.table.setItem(i, 1, QTableWidgetItem(str(machine)))
            self.table.setItem(i, 2, QTableWidgetItem(str(correction)))
 
 
# ============================================================
# Janela principal
# ============================================================
 
class MainWindow(QMainWindow):
    def __init__(self, db: sqlite3.Connection):
        super().__init__()
        self.db = db
        self.setWindowTitle("Correção de Apontamentos")
        self.setGeometry(200, 200, 700, 450)
 
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_corrections_tab(), "Correções")
        self.tabs.addTab(self._build_history_tab(), "Histórico")
        self.setCentralWidget(self.tabs)
 
        self.refresh_coordinator_lists()
 
        # guarda referências pra evitar que o Python destrua as janelas filhas
        self._open_windows = []
 
    def _build_corrections_tab(self):
        btn_create_user = QPushButton("Criar Usuário")
        btn_create_correction = QPushButton("Criar Correção")
        btn_create_user.clicked.connect(self.open_create_user)
        btn_create_correction.clicked.connect(self.open_create_correction)
 
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Ações"))
        left_layout.addWidget(btn_create_user)
        left_layout.addWidget(btn_create_correction)
        left_layout.addStretch()
 
        self.coordinator_list = QListWidget()
        self.coordinator_list.itemClicked.connect(self.open_coordinator_corrections)
 
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Coordenadores"))
        right_layout.addWidget(self.coordinator_list)
 
        layout = QHBoxLayout()
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)
 
        tab = QWidget()
        tab.setLayout(layout)
        return tab
 
    def _build_history_tab(self):
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.open_coordinator_history)
 
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Coordenadores - clique para ver o histórico de envios"))
        layout.addWidget(self.history_list)
 
        tab = QWidget()
        tab.setLayout(layout)
        return tab
 
    def refresh_coordinator_lists(self):
        coordinators = get_all_coordinators(self.db)
 
        self.coordinator_list.clear()
        self.history_list.clear()
        for coordinator_id, name in coordinators:
            item1 = QListWidgetItem(name)
            item1.setData(1000, coordinator_id)
            self.coordinator_list.addItem(item1)
 
            item2 = QListWidgetItem(name)
            item2.setData(1000, coordinator_id)
            self.history_list.addItem(item2)
 
    def open_create_user(self):
        dialog = CreateUserDialog(self.db, parent=self)
        if dialog.exec():  
            self.refresh_coordinator_lists()
 
    def open_create_correction(self):
        dialog = CreateCorrectionDialog(self.db, parent=self)
        dialog.correction_saved.connect(self.on_correction_saved)
        dialog.exec()
 
    def on_correction_saved(self, coordinator_id, coordinator_name):
        existing = [
            self.coordinator_list.item(i).data(1000)
            for i in range(self.coordinator_list.count())
        ]
        if coordinator_id not in existing:
            item1 = QListWidgetItem(coordinator_name)
            item1.setData(1000, coordinator_id)
            self.coordinator_list.addItem(item1)
 
            item2 = QListWidgetItem(coordinator_name)
            item2.setData(1000, coordinator_id)
            self.history_list.addItem(item2)
 
    def open_coordinator_corrections(self, item: QListWidgetItem):
        coordinator_id = item.data(1000)
        coordinator_name = item.text()
        window = CoordinatorCorrectionsWindow(coordinator_id, coordinator_name, self.db)
        self._open_windows.append(window)  # evita garbage collection
        window.show()
 
    def open_coordinator_history(self, item: QListWidgetItem):
        coordinator_id = item.data(1000)
        coordinator_name = item.text()
        window = CoordinatorHistoryWindow(coordinator_id, coordinator_name, self.db)
        self._open_windows.append(window)
        window.show()

if __name__ == "__main__":
    import sys
    db = main_db()
    sys.argv.append('d:/project-scda/venv/Scripts/python.exe designer/mainwindow.py')
    app = QApplication(sys.argv)
    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())