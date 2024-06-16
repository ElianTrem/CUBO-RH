import sys
import markdown
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QTextBrowser, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor 

class MarkdownEditor(QWidget):
    def __init__(self, markdown_file):
        super().__init__()
        self.markdown_file = markdown_file
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Markdown Editor')

        # Layouts
        main_layout = QHBoxLayout()
        editor_layout = QVBoxLayout()
        preview_layout = QVBoxLayout()

        # QTextEdit for editing Markdown
        self.text_edit = QTextEdit(self)
        self.text_edit.textChanged.connect(self.update_preview)
        editor_layout.addWidget(self.text_edit)

        # QTextBrowser to display Markdown preview
        self.text_browser = QTextBrowser(self)
        preview_layout.addWidget(self.text_browser)

        main_layout.addLayout(editor_layout)
        main_layout.addLayout(preview_layout)

        self.setLayout(main_layout)
        self.resize(800, 600)

        # Load Markdown content into editor and update preview
        self.load_markdown(self.markdown_file)

    def load_markdown(self, markdown_file):
        with open(markdown_file, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
            self.text_edit.setPlainText(markdown_content)
            self.update_preview()

    def update_preview(self):
        markdown_content = self.text_edit.toPlainText()
        html_content = markdown.markdown(markdown_content)
        self.text_browser.setHtml(html_content)

        # Process Markdown syntax dynamically
        cursor = self.text_edit.textCursor()
        cursor_position = cursor.position()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, cursor_position)
        selected_text = cursor.selectedText()

        if selected_text.startswith("#"):
            level = selected_text.count("#")
            html_text = f"<h{level}>{selected_text[level+1:]}</h{level}>"
            cursor.insertHtml(html_text)

        cursor.setPosition(cursor_position)
        self.text_edit.setTextCursor(cursor)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = MarkdownEditor('Markdown/CoordinadorLocal.md')
    editor.show()
    sys.exit(app.exec_())
