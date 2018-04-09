import StringIO
import re

from PySide2 import QtWidgets, QtGui
from PySide2 import QtCore
from PySide2.QtGui import QTextLayout

from pyflakes.api import check
from pyflakes.reporter import Reporter


class DockWidget(QtWidgets.QWidget):

    simulate = QtCore.Signal()

    def __init__(self, view):
        super(DockWidget, self).__init__(view)
        self._ui = UiWidgetContainer()
        self._ui.setup_ui(view)
        self._ui.setup_text_edit()
        # self._ui.highlighter.addToDocument(self._ui.textEdit.document())

        self._make_connections()

    def enable_simulation(self, state):
        self._ui.pushButton.setEnabled(state)

    def get_code(self):
        return self._ui.textEdit.toPlainText()

    def _make_connections(self):
        self._ui.pushButton.clicked.connect(self._parse_code)

    def _parse_code(self):
        code = self._ui.textEdit.toPlainText()
        out_stream = StringIO.StringIO()
        err_stream = StringIO.StringIO()
        reporter = Reporter(out_stream, err_stream)

        result = check(code, 'function', reporter)

        out_string = out_stream.getvalue()
        err_string = err_stream.getvalue()
        out_stream.close()
        err_stream.close()
        if result:
            QtWidgets.QMessageBox.critical(self.parent(), "Problems encountered!",
                                           "%s\n%s\n" % (out_string, err_string))
        else:
            self.simulate.emit()


class UiWidgetContainer(object):

    def __init__(self):
        self.horizontalLayout_2 = None
        self.dockWidget = None
        self.dockWidgetContents = None
        self.verticalLayout = None
        self.textEdit = None
        self.horizontalLayout = None
        self.pushButton = None
        self.highlighter = Highlighter()

    def setup_ui(self, widget_container):
        # self.horizontalLayout_2 = QtWidgets.QHBoxLayout(widget_container)
        # self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        # self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.dockWidget = QtWidgets.QDockWidget()  # QtCore.Qt.RightDockWidgetArea, widget_container)
        self.dockWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textEdit = QtWidgets.QTextEdit(self.dockWidgetContents)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacer_item)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.dockWidget.setWidget(self.dockWidgetContents)
        # self.horizontalLayout_2.addWidget(self.dockWidget)

        self.highlighter.addToDocument(self.textEdit.document())

        # QtCore.QMetaObject.connectSlotsByName(widget_container)

        self.dockWidget.setWindowTitle(QtWidgets.QApplication.translate("widgetContainer", "Animate Jaw", None, -1))
        self.pushButton.setText(QtWidgets.QApplication.translate("widgetContainer", "Simulate", None, -1))

        widget_container.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockWidget)

    def setup_text_edit(self):
        variable_format = QtGui.QTextCharFormat()
        variable_format.setFontWeight(QtGui.QFont.Bold)
        variable_format.setForeground(QtCore.Qt.blue)
        self.highlighter.addMapping("def|\\breturn\\b", variable_format)
        # self.highlighter.addMapping("return", variable_format)

        single_line_comment_format = QtGui.QTextCharFormat()
        single_line_comment_format.setForeground(QtCore.Qt.darkGray)
        # single_line_comment_format.setBackground(QtGui.QColor("#77ff77"))
        self.highlighter.addMapping("#[^\n]*", single_line_comment_format)

        quotation_format = QtGui.QTextCharFormat()
        # quotation_format.setBackground(QtCore.Qt.cyan)
        quotation_format.setForeground(QtCore.Qt.darkGreen)
        self.highlighter.addMapping("sin|cos|exp|sqrt", quotation_format)

        function_format = QtGui.QTextCharFormat()
        function_format.setFontItalic(True)
        function_format.setForeground(QtCore.Qt.blue)
        self.highlighter.addMapping("\\b[a-z0-9_]+\\(.*\\)", function_format)

        self.textEdit.setText("""def animate_jaw(elapsed_time):
    \"\"\"
    This function takes in an elapsed time value between [0, X) seconds and returns
    the angle (in radians!!) for the jaw at that time.  Mathematical functions
    that are available are:
       'sin', 'cos', 'exp', 'sqrt'.
    \"\"\"
    angle = 0.0
    # Place your code here!
    if elapsed_time < 0.5:
        pass
    elif elapsed_time < 1.2:
        angle = 0.707
    elif elapsed_time < 2.0:
        angle = 1.5
    elif elapsed_time < 3.5:
        angle = 2.8
        
    return angle
""")


class Highlighter(QtCore.QObject):

    def __init__(self):
        super(Highlighter, self).__init__()
        self.mappings = {}

    def addToDocument(self, doc):
        doc.contentsChange.connect(self.highlight)
        # self.connect(doc, QtCore.SIGNAL("contentsChange(int, int, int)"), self.highlight)

    def addMapping(self, pattern, pattern_format):
        self.mappings[pattern] = pattern_format

    def highlight(self, position, removed, added):
        doc = self.sender()

        block = doc.findBlock(position)
        if not block.isValid():
            return

        if added > removed:
            endBlock = doc.findBlock(position + added - 1)
        else:
            endBlock = block

        while block.isValid() and not (endBlock < block):
            self.highlightBlock(block)
            block = block.next()

    def highlightBlock(self, block):
        layout = block.layout()
        text = block.text()

        overrides = []

        for pattern in self.mappings:
            for m in re.finditer(pattern, text):
                format_range = QTextLayout.FormatRange()
                s, e = m.span()
                format_range.start = s
                format_range.length = e - s
                format_range.format = self.mappings[pattern]
                overrides.append(format_range)

        layout.setAdditionalFormats(overrides)
        block.document().markContentsDirty(block.position(), block.length())
