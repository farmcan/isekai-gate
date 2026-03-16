import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from isekai_live.ai_video import VideoStyle, generate_stylized_video_qwen


class AIVideoTests(unittest.TestCase):
    def test_generate_stylized_video_qwen_uploads_local_video_polls_and_downloads(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_video = Path(tmpdir) / "input.mov"
            output_video = Path(tmpdir) / "output.mp4"
            input_video.write_bytes(b"fake-video")

            responses = [
                {"output": {"task_id": "task-456", "task_status": "PENDING"}},
                {
                    "output": {
                        "task_id": "task-456",
                        "task_status": "SUCCEEDED",
                        "output_video_url": "https://example.com/result.mp4",
                    }
                },
            ]

            with patch("isekai_live.ai_video._upload_file_get_oss_url", return_value="oss://dashscope-instant/demo/input.mov") as upload_mock:
                with patch("isekai_live.ai_video._dashscope_request_json", side_effect=responses) as request_mock:
                    with patch("isekai_live.ai_video._download_binary", return_value=b"mp4-bytes") as download_mock:
                        with patch("isekai_live.ai_video.time.sleep"):
                            result = generate_stylized_video_qwen(
                                input_video=input_video,
                                output_path=output_video,
                                style=VideoStyle.ANIME,
                                api_key="sk-test",
                                resolution=540,
                            )
                            self.assertEqual(result, output_video)
                            self.assertEqual(output_video.read_bytes(), b"mp4-bytes")
                            upload_mock.assert_called_once_with("sk-test", "video-style-transform", input_video)
                            self.assertEqual(request_mock.call_count, 2)
                            create_call = request_mock.call_args_list[0]
                            self.assertEqual(
                                create_call.args[0],
                                "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis",
                            )
                            self.assertEqual(create_call.kwargs["payload"]["model"], "video-style-transform")
                            self.assertEqual(create_call.kwargs["payload"]["input"]["video_url"], "oss://dashscope-instant/demo/input.mov")
                            self.assertEqual(create_call.kwargs["payload"]["parameters"]["style"], 0)
                            self.assertEqual(create_call.kwargs["payload"]["parameters"]["min_len"], 540)
                            self.assertEqual(create_call.kwargs["extra_headers"]["X-DashScope-OssResourceResolve"], "enable")
                            poll_call = request_mock.call_args_list[1]
                            self.assertEqual(
                                poll_call.args[0],
                                "https://dashscope.aliyuncs.com/api/v1/tasks/task-456",
                            )
                            download_mock.assert_called_once_with("https://example.com/result.mp4")

    def test_generate_stylized_video_qwen_raises_when_task_fails(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_video = Path(tmpdir) / "input.mov"
            output_video = Path(tmpdir) / "output.mp4"
            input_video.write_bytes(b"fake-video")

            responses = [
                {"output": {"task_id": "task-456", "task_status": "PENDING"}},
                {"output": {"task_id": "task-456", "task_status": "FAILED", "message": "quota exceeded"}},
            ]

            with patch("isekai_live.ai_video._upload_file_get_oss_url", return_value="oss://dashscope-instant/demo/input.mov"):
                with patch("isekai_live.ai_video._dashscope_request_json", side_effect=responses):
                    with patch("isekai_live.ai_video.time.sleep"):
                        with self.assertRaises(RuntimeError) as exc:
                            generate_stylized_video_qwen(
                                input_video=input_video,
                                output_path=output_video,
                                style=VideoStyle.THREE_D_CARTOON,
                                api_key="sk-test",
                            )

        self.assertIn("quota exceeded", str(exc.exception))
