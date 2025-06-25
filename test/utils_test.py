import unittest
from unittest.mock import patch, MagicMock, ANY
from src.utils import get_video_properties, run_ffmpeg_command, extract_frame, extract_frame_with_conversion
import subprocess  
from PIL import Image  # Added import
import json  # Ensure json is imported

# Constants
FFMPEG_EXECUTABLE = 'c:\\Users\\Torin\\Desktop\\HDR to SDR\\src\\ffmpeg.exe'
FFMPEG_FILTER = 'zscale=primaries=bt709:transfer=bt709:matrix=bt709,tonemap=reinhard,eq=gamma={gamma},scale={width}:{height}'

class TestGetVideoProperties(unittest.TestCase):

    @patch('src.utils.subprocess.Popen')
    def test_get_video_properties(self, mock_popen):
        # Mock subprocess.Popen to return a predefined JSON output as bytes, including 'format'
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (b'''
        {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "bit_rate": "5000000",
                    "codec_name": "h264",
                    "avg_frame_rate": "30/1",
                    "duration": "600.0"
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "bit_rate": "128000"
                }
            ],
            "format": {
                "duration": "600.0"
            }
        }
        ''', b'')
        mock_process.returncode = 0

        input_file = 'path/to/test_video.mkv'
        expected_properties = {
            "width": 1920,
            "height": 1080,
            "bit_rate": 5000000,
            "codec_name": "h264",
            "frame_rate": 30.0,
            "audio_codec": "aac",
            "audio_bit_rate": 128000,
            "duration": 600.0,
            "subtitle_streams": []  # Added this line
        }

        properties = get_video_properties(input_file)
        self.assertEqual(properties, expected_properties)

    @patch('src.utils.subprocess.Popen')
    def test_get_video_properties_with_subtitles(self, mock_popen):
        """Test that get_video_properties correctly parses subtitle streams."""
        # Mock subprocess.Popen to return a predefined JSON output with subtitles and 'format'
        mock_process = mock_popen.return_value
        mock_process.communicate.return_value = (
            json.dumps({
                "streams": [
                    {
                        "codec_type": "video",
                        "width": 1920,
                        "height": 1080,
                        "codec_name": "h264",
                        "avg_frame_rate": "30/1",
                        "bit_rate": "4000000",
                        "duration": "120.0"
                    },
                    {
                        "codec_type": "audio",
                        "codec_name": "aac",
                        "bit_rate": "128000"
                    },
                    {
                        "codec_type": "subtitle",
                        "codec_name": "srt",
                        "index": 2
                    }
                ],
                "format": {
                    "duration": "120.0"
                }
            }).encode('utf-8'),
            b''
        )
        mock_process.returncode = 0

        properties = get_video_properties("dummy_video.mp4")
        
        expected_properties = {
            "width": 1920,
            "height": 1080,
            "bit_rate": 4000000,
            "codec_name": "h264",
            "frame_rate": 30.0,
            "duration": 120.0,
            "audio_codec": "aac",
            "audio_bit_rate": 128000,
            "subtitle_streams": [
                {
                    "codec_type": "subtitle",
                    "codec_name": "srt",
                    "index": 2
                }
            ]
        }
        self.assertEqual(properties, expected_properties)

class TestRunFfmpegCommand(unittest.TestCase):

    @patch('subprocess.Popen')
    def test_run_ffmpeg_command_success(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'output', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = run_ffmpeg_command(['ffmpeg', '-i', 'input.mp4', 'output.mkv'])
        self.assertEqual(result, b'output')

    @patch('subprocess.Popen')
    def test_run_ffmpeg_command_failure(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'', b'error')
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        with self.assertRaises(RuntimeError):
            run_ffmpeg_command(['ffmpeg', '-i', 'input.mp4', 'output.mkv'])

class TestExtractFrame(unittest.TestCase):

    @patch('src.utils.run_ffmpeg_command')
    @patch('src.utils.get_video_properties')
    def test_extract_frame_success(self, mock_get_props, mock_run_ffmpeg):
        # Mock the video properties to have a duration of 90 seconds
        mock_get_props.return_value = {
            "width": 1920,
            "height": 1080,
            "bit_rate": 5000000,
            "codec_name": "h264",
            "frame_rate": 30.0,
            "audio_codec": "aac",
            "audio_bit_rate": 128000,
            "duration": 90.0,
            "subtitle_streams": []
        }

        # Provide valid PNG image bytes
        mock_run_ffmpeg.return_value = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
            b'\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00'
            b'\x18\xdd\x8d\x1b\x00\x00\x00\x00IEND\xaeB`\x82'
        )

        frame = extract_frame('input.mp4')
        self.assertIsInstance(frame, Image.Image)

        # Verify that ffmpeg was called with the correct command and timestamp
        expected_time = 90.0 / 3  # 30 seconds
        mock_run_ffmpeg.assert_called_once_with([
            ANY, '-ss', str(expected_time), '-i', 'input.mp4',
            '-vframes', '1', '-f', 'image2pipe', '-'
        ])

    @patch('subprocess.Popen')
    def test_extract_frame_failure(self, mock_popen):
        # Mock video properties first
        with patch('src.utils.get_video_properties') as mock_get_props:
            mock_get_props.return_value = {
                "width": 1920,
                "height": 1080,
                "bit_rate": 5000000,
                "codec_name": "h264",
                "frame_rate": 30.0,
                "audio_codec": "aac",
                "audio_bit_rate": 128000,
                "duration": 90.0,
                "subtitle_streams": []
            }

            # Setup the ffmpeg command failure
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b'', b'error')
            mock_process.returncode = 1
            mock_popen.return_value = mock_process

            with self.assertRaises(RuntimeError):
                extract_frame('input.mp4')

class TestExtractFrameWithConversion(unittest.TestCase):

    @patch('src.utils.get_maxfall')  # Added patch for get_maxfall
    @patch('src.utils.run_ffmpeg_command')
    def test_extract_frame_with_conversion_success(self, mock_run_ffmpeg, mock_get_maxfall):
        # Mock the video properties to have a duration of 90 seconds
        with patch('src.utils.get_video_properties') as mock_get_props:
            mock_get_props.return_value = {
                "width": 1920,
                "height": 1080,
                "bit_rate": 4000000,
                "codec_name": "h264",
                "frame_rate": 30.0,
                "audio_codec": "aac",
                "audio_bit_rate": 128000,
                "duration": 90.0,
                "subtitle_streams": []
            }

            # Provide valid PNG image bytes
            mock_run_ffmpeg.return_value = (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
                b'\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00'
                b'\x18\xdd\x8d\x1b\x00\x00\x00\x00IEND\xaeB`\x82'
            )

            mock_get_maxfall.return_value = 100.0  # Mocked get_maxfall return value
            gamma = 2.2
            frame = extract_frame_with_conversion('input.mp4', gamma, filter_index=1)  # Added filter_index
            
            # Update the expected_vf string to match actual format
            expected_vf = 'zscale=t=linear:npl=100.0,tonemap=reinhard,zscale=t=bt709:m=bt709:r=tv:p=bt709,eq=gamma=2.2,scale=iw:ih'
            
            self.assertIsInstance(frame, Image.Image)
    
            # Verify that ffmpeg was called with the correct command and timestamp
            expected_time = 90.0 / 3  # 30 seconds
    
            mock_run_ffmpeg.assert_called_once()
            actual_args = mock_run_ffmpeg.call_args[0][0]
            
            # Check all arguments except the first one (ffmpeg path)
            self.assertEqual(actual_args[1:], [
                '-ss', str(expected_time), '-i', 'input.mp4',
                '-vf', expected_vf, '-vframes', '1', '-f', 'image2pipe', '-'
            ])

    @patch('src.utils.run_ffmpeg_command')
    @patch('src.utils.get_maxfall')  # Added patch for get_maxfall
    def test_extract_frame_with_conversion_failure(self, mock_run_ffmpeg, mock_get_maxfall):
        # Mock video properties first
        with patch('src.utils.get_video_properties') as mock_get_props:
            mock_get_props.return_value = {
                "width": 1920,
                "height": 1080,
                "bit_rate": 4000000,
                "codec_name": "h264",
                "frame_rate": 30.0,
                "audio_codec": "aac",
                "audio_bit_rate": 128000,
                "duration": 90.0,
                "subtitle_streams": []
            }

            # Mock get_maxfall to return a predefined value
            mock_get_maxfall.return_value = 100.0  # Mocked get_maxfall return value

            # Setup run_ffmpeg_command to raise RuntimeError to simulate failure
            mock_run_ffmpeg.side_effect = RuntimeError("FFmpeg conversion failed")

            with self.assertRaises(RuntimeError):
                extract_frame_with_conversion('input.mp4', gamma=2.2, filter_index=1)  # Added gamma and filter_index

if __name__ == '__main__':
    unittest.main()
    unittest.main()