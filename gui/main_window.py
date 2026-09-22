"""The application's single window: URL input, selector options, and export."""

import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from core.http_client import DEFAULT_USER_AGENT, HttpClient
from core.parser import SelectorType
from core.scraper import ScraperEngine, ScrapeReport
from services.export_service import EXPORTERS

APP_VERSION = "0.1.0"


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Web Scraper Toolkit")
        self.resize(900, 680)

        self.report: ScrapeReport | None = None
        self.setup_ui()
        self._build_status_bar()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(self._build_urls_group())

        middle_row = QHBoxLayout()
        middle_row.setSpacing(8)
        middle_row.addWidget(self._build_selector_group(), 1)
        middle_row.addWidget(self._build_options_group(), 1)
        layout.addLayout(middle_row)

        layout.addWidget(self._build_output_group())

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Log çıktısı burada görünecek...")
        self.log_box.setFixedHeight(160)
        layout.addWidget(self.log_box, stretch=1)

        self.scrape_button = QPushButton("🌐  Scrape")
        self.scrape_button.setFixedHeight(42)
        self.scrape_button.clicked.connect(self.run_scrape)
        layout.addWidget(self.scrape_button)

    def _build_urls_group(self) -> QGroupBox:
        group = QGroupBox("URLs")
        group.setToolTip("Her satıra bir URL yazın - tek URL veya toplu tarama için aynı alan kullanılır.")
        layout = QVBoxLayout(group)

        self.urls_edit = QPlainTextEdit()
        self.urls_edit.setPlaceholderText("https://example.com/page-1\nhttps://example.com/page-2")
        self.urls_edit.setFixedHeight(90)
        layout.addWidget(self.urls_edit)
        return group

    def _build_selector_group(self) -> QGroupBox:
        group = QGroupBox("Selector")
        layout = QVBoxLayout(group)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.selector_type_combo = QComboBox()
        self.selector_type_combo.addItem("CSS Selector", SelectorType.CSS)
        self.selector_type_combo.addItem("XPath", SelectorType.XPATH)
        type_row.addWidget(self.selector_type_combo, stretch=1)
        layout.addLayout(type_row)

        self.selector_edit = QLineEdit()
        self.selector_edit.setPlaceholderText("örn. h2.title  veya  //h2[@class='title']")
        layout.addWidget(self.selector_edit)

        attr_row = QHBoxLayout()
        attr_row.addWidget(QLabel("Attribute:"))
        self.attribute_edit = QLineEdit()
        self.attribute_edit.setPlaceholderText("boş = metin, örn. href")
        attr_row.addWidget(self.attribute_edit, stretch=1)
        layout.addLayout(attr_row)

        layout.addStretch()
        return group

    def _build_options_group(self) -> QGroupBox:
        group = QGroupBox("Options")
        layout = QVBoxLayout(group)

        ua_row = QHBoxLayout()
        ua_row.addWidget(QLabel("User-Agent:"))
        self.user_agent_edit = QLineEdit(DEFAULT_USER_AGENT)
        ua_row.addWidget(self.user_agent_edit, stretch=1)
        layout.addLayout(ua_row)

        numbers_row = QHBoxLayout()
        numbers_row.addWidget(QLabel("Timeout (s):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 120)
        self.timeout_spin.setValue(15)
        numbers_row.addWidget(self.timeout_spin)

        numbers_row.addWidget(QLabel("Retries:"))
        self.retries_spin = QSpinBox()
        self.retries_spin.setRange(0, 5)
        self.retries_spin.setValue(2)
        numbers_row.addWidget(self.retries_spin)
        layout.addLayout(numbers_row)

        self.robots_checkbox = QCheckBox("Respect robots.txt")
        self.robots_checkbox.setChecked(True)
        self.robots_checkbox.setToolTip("İşaretliyse, sitenin robots.txt kuralı taramayı yasaklıyorsa o URL atlanır.")
        layout.addWidget(self.robots_checkbox)

        layout.addStretch()
        return group

    def _build_output_group(self) -> QGroupBox:
        group = QGroupBox("Output")
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Folder:"))
        self.output_folder_edit = QLineEdit(str(Path.cwd() / "output"))
        layout.addWidget(self.output_folder_edit, stretch=1)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_output_folder)
        layout.addWidget(browse_button)

        self.format_combo = QComboBox()
        self.format_combo.addItem("CSV", "csv")
        self.format_combo.addItem("Excel", "excel")
        self.format_combo.addItem("JSON", "json")
        layout.addWidget(self.format_combo)

        return group

    def _build_status_bar(self) -> None:
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Web Scraper Toolkit v{APP_VERSION}")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _browse_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder_edit.text())
        if folder:
            self.output_folder_edit.setText(folder)

    def log(self, message: str) -> None:
        self.log_box.appendPlainText(message)

    def run_scrape(self) -> None:
        urls = [line.strip() for line in self.urls_edit.toPlainText().splitlines() if line.strip()]
        selector = self.selector_edit.text().strip()

        if not urls:
            QMessageBox.warning(self, "No URLs", "Please enter at least one URL.")
            return
        if not selector:
            QMessageBox.warning(self, "No Selector", "Please enter a CSS selector or an XPath expression.")
            return

        self.scrape_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_box.clear()
        self.log(f"Starting scrape of {len(urls)} URL(s)...")

        try:
            client = HttpClient(
                user_agent=self.user_agent_edit.text().strip() or DEFAULT_USER_AGENT,
                timeout=self.timeout_spin.value(),
                max_retries=self.retries_spin.value(),
            )
            engine = ScraperEngine(client=client, respect_robots_txt=self.robots_checkbox.isChecked())
            selector_type = self.selector_type_combo.currentData()
            attribute = self.attribute_edit.text().strip() or None

            report = engine.scrape_many(
                urls, selector, selector_type, attribute, on_progress=self._on_progress
            )
            self.report = report

            for result in report.results:
                if result.success:
                    self.log(f"OK      {result.url} -> {len(result.values)} value(s)")
                elif result.skipped_by_robots:
                    self.log(f"SKIPPED {result.url} (robots.txt disallows this page)")
                else:
                    self.log(f"FAILED  {result.url} - {result.error}")

            self.log(
                f"Finished: {report.succeeded} succeeded, {report.failed} failed, "
                f"{report.total_values} value(s) extracted."
            )

            if report.total_values == 0:
                QMessageBox.information(self, "No Data", "No values were extracted - check the selector and try again.")
                return

            self._export_results(report)
        except Exception as error:
            self.log(f"ERROR: {error}")
            QMessageBox.critical(self, "Error", str(error))
        finally:
            self.progress_bar.setValue(100)
            self.scrape_button.setEnabled(True)

    def _on_progress(self, done: int, total: int, url: str) -> None:
        self.progress_bar.setValue(int(done / total * 100) if total else 0)
        self.status_bar.showMessage(f"Scraping {done + 1}/{total}: {url}" if done < total else "Done")
        self.log_box.repaint()
        from PySide6.QtWidgets import QApplication

        QApplication.processEvents()

    def _export_results(self, report: ScrapeReport) -> None:
        output_folder = Path(self.output_folder_edit.text())
        output_folder.mkdir(parents=True, exist_ok=True)

        export_format = self.format_combo.currentData()
        extension = {"csv": "csv", "excel": "xlsx", "json": "json"}[export_format]
        output_path = output_folder / f"scrape_results.{extension}"

        exporter = EXPORTERS[export_format]
        exporter(report, output_path)
        self.log(f"Saved: {output_path}")

        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("Done")
        message_box.setText(f"{report.total_values} value(s) exported.")
        message_box.setInformativeText(str(output_path))
        message_box.addButton(QMessageBox.StandardButton.Ok)
        open_folder_button = message_box.addButton("Open Folder", QMessageBox.ButtonRole.ActionRole)
        message_box.exec()

        if message_box.clickedButton() == open_folder_button:
            os.startfile(output_folder)
