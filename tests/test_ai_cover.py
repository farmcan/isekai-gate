import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from isekai_live.ai_cover import AIProvider, generate_cover, generate_cover_qwen


class AICoverTests(unittest.TestCase):
    def test_generate_cover_qwen_submits_task_polls_and_downloads_image(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_image = Path(tmpdir) / "input.jpg"
            output_image = Path(tmpdir) / "output.png"
            input_image.write_bytes(b"fake-image")

            responses = [
                {"output": {"task_id": "task-123", "task_status": "PENDING", "results": []}},
                {
                    "output": {
                        "task_id": "task-123",
                        "task_status": "SUCCEEDED",
                        "results": [{"url": "https://example.com/result.png"}],
                    }
                },
            ]

            with patch("isekai_live.ai_cover._dashscope_post_json", side_effect=responses) as post_mock:
                with patch("isekai_live.ai_cover._download_binary", return_value=b"png-bytes") as download_mock:
                    with patch("isekai_live.ai_cover.time.sleep"):
                        result = generate_cover_qwen(
                            input_image=input_image,
                            prompt="cartoon portrait",
                            output_path=output_image,
                            api_key="sk-test",
                        )
                        self.assertEqual(result, output_image)
                        self.assertEqual(output_image.read_bytes(), b"png-bytes")
                        self.assertEqual(post_mock.call_count, 2)
                        create_call = post_mock.call_args_list[0]
                        self.assertEqual(
                            create_call.args[0],
                            "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis",
                        )
                        self.assertEqual(create_call.kwargs["api_key"], "sk-test")
                        self.assertEqual(create_call.kwargs["payload"]["model"], "wanx2.1-imageedit")
                        self.assertEqual(create_call.kwargs["payload"]["input"]["function"], "stylization_all")
                        self.assertEqual(create_call.kwargs["payload"]["input"]["prompt"], "cartoon portrait")
                        self.assertTrue(create_call.kwargs["payload"]["input"]["base_image_url"].startswith("data:image/jpeg;base64,"))

                        poll_call = post_mock.call_args_list[1]
                        self.assertEqual(
                            poll_call.args[0],
                            "https://dashscope.aliyuncs.com/api/v1/tasks/task-123",
                        )
                        self.assertIsNone(poll_call.kwargs["payload"])
                        download_mock.assert_called_once_with("https://example.com/result.png")

    def test_generate_cover_qwen_raises_when_task_fails(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_image = Path(tmpdir) / "input.jpg"
            output_image = Path(tmpdir) / "output.png"
            input_image.write_bytes(b"fake-image")

            responses = [
                {"output": {"task_id": "task-123", "task_status": "PENDING", "results": []}},
                {
                    "output": {
                        "task_id": "task-123",
                        "task_status": "FAILED",
                        "message": "quota exceeded",
                    }
                },
            ]

            with patch("isekai_live.ai_cover._dashscope_post_json", side_effect=responses):
                with patch("isekai_live.ai_cover.time.sleep"):
                    with self.assertRaises(RuntimeError) as exc:
                        generate_cover_qwen(
                            input_image=input_image,
                            prompt="cartoon portrait",
                            output_path=output_image,
                            api_key="sk-test",
                        )

        self.assertIn("quota exceeded", str(exc.exception))

    def test_generate_cover_dispatches_to_qwen_provider(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_image = Path(tmpdir) / "input.jpg"
            output_image = Path(tmpdir) / "output.png"
            input_image.write_bytes(b"fake-image")

            with patch("isekai_live.ai_cover.generate_cover_qwen", return_value=output_image) as qwen_mock:
                result = generate_cover(
                    input_image=input_image,
                    prompt="cartoon portrait",
                    output_path=output_image,
                    provider=AIProvider.QWEN,
                    qwen_key="sk-test",
                )

        self.assertEqual(result, output_image)
        qwen_mock.assert_called_once()
