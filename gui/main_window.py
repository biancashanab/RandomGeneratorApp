"""Main window and interaction flow."""

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QSpinBox, QStackedWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from algorithms import generate_bbs, generate_lcg
from utils.export import export_sequence
from utils.validation import parse_integer


@dataclass
class Generation:
    name: str
    parameters: str
    values: list[int]
    states: list[int] | None = None
    modulus: int | None = None


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Random Number Generator Laboratory")
        self.resize(1120, 760)
        self.setMinimumSize(900, 650)
        self.generation: Generation | None = None
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(30, 24, 30, 24)
        outer.setSpacing(18)

        header = QHBoxLayout()
        title_block = QVBoxLayout()

        title = QLabel("Random Generator Laboratory")
        title.setObjectName("title")
        subtitle = QLabel("Explore deterministic sequences with LCG and Blum Blum Shub.")
        subtitle.setObjectName("subtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        header.addLayout(title_block)
        header.addStretch()
        self.status_badge = QLabel("READY  ·  NO SEQUENCE")
        self.status_badge.setObjectName("badge")
        header.addWidget(self.status_badge, alignment=Qt.AlignmentFlag.AlignTop)
        outer.addLayout(header)

        workspace = QHBoxLayout()
        workspace.setSpacing(18)
        config_card = QFrame()
        config_card.setObjectName("card")
        config_card.setFixedWidth(350)
        config_layout = QVBoxLayout(config_card)
        config_layout.setContentsMargins(22, 22, 22, 22)
        config_layout.setSpacing(14)

        config_layout.addWidget(self._section_label("01  /  GENERATOR"))
        self.generator_select = QComboBox()
        self.generator_select.addItems(["Linear Congruential (LCG)", "Blum Blum Shub (BBS)"])
        self.generator_select.currentIndexChanged.connect(self._switch_generator)
        config_layout.addWidget(self.generator_select)

        self.parameter_stack = QStackedWidget()
        self.lcg_fields = self._make_fields([
            ("Multiplier  a", "1664525"), ("Increment  c", "1013904223"),
            ("Modulus  m", "4294967296"), ("Seed  X₀", "42"),
        ])
        self.bbs_fields = self._make_fields([
            ("Prime  p  (≡ 3 mod 4)", "383"), ("Prime  q  (≡ 3 mod 4)", "503"),
            ("Seed  X₀  (coprime to p·q)", "12345"),
        ])
        self.parameter_stack.addWidget(self.lcg_fields[0])
        self.parameter_stack.addWidget(self.bbs_fields[0])
        config_layout.addWidget(self.parameter_stack)

        config_layout.addWidget(self._section_label("02  /  SEQUENCE LENGTH"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100000)
        self.count_spin.setValue(64)
        config_layout.addWidget(self.count_spin)

        self.generate_button = QPushButton("Generate sequence  →")
        self.generate_button.setObjectName("primary")
        self.generate_button.clicked.connect(self._generate)
        config_layout.addWidget(self.generate_button)
        config_layout.addStretch()
        hint = QLabel("LCG returns integer states and normalized values.\nBBS returns generated bits and states.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        config_layout.addWidget(hint)

        output_card = QFrame()
        output_card.setObjectName("card")
        output_layout = QVBoxLayout(output_card)
        output_layout.setContentsMargins(22, 22, 22, 22)
        output_layout.setSpacing(14)
        top = QHBoxLayout()
        top.addWidget(self._section_label("03  /  OUTPUT"))
        top.addStretch()
        self.count_label = QLabel("0 VALUES")
        self.count_label.setObjectName("count")
        top.addWidget(self.count_label)
        output_layout.addLayout(top)
        self.summary = QLabel("Configure a generator and create your first sequence.")
        self.summary.setObjectName("summary")
        self.summary.setWordWrap(True)
        output_layout.addWidget(self.summary)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["INDEX", "GENERATED VALUE", "STATE / NORMALIZED"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(120)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        output_layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        actions.addWidget(QLabel("Export sequence"))
        actions.addStretch()
        self.txt_button = QPushButton("Export TXT")
        self.csv_button = QPushButton("Export CSV")
        self.txt_button.clicked.connect(lambda: self._export("txt"))
        self.csv_button.clicked.connect(lambda: self._export("csv"))
        actions.addWidget(self.txt_button)
        actions.addWidget(self.csv_button)
        output_layout.addLayout(actions)
        workspace.addWidget(config_card)
        workspace.addWidget(output_card, 1)
        outer.addLayout(workspace, 1)

        footer = QLabel("ALL GENERATORS ARE DETERMINISTIC FOR FIXED PARAMETERS")
        footer.setObjectName("footer")
        outer.addWidget(footer)
        self.setCentralWidget(root)

    @staticmethod
    def _section_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("section")
        return label

    @staticmethod
    def _make_fields(spec: list[tuple[str, str]]) -> tuple[QWidget, list[QLineEdit]]:
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(9)
        edits: list[QLineEdit] = []
        for row, (label_text, default) in enumerate(spec):
            label = QLabel(label_text)
            edit = QLineEdit(default)
            edit.setClearButtonEnabled(True)
            layout.addWidget(label, row, 0)
            layout.addWidget(edit, row, 1)
            edits.append(edit)
        return panel, edits

    def _switch_generator(self, index: int) -> None:
        self.parameter_stack.setCurrentIndex(index)
        self.count_spin.setSuffix(" values" if index == 0 else " bits")
        if self.generation is None:
            self.status_badge.setText("READY  ·  LCG" if index == 0 else "READY  ·  BBS")

    def _generate(self) -> None:
        try:
            count = self.count_spin.value()
            if self.generator_select.currentIndex() == 0:
                a, c, m, seed = [parse_integer(field.text(), name) for field, name in zip(
                    self.lcg_fields[1], ("a", "c", "m", "X₀"))]
                values = generate_lcg(a, c, m, seed, count)
                params = f"a={a}, c={c}, m={m}, X₀={seed}"
                self.generation = Generation("LCG", params, values, modulus=m)
            else:
                p, q, seed = [parse_integer(field.text(), name) for field, name in zip(
                    self.bbs_fields[1], ("p", "q", "X₀"))]
                states, bits = generate_bbs(p, q, seed, count)
                params = f"p={p}, q={q}, M=p·q={p*q}, X₀={seed}"
                self.generation = Generation("BBS", params, bits, states=states)
            self._render_generation()
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid parameters", str(exc))

    def _render_generation(self) -> None:
        assert self.generation is not None
        data = self.generation
        is_lcg = data.name == "LCG"
        self.table.setRowCount(len(data.values))
        for i, value in enumerate(data.values):
            self.table.setItem(i, 0, self._item(str(i + 1)))
            self.table.setItem(i, 1, self._item(str(value)))
            if is_lcg:
                normalized = value / data.modulus  # type: ignore[operator]
                detail = f"{normalized:.10f}"
            else:
                detail = str(data.states[i])  # type: ignore[index]
            self.table.setItem(i, 2, self._item(detail))
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.count_label.setText(f"{len(data.values):,} {'VALUES' if is_lcg else 'BITS'}")
        self.summary.setText(f"{data.name}  ·  {data.parameters}\nShowing {len(data.values)} generated {'states' if is_lcg else 'bits'}.")
        self.status_badge.setText(f"GENERATED  ·  {data.name}")

    @staticmethod
    def _item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        return item

    def _export(self, extension: str) -> None:
        if self.generation is None:
            QMessageBox.information(self, "Nothing to export", "Generate a sequence first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export sequence", f"{self.generation.name.lower()}_sequence.{extension}",
            "CSV files (*.csv)" if extension == "csv" else "Text files (*.txt)",
        )
        if not path:
            return
        try:
            export_sequence(path, self.generation.name, self.generation.parameters,
                            self.generation.values, self.generation.states, self.generation.modulus)
            self.status_badge.setText("EXPORTED  ·  " + extension.upper())
        except OSError as exc:
            QMessageBox.critical(self, "Export failed", f"Could not write the file:\n{exc}")

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #17121d; color: #f3eefa; font-family: 'Segoe UI'; font-size: 13px; }
            QFrame#card { background: #211927; border: 1px solid #403149; border-radius: 12px; }
            QLabel#eyebrow, QLabel#section { color: #e9a8d4; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
            QLabel#title { font-size: 27px; font-weight: 700; color: #fff8ff; }
            QLabel#subtitle, QLabel#hint { color: #bbaec3; }
            QLabel#hint { font-size: 11px; line-height: 1.4; }
            QLabel#badge { color: #f2b7dc; background: #352238; border: 1px solid #704a70; border-radius: 12px; padding: 8px 11px; font-size: 10px; font-weight: 700; }
            QLabel#count { color: #b9a9c2; font-size: 10px; font-weight: 700; }
            QLabel#summary { color: #ded1e4; padding: 5px 0; }
            QLabel#footer { color: #887991; font-size: 9px; letter-spacing: 1px; }
            QLineEdit, QComboBox, QSpinBox { background: #19141f; border: 1px solid #4a3b52; border-radius: 6px; padding: 8px; color: #f3eefa; selection-background-color: #87517c; }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #df91c2; }
            QComboBox QAbstractItemView { background: #211927; color: #f3eefa; selection-background-color: #704568; }
            QPushButton { background: #30253a; border: 1px solid #51425c; border-radius: 6px; padding: 9px 13px; color: #eee3f2; }
            QPushButton:hover { background: #40304a; border-color: #9a6b94; }
            QPushButton#primary { background: #92517e; border: 1px solid #bd72a4; color: white; font-weight: 700; padding: 12px; margin-top: 7px; }
            QPushButton#primary:hover { background: #a75f91; }
            QTableWidget { background: #1b1621; alternate-background-color: #241c2a; border: 1px solid #403149; border-radius: 7px; gridline-color: #382c40; selection-background-color: #493049; }
            QHeaderView::section { background: #2b2132; color: #c8b6cf; border: none; border-bottom: 1px solid #4a3b52; padding: 10px 8px; font-size: 10px; font-weight: 700; }
            QScrollBar:vertical { background: #1b1621; width: 10px; margin: 2px; }
            QScrollBar::handle:vertical { background: #594663; border-radius: 4px; min-height: 20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
