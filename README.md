ATORCH USB Energy Monitor GUI

![ATORCH Energy Monitor Screenshot](https://github.com/peterpt/Atorch-Energy-Monitor/blob/main/atorch.png)


** Hardware
  ![ATORCH Energy Monitor Hardware](https://github.com/peterpt/Atorch-Energy-Monitor/blob/main/energycontroler.png)


** About

A cross-platform graphical user interface for monitoring ATORCH USB energy meters in real-time. This tool provides a visual representation of key electrical measurements and plots historical data on an interactive chart.

(To use the image above, you can use the provided Imgur link or add your own screenshot named screenshot.png to the root of your repository and change the line to ![ATORCH Energy Monitor Screenshot](screenshot.png))
🌟 Key Features

    Real-Time Data Display: View live measurements for Voltage (V), Current (A), Power (W), Resistance (Ω), Energy (Wh), Temperature (°C), and Battery Percentage (%).

    Live Interactive Chart: Plots Voltage, Current, and Power data over time.

        Zoom in on specific timeframes by clicking and dragging on the chart.

        Use the mouse wheel to zoom in and out.

        Instantly reset the chart view with the "Reset Zoom" button.

    Multi-Language Support: The interface is available in multiple languages, including English, Portuguese, Spanish, French, German, Italian, Russian, and Chinese.

    Auto-Detection of Devices: Automatically scans and lists available ATORCH devices on connection.

    Adjustable Refresh Rate: Choose how often data is read from the device (1, 3, or 5 seconds).

    Robust Error Handling: Automatically detects if the device is disconnected and safely stops the monitoring process.

    Cross-Platform: Built with Python and the PyQt5 framework, allowing it to run on multiple operating systems.

📋 Requirements

There are two ways to use this application: by running the pre-compiled executable or by running the script from the source code.
1. For Users (Running the .exe)

    Operating System: Windows 7, 10, or 11.

    Hardware: An ATORCH USB Energy Meter.

    Dependencies: None. All required libraries are bundled into the .exe file.

2. For Developers (Running from Source)

    Python: Python 3.8 or newer.

    Python Libraries:

        PyQt5

        PyQtChart

        hidapi

    You can install these dependencies using pip:
    code Sh

      
    pip install PyQt5 PyQtChart hidapi

      

🚀 How to Use
Option A: Recommended for Most Users (Pre-compiled Version)

    Navigate to the Releases page of this repository.

    Download the latest windows7_32bit_release.xip file.

    Extract the zip file.

    Run the gui.exe executable.

    Select your ATORCH device from the dropdown menu and click "Connect".

Option B: For Developers (Running from Source)

    Clone the repository:
    code Sh


    

Install the required libraries:
code Sh
   
pip install -r requirements.txt

  

(You will need to create a requirements.txt file containing PyQt5, PyQtChart, and hidapi, or just install them manually as shown above).

Run the application:
code Sh

          
    python3 gui.py

      

⚖️ License

This project is licensed under the MIT License. See the LICENSE file for details.

(You should create a file named LICENSE in your repository and paste the text of the MIT license into it).
🙏 Acknowledgments

    This application was built using the powerful PyQt5 framework for the user interface.

    Device communication is handled by the hidapi library.

    Code developed in collaboration with Gemini (Google AI Model).
