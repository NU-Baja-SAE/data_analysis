import pyqtgraph as pg
from PyQt5 import QtWidgets
import numpy as np
import pandas as pd

PATH = 'data_2/data_3.csv'

# Create a QApplication instance
app = QtWidgets.QApplication([])

# Create a main window
main_window = QtWidgets.QMainWindow()
main_window.setWindowTitle("PyQtGraph Example Plot")

# Create a PlotWidget and set it as the central widget
plot_widget = pg.PlotWidget()
main_window.setCentralWidget(plot_widget)

# Load data from CSV
df = pd.read_csv(PATH)

#filter data
# remove outliers where engine_rpm > 8000
df = df[df["engine_rpm"] <= 8000] if "engine_rpm" else df

# Plot the data
plot_widget.plot(df["engine_rpm"], pen='b', name="Engine RPM")
plot_widget.plot(df["wheel_rpm"], pen='r', name="Wheel RPM")


# Add a title and labels
plot_widget.setTitle("Backwoods Data Plot")
plot_widget.setLabel('left', "Engine RPM")
plot_widget.setLabel('bottom', "index")

# Show the grid
plot_widget.showGrid(x=True, y=True)

# Display the main window
main_window.show()

# Start the Qt event loop
app.exec_()