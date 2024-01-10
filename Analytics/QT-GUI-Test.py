import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QDateEdit, QPushButton, QTableView, QListWidget, QAbstractItemView, QCalendarWidget
from PyQt5.QtGui import QColor, QFont, QStandardItemModel, QStandardItem, QPalette
from PyQt5.QtCore import Qt, QDate


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI")
        self.setGeometry(100, 100, 1200, 1000)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        central_widget.setStyleSheet("background-color: #FFEFD5;")  # Light orange background color (hexadecimal value)

        # Widget1: Date Entry
        self.widget1 = QWidget(central_widget)
        self.widget1.setGeometry(20, 20, 200, 80)
        self.widget1.setStyleSheet("background-color: lightblue;")
        widget1_label = QLabel("Date:", self.widget1)
        widget1_label.setGeometry(10, 20, 40, 20)
        widget1_label.setStyleSheet("color: darkblue;")
        self.date_entry = QDateEdit(self.widget1)
        self.date_entry.setGeometry(60, 20, 120, 20)
        self.date_entry.setDisplayFormat("dd-MM-yyyy")
        self.date_entry.setDate(QDate.currentDate())  # Set initial date to today

        self.calendar_button = QPushButton("Calendar", self.widget1)
        self.calendar_button.setGeometry(60, 50, 120, 20)
        self.calendar_button.setStyleSheet("color: darkblue;")
        self.calendar_button.clicked.connect(self.open_calendar)

        # Widget2: Selection Widget
        self.widget2 = QListWidget(central_widget)
        self.widget2.setGeometry(20, 110, 100, 600)
        self.widget2.setStyleSheet("background-color: white;")
        self.widget2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.widget2.itemClicked.connect(self.item_selected)

        items = ["SOFR_DC", "ESTER_DC", "SONIA_DC", "AUD_6M", "CAD_6M"]
        self.widget2.addItems(items)

        # Widget3: Table Display
        self.widget3 = QTableView(central_widget)
        self.widget3.setGeometry(130, 110, 800, 600)
        self.widget3.setStyleSheet("background-color: lightgrey;")
        self.widget3.setShowGrid(False)
        self.widget3.verticalHeader().setVisible(False)

        # Widget4: Go Button
        self.widget4 = QPushButton("Go!", central_widget)
        self.widget4.setGeometry(235, 20, 80, 80)
        self.widget4.clicked.connect(self.show_table)

        self.table_data = None
        self.selected_item = None

    def open_calendar(self):
        self.calendar = QCalendarWidget()
        self.calendar.setWindowModality(Qt.ApplicationModal)
        self.calendar.clicked.connect(self.select_date)
        self.calendar.clicked.connect(self.close_calendar_on_double_click)
        self.calendar.show()

    def select_date(self, date):
        self.date_entry.setDate(date)
        self.calendar.close()

    def close_calendar_on_double_click(self):
        self.calendar.close()

    def item_selected(self, item):
        self.selected_item = item.text()
        for i in range(self.widget2.count()):
            item = self.widget2.item(i)
            if item.text() == self.selected_item:
                item.setBackground(QColor(Qt.darkBlue))
                item.setForeground(QColor(Qt.white))
            else:
                item.setBackground(QColor(Qt.white))
                item.setForeground(QColor(Qt.black))


    def show_table(self):
        self.set_table_data()

    def set_table_data(self):
#        outright_rates = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]
#        fwd_rates = [(1,1), (2,1), (3,1), (4,1), (2,2), (3,2), (5,5), (10,5), (10,10), (15,15) ]
#        curve_rates = [(2,3), (2,5), (2,10), (5,10), (5,30), (10,30)]
#        fly_rates = [(2,3,5), (2,5,10), (3,5,7), (5,10,30)]
#        tab1 = swap_table2([sofr_live], outright_rates, fwd_rates, curve_rates, fly_rates)

        ###### Get selection from QListWidget
        a = self.widget2.currentRow()
        print(self.widget2.item(a).text())

        crv1 = ois_dc_build(self.widget2.item(a).text(), b=0)
        data = swap_table(crv1).table

        ###### Get date from QDateEdit
        print(self.date_entry.date().toPyDate())

        self.table_data = QStandardItemModel()
        self.table_data.setColumnCount(len(data.keys()))

        for i, column in enumerate(data.keys()):
            for j, value in enumerate(data.iloc[:,i]):
#                print(i,j,value)
                item = QStandardItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table_data.setItem(j, i, item)

                if i in [0, 3, 6, 9]:  # Sets
                    item.setFont(QFont("Arial", weight=QFont.Bold))
                    item.setBackground(QColor(Qt.lightGray))

                if i in [1, 4, 7, 10]:  # Rates
                    item.setForeground(QColor(Qt.darkBlue))

                if i in [2, 5, 8, 11]:  # chgs
                    if (value == '' or value < 0):
                        item.setForeground(QColor(Qt.red))
                    else:
                        item.setForeground(QColor(Qt.darkGreen))

        self.table_data.setHorizontalHeaderLabels(data.keys())
        self.widget3.setModel(self.table_data)
        self.widget3.setColumnWidth(0, 60)
        self.widget3.setColumnWidth(1, 80)
        self.widget3.setColumnWidth(2, 40)
        self.widget3.setColumnWidth(3, 70)
        self.widget3.setColumnWidth(4, 80)
        self.widget3.setColumnWidth(5, 40)
        self.widget3.setColumnWidth(6, 70)
        self.widget3.setColumnWidth(7, 80)
        self.widget3.setColumnWidth(8, 40)
        self.widget3.setColumnWidth(9, 70)
        self.widget3.setColumnWidth(10, 80)
        self.widget3.setColumnWidth(11, 40)
        for i in np.arange(len(data)):
            self.widget3.setRowHeight(i,20)



app = QApplication(sys.argv)
gui = GUI()
gui.show()
sys.exit(app.exec_())










import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class Eco(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title label
        label_tab = QLabel("Eco")
        label_tab.setFixedSize(200, 50)
        label_tab.setStyleSheet("background-color: grey; color: blue")
        layout.addWidget(label_tab)

        # Right layout - listboxes and plot buttons
        right_layout = QVBoxLayout()
        layout.addLayout(right_layout)

        # Listboxes
        listbox_layout = QHBoxLayout()
        right_layout.addLayout(listbox_layout)
        listbox_layout.setSpacing(1)  # Add 10 pixels of space between widgets
        listbox_layout.setContentsMargins(1, 1, 1, 1)  # Add 10 pixels of margin on each side of the layout

        self.ticker_lstbox = QListWidget()
        self.ticker_lstbox.setFixedSize(100, 200)
        self.ticker_lstbox.addItems('GDP CPI PCE Core-PCE UNEMP FISC'.split())
        self.ticker_lstbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        listbox_layout.addWidget(self.ticker_lstbox)

        self.country_lstbox = QListWidget()
        self.country_lstbox.setFixedSize(100, 200)
        self.country_lstbox.addItems('US EU GB DE FR IT ES CA AU NZ SE NO CH JP KR CN'.split())
        self.country_lstbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        listbox_layout.addWidget(self.country_lstbox)

        self.yr_lstbox = QListWidget()
        self.yr_lstbox.setFixedSize(100, 200)
        self.yr_lstbox.addItems('2022 2023 2024 2025 2026'.split())
        self.yr_lstbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        listbox_layout.addWidget(self.yr_lstbox)

        self.contrib_lstbox = QListWidget()
        self.contrib_lstbox.setFixedSize(100, 200)
        self.contrib_lstbox.addItems('BAR BOA BNP CE CIT CAG CSU DNS FTC GS HSB IG JPM MS NTX NS NDA PMA UBS WF SCB'.split())
        self.contrib_lstbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        listbox_layout.addWidget(self.contrib_lstbox)

        self.offi_lstbox = QListWidget()
        self.offi_lstbox.setFixedSize(100, 200)
        self.offi_lstbox.addItems('FED ECB BOE OEC IMF WB EU EC OBR IST DBK ISE BOC RBA RIK NOR NPC'.split())
        self.offi_lstbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        listbox_layout.addWidget(self.offi_lstbox)

        listbox_layout.addStretch(1)

        # Plot buttons
        button_layout = QHBoxLayout()
        right_layout.addLayout(button_layout)

        plot_button1 = QPushButton("Plot1")
        plot_button1.clicked.connect(self.on_plot_button_clicked)
        button_layout.addWidget(plot_button1)

        plot_button2 = QPushButton("Plot2")
        plot_button2.clicked.connect(self.on_plot_button_clicked)
        button_layout.addWidget(plot_button2)

        plot_button3 = QPushButton("Plot3")
        plot_button3.clicked.connect(self.on_plot_button_clicked)
        button_layout.addWidget(plot_button3)

        plot_button4 = QPushButton("Plot4")
        plot_button4.clicked.connect(self.on_plot_button_clicked)
        button_layout.addWidget(plot_button4)

        button_layout.addStretch(1)

        # Plot canvas and toolbar
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        # Define plot_layout in your __init__ method, where self refers to the Eco widget
        self.plot_layout = QVBoxLayout()
        self.setLayout(self.plot_layout)

        # Create the initial FigureCanvasQTAgg and NavigationToolbar2QT
        fig, ax = plt.subplots()
        self.canvas = FigureCanvas(fig)
        self.plot_layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.plot_layout.addWidget(self.toolbar)



    def on_plot_button_clicked(self):
        a1 = self.ticker_lstbox.currentItem().text()
        a2 = self.country_lstbox.currentItem().text()
        a3 = self.yr_lstbox.currentItem().text()
        a4 = self.contrib_lstbox.currentItem().text()
        a5 = self.offi_lstbox.currentItem().text()

        print(a1, a2, a3, a4, a5)

        fig = ecfc_plot(a1, a2, a3, contrib1=a4, off=a5)

        # Create a new canvas with the new figure
        canvas = FigureCanvas(fig)

        # Remove the old canvas from the layout
        self.plot_layout.removeWidget(self.canvas)

        # Replace the old canvas with the new one
        self.canvas.deleteLater()
        self.canvas = canvas
        self.plot_layout.addWidget(self.canvas)

        # Recreate the navigation toolbar
#        self.toolbar.deleteLater()
#        self.toolbar = NavigationToolbar(self.canvas, self)
#        self.plot_layout.addWidget(self.toolbar)
#        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quixotic")  # Set the window title
        self.resize(1800, 1200)  # Set the size of the window

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(Eco(), "Eco")
        self.tab_widget.addTab(Tab("Plottool"), "Plottool")
        self.tab_widget.addTab(Tab("Swap Monitor"), "Swap Monitor")
        self.tab_widget.addTab(Tab("Inflation Monitor"), "Inflation Monitor")
        self.tab_widget.addTab(Tab("Swap Fwds"), "Swap Fwds")

        self.setCentralWidget(self.tab_widget)

        # Set the stylesheet
        self.setStyleSheet("""
            QTabWidget::pane { /* The tab widget frame */
                border-top: 2px solid #C2C7CB;
                background: grey;
            }
            QTabWidget { /* The tab widget frame */
                background: grey;
            }
            QTabBar::tab { /* The tabs themselves */
                background: lightgrey;
                padding: 5px;
            }
            QTabBar::tab:selected { /* The selected tab */
                background: grey;
            }
        """)

class Tab(QWidget):
    def __init__(self, name):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)


app = QApplication(sys.argv)
gui = MainWindow()
gui.show()
sys.exit(app.exec_())

























