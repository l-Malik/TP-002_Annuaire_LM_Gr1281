import sys
import re
import csv
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox,QTableWidget, QTableWidgetItem, QComboBox,QFileDialog, QHeaderView
)

class ContactDirectory(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        """Initialise l'interface utilisateur et les éléments graphiques."""

        self.nom_label = QLabel("Nom :")
        self.nom_input = QLineEdit()

        self.prenom_label = QLabel("Prénom :")
        self.prenom_input = QLineEdit()

        self.email_label = QLabel("Email :")
        self.email_input = QLineEdit()

        self.phone_label = QLabel("Téléphone :")
        self.phone_input = QLineEdit()

        self.categorie_label = QLabel("Catégorie :")
        self.categorie_input = QComboBox()
        self.categorie_input.addItems(["Famille", "Amis", "Travail", "Prestataires", "Autres"])

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.filter_contacts)

        self.add_button = QPushButton('Ajouter')
        self.add_button.clicked.connect(self.add_contact)

        self.update_button = QPushButton('Modifier')
        self.update_button.clicked.connect(self.update_contact)
        self.update_button.setEnabled(False)

        self.delete_button = QPushButton('Supprimer')
        self.delete_button.clicked.connect(self.delete_contact)
        self.delete_button.setEnabled(False)

        self.show_button = QPushButton('Afficher les contacts')
        self.show_button.clicked.connect(self.display_contacts)

        self.export_button = QPushButton('Créer Une Sauvegarde')
        self.export_button.clicked.connect(self.export_contacts_to_csv)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Id', 'Nom', 'Prénom', 'Email', 'Téléphone', 'Catégorie'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.clicked.connect(self.enable_buttons)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.show_button)
        button_layout.addWidget(self.export_button)

        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.nom_label)
        layout.addWidget(self.nom_input)
        layout.addWidget(self.prenom_label)
        layout.addWidget(self.prenom_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.categorie_label)
        layout.addWidget(self.categorie_input)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)

        self.table.clicked.connect(self.load_selected_contact)

        self.setLayout(layout)

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.resize((2 * screen_width) // 5, (4 * screen_height) // 5)

        self.move(((3 * screen_width) - self.width()) // 5, (screen_height - self.height()) // 2)

        self.create_table()
        self.setWindowTitle('TP-02 Annuaire LM')
        self.show()


    def validate_contact_fields(self):
        nom = self.nom_input.text()
        prenom = self.prenom_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        categorie = self.categorie_input.currentText()

        if not nom and not prenom:
            QMessageBox.warning(self, 'Champs obligatoires', 'Le Nom et le Prénom doivent être saisis.')
            return False

        if not categorie:
            QMessageBox.warning(self, 'Champs obligatoires', 'Sélectionner une Catégorie.')
            return False

        if not email and not phone:
            QMessageBox.warning(self, 'Champs manquants',
                                'Vous devez remplir au moins un numéro de téléphone ou un email.')
            return False

        if not self.is_valid_email(email):
            QMessageBox.warning(self, 'Erreur', "L'email n'est pas valide.")
            return False

        if not self.is_valid_phone(phone):
            QMessageBox.warning(self, 'Erreur', "Le téléphone doit contenir uniquement des chiffres.")
            return False

        return True


    @staticmethod
    def is_valid_email(email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None


    @staticmethod
    def is_valid_phone(phone):
        return phone.isdigit()


    def add_contact(self):
        nom = self.nom_input.text()
        prenom = self.prenom_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        categorie = self.categorie_input.currentText()

        if not self.validate_contact_fields():
            return

        conn = None
        try:
            conn = sqlite3.connect('contacts_TP02.db')
            cursor = conn.cursor()

            cursor.execute('''SELECT COUNT (*) FROM contacts WHERE email = ?''', (email,))
            email_exists = cursor.fetchone()[0]

            if email_exists:
                QMessageBox.warning(self, 'Attention', 'Cet email existe déjà dans la base de données.')
                return

            cursor.execute('''INSERT INTO contacts (nom, prenom, email, phone, categorie) VALUES (?, ?, ?, ?, ?)''',
                               (nom, prenom, email, phone, categorie))
            conn.commit()

            QMessageBox.information(self, 'Succès', 'Contact ajouté avec succès.')
            self.display_contacts()
            self.clear_inputs()

        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Erreur de la base de données', f'Une erreur est survenue : {e}')

        finally:
            conn.close()


    def update_contact(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Erreur', 'Veuillez sélectionner un contact à modifier.')
            return

        reply = QMessageBox.question(self, 'Confirmation', 'Êtes-vous sûr de vouloir modifier ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        contact_id = int(self.table.item(selected_row, 0).text())

        if not self.validate_contact_fields():
            return

        nom = self.nom_input.text()
        prenom = self.prenom_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        categorie = self.categorie_input.currentText()

        try:
            conn = sqlite3.connect('contacts_TP02.db')
            cursor = conn.cursor()
            cursor.execute('''UPDATE contacts SET nom = ?, prenom = ?, email = ?, phone = ?, categorie = ? WHERE Id = ?''',
                           (nom, prenom, email, phone, categorie, contact_id))
            conn.commit()

            QMessageBox.information(self, 'Succès', 'Les données ont été mises à jour avec succès.')
            self.clear_inputs()
            self.display_contacts()
            self.disable_buttons()

        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Une erreur est survenue : {str(e)}')


    def delete_contact(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Erreur', 'Veuillez sélectionner un étudiant à supprimer.')
            return

        reply = QMessageBox.question(self, 'Confirmation', 'Êtes-vous sûr de vouloir supprimer ce contact ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        contact_id = int(self.table.item(selected_row, 0).text())

        try:
            conn = sqlite3.connect('contacts_TP02.db')
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM contacts WHERE Id = ?''',
                           (contact_id,))
            conn.commit()

            QMessageBox.information(self, "Succès", "Le contact a été supprimé avec succès.")
            self.clear_inputs()
            self.display_contacts()
            self.disable_buttons()

        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Une erreur est survenue : {str(e)}')


    def display_contacts(self):
        try:
            conn = sqlite3.connect('contacts_TP02.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM contacts')
            contacts = cursor.fetchall()
            conn.close()

            self.table.setRowCount(0)

            for row_number, row_data in enumerate(contacts):
                self.table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_number, column_number, item)

        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Une erreur est survenue : {str(e)}')


    def filter_contacts(self):
        filter_text = self.search_input.text().lower()
        for i in range(self.table.rowCount()):
            match = any(filter_text in self.table.item(i, j).text().lower() for j in range(self.table.columnCount()))
            self.table.setRowHidden(i, not match)


    def load_selected_contact(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            self.nom_input.setText(self.table.item(selected_row, 1).text())
            self.prenom_input.setText(self.table.item(selected_row, 2).text())
            self.email_input.setText(self.table.item(selected_row, 3).text())
            self.phone_input.setText(self.table.item(selected_row, 4).text())
            self.categorie_input.setCurrentText(self.table.item(selected_row, 5).text())


    def enable_buttons(self):
        self.update_button.setEnabled(True)
        self.delete_button.setEnabled(True)


    def disable_buttons(self):
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)


    def clear_inputs(self):
        self.nom_input.clear()
        self.prenom_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.categorie_input.setCurrentIndex(0)


    def export_contacts_to_csv(self):
        try:
            conn = sqlite3.connect('contacts_TP02.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM contacts')
            contacts = cursor.fetchall()
            conn.close()

            file_sauvegarde, _ = QFileDialog.getSaveFileName(self, "Exporter en CSV", "", "CSV Files (*.csv);;All Files (*)")
            if file_sauvegarde:
                with open(file_sauvegarde, 'w', newline='', encoding= 'utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Id', 'Nom','Prénom', 'Email', 'Téléphone', 'catégorie'])
                    writer.writerows(contacts)

                QMessageBox.information(self, "Sauvegarde réussie", "Les données ont été exportées avec succès.")

        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f'Une erreur est survenue : {str(e)}')


    def create_table(self):
        try:
            conn = sqlite3.connect('contacts_TP02.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    categorie TEXT NOT NULL)''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Erreur de la base de données', f'Une erreur est survenue : {e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = ContactDirectory()
    sys.exit(app.exec())
