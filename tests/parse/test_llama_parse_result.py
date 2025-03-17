import tempfile
import os
import pytest
from llama_cloud_services import LlamaParse
from llama_cloud_services.parse.result import ParseResult


@pytest.fixture
def file_path() -> str:
    return "tests/test_files/attention_is_all_you_need.pdf"


@pytest.mark.asyncio
async def test_basic_parse_result(file_path: str):
    parser = LlamaParse(
        take_screenshot=True,
        auto_mode=True,
        # extract_charts=True,
        # extract_layout=True,
        # structured_output=True,
        # structured_output_json_schema_name="imFeelingLucky",
        fast_mode=False,
        result_type="markdown",
        # invalidate_cache=True,
    )
    result = await parser.aparse(file_path)

    assert isinstance(result, ParseResult)
    assert result.job_id is not None
    assert result.file_name == file_path
    assert result.get_status() == "SUCCESS"

    assert result.get_text() is not None
    assert len(result.get_text()) > 0

    assert result.get_markdown() is not None
    assert len(result.get_markdown()) > 0

    assert result.get_markdown() != result.get_text()

    assert len(result.get_image_names()) > 0
    assert await result.aget_image_data(result.get_image_names()[0]) is not None

    with tempfile.TemporaryDirectory() as temp_dir:
        file_names = await result.asave_all_images(temp_dir)
        assert len(file_names) > 0
        for file_name in file_names:
            assert os.path.exists(file_name)
            assert os.path.getsize(file_name) > 0

    assert result.get_metadata() is not None
