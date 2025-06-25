This is a simple GUI application to convert HDR videos to SDR using FFmpeg. The application allows you to select an input video file, drag and drop files into the application, specify an output file name, adjust the gamma value, and monitor the conversion progress.

## Features

- **Select Input Video Files**: Choose from video files with extensions `.mp4`, `.mkv`, and `.mov`.
- **Drag and Drop Files**: Simply drag and drop your video files into the application window for easy selection.
- **Specify Output File Name**: Define the name and location of the converted SDR video file.
- **Adjust Gamma Value**: Use a slider to adjust the gamma value for the conversion process, allowing for fine-tuning of the output video.
- **Monitor Conversion Progress**: A progress bar displays the current status of the conversion process.
- **Open Output File**: Option to automatically open the output file after the conversion is complete.
- **GPU Acceleration**: Utilize NVIDIA GPUs for faster conversion using CUDA if available.
- **Conversion Methods**: Choose between a static or dynamic conversion method. Static uses the same conversion no matter the file, dynamic takes the brightness of the original into account.
- **Tonemappers**: Choose between 3 different tonemappers Reinhard, Mobius, and Hable.

## Requirements

- Python 3.10 and above
- FFmpeg
- NVIDIA GPU (optional, for GPU acceleration)

## Installation

### Normal Installation

1. Download the latest release from the [releases page](https://github.com/TORlN/HDR-to-SDR/releases).
2. Run the `hdr_to_sdr_converter.exe` file.

### Development Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/TORlN/HDR-to-SDR
    cd <repository-directory>
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Ensure FFmpeg is installed and available in your system's PATH.

### Development Usage

1. Create a virtual environment:
    ```sh
    python -m venv .venv
    ```

2. Activate the virtual environment:
    - On Windows:
        ```sh
        .venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source .venv/bin/activate
        ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Place `ffmpeg.exe`, `ffprobe.exe`, and `ffplay.exe` in the src folder

5. Compile the executable:
    ```sh
    pyinstaller --onefile --noconsole --name "HDR_to_SDR_Converter" --icon=logo/icon.ico ^
        --paths=.venv\Lib\site-packages ^
        --hidden-import=numpy ^
        --hidden-import=numpy.core ^
        --add-data ".venv\Lib\site-packages\sv_ttk;sv_ttk" ^
        --add-data ".venv\Lib\site-packages\tkinterdnd2;tkinterdnd2" ^
        --add-data ".venv\Lib\site-packages\PIL;PIL" ^
        --add-binary "src\ffmpeg.exe;." ^
        --add-binary "src\ffprobe.exe;." ^
        --add-binary "src\ffplay.exe;." ^
        --collect-submodules numpy ^
        --log-level DEBUG ^
        src\main.pyw
    ```
6. The compiled executable will be located in the `dist` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
