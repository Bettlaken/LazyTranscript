from PySide2.QtGui import QTextFormat
from PySide2.QtWidgets import *

""" QPlainTextEdit that highlights the current line. Based on: https://github.com/luchko/QCodeEditor """
class HighlightedQTextEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.currentLineColor = self.palette().alternateBase()
        self.cursorPositionChanged.connect(self.highlight_current_line)

    def highlight_current_line(self):
        hiSelection = QTextEdit.ExtraSelection()
        hiSelection.format.setBackground(self.currentLineColor)
        hiSelection.format.setProperty(QTextFormat.FullWidthSelection, True)
        hiSelection.cursor = self.textCursor()
        hiSelection.cursor.clearSelection()
        self.setExtraSelections([hiSelection])
