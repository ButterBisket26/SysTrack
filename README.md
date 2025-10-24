# SysTrack - System Resource Monitor

SysTrack is a real-time system resource monitoring application built with Python and customtkinter. It provides detailed insights into CPU, GPU, RAM, disk, network usage, and system performance through a user-friendly graphical interface.

## Features

- Real-time monitoring of CPU usage, per-core stats, temperature, and frequency.
- GPU utilization, memory, and temperature tracking.
- RAM and disk usage overview.
- Network upload and download speed monitoring.
- Frames per second (FPS) performance measurement.
- Interactive graphs and progress bars for visual data representation.
- Process listing with top CPU and memory-consuming processes.
- Logging system metrics to a CSV file.
- Alerts for high usage thresholds.

## Installation

1. Clone the repository
git clone https://github.com/ButterBisket26/SysTrack.git


2. Install dependencies

> Note: Dependencies include `customtkinter`, `psutil`, `matplotlib`, and `GPUtil`.

## Usage

Run the main program:

python main.py

The application window will open displaying system resource stats. Use the tabs to navigate different views and enable logging if needed.

## Demo Video

Below is a demo video showcasing SysTrack's features and interface:

![SysTrack Demo](demo_video.gif)

> To include a video on your GitHub README:
> - Convert your demo video to a GIF for inline display, or
> - Upload the video file to your repository or an external hosting platform (e.g., YouTube, Vimeo).
> - Link to the video using Markdown:
> 
> For a GIF:
> ```
> ![Demo](path/to/demo_videoideo link:
> ```
> [Watch Demo Video](https://your-video-link)
> ```

## Logging

Enable logging using the switch in the application to record system stats into `systemlog.csv`.

## Contribution

Contributions, issues, and feature requests are welcome. Feel free to check [issues](https://github.com/ButterBisket26/SysTrack/issues) or submit a pull request.

## License

This project is licensed under the MIT License.

---



