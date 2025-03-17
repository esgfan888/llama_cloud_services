import httpx
import os
from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Optional, Dict, Any, Union

from llama_index.core.async_utils import asyncio_run
from llama_cloud_services.parse.types import JobResult, JobMetadata, Page
from llama_cloud_services.parse.utils import make_api_request


class ParseResult(BaseModel):
    """Result of parsing a document."""

    job_id: str = Field(description="The job ID of the parsing task.")
    file_name: str = Field(description="The name of the file/object that was parsed.")
    _job_result: JobResult = PrivateAttr(default=None)
    _api_key: Optional[str] = PrivateAttr(default=None)
    _base_url: Optional[str] = PrivateAttr(default=None)

    def __init__(
        self,
        job_id: str,
        file_name: str,
        job_result: Union[Dict[str, Any], JobResult],
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        """
        Initialize ParseResult with job_id and job_result.

        Args:
            job_id: The job ID of the parsing task
            job_result: The JSON response from the parsing job or a JobResult instance (optional)
            api_key: The API key for the LlamaParse API
            base_url: The base URL of the Llama Parsing API
        """
        super().__init__(job_id=job_id, file_name=file_name)
        if job_result is not None:
            if isinstance(job_result, JobResult):
                self._job_result = job_result
                self._job_result.file_name = file_name
                self._job_result.job_id = job_id
            else:
                job_result["file_name"] = file_name
                job_result["job_id"] = job_id
                self._job_result = JobResult.model_validate(job_result)

        self._api_key = api_key or os.environ.get("LLAMA_CLOUD_API_KEY", "")
        self._base_url = base_url or os.environ.get(
            "LLAMA_CLOUD_BASE_URL", "https://api.llama-parse.ai"
        )
        self._client = client or httpx.AsyncClient()
        self._client.base_url = self._base_url
        self._client.headers["Authorization"] = f"Bearer {self._api_key}"

    def get_text(self, split_pages: bool = False) -> Union[str, List[str]]:
        """
        Get the plain text result of the parsing job.

        Returns:
            The plain text content
        """
        if split_pages:
            return [page.text for page in self._job_result.pages]

        return "\n".join([page.text for page in self._job_result.pages])

    def get_markdown(self, split_pages: bool = False) -> Union[str, List[str]]:
        """
        Get the markdown result of the parsing job.

        Returns:
            The markdown content
        """
        if split_pages:
            return [page.md for page in self._job_result.pages]

        return "\n".join([page.md for page in self._job_result.pages])

    def get_json(self) -> List[Dict[str, Any]]:
        """
        Get the JSON result of the parsing job.

        Returns:
            The parsed JSON content of the result
        """
        return self._job_result.model_dump()

    def get_structured(self) -> List[Dict[str, Any]]:
        """
        Get the structured result of the parsing job.

        Returns:
            The structured content as a list of page structured data
        """
        return [
            page.structuredData
            for page in self._job_result.pages
            if page.structuredData is not None
        ]

    def get_images(self) -> List[Dict[str, Any]]:
        """
        Get information about the images from the parsing job.

        Returns:
            A list of image information
        """
        images = []
        # Collect images from all pages
        for page in self._job_result.pages:
            for img in page.images:
                # Convert to dictionary with additional page info
                if isinstance(img, str):
                    # If image is just a string (name), create a dict
                    images.append({"name": img, "page": page.page})
                else:
                    # If image is already a dict or object, add page info
                    img_dict = img if isinstance(img, dict) else img.dict()
                    img_dict["page"] = page.page
                    images.append(img_dict)
        return images

    def get_image_names(self) -> List[str]:
        """
        Get the names of all images from the parsing job.

        Returns:
            A list of image names
        """
        images = self.get_images()
        return [img.get("name", "unknown.png") for img in images if "name" in img]

    def get_pages(self) -> List[Page]:
        """
        Get all pages from the structured result.

        Returns:
            A list of page information
        """
        return self._job_result.pages

    def get_tables(self) -> List[Dict[str, Any]]:
        """
        Get tables from the result if available.

        Returns:
            A list of tables from all pages
        """
        tables = []
        for page in self._job_result.pages:
            for table in page.tables:
                table_dict = table.dict() if hasattr(table, "dict") else table
                table_dict["page"] = page.page
                tables.append(table_dict)
        return tables

    def get_charts(self) -> List[Dict[str, Any]]:
        """
        Get charts from the result if available.

        Returns:
            A list of charts from all pages
        """
        charts = []
        for page in self._job_result.pages:
            # Add page number to each chart
            for chart in page.charts:
                if isinstance(chart, str):
                    charts.append({"name": chart, "page": page.page})
                else:
                    chart_dict = chart.dict() if hasattr(chart, "dict") else chart
                    chart_dict["page"] = page.page
                    charts.append(chart_dict)
        return charts

    def get_page_count(self) -> int:
        """
        Get the number of pages in the document.

        Returns:
            Number of pages
        """
        pages = self.get_pages()
        return len(pages)

    async def aget_image_data(self, image_name: str) -> bytes:
        """
        Get image data by name using the job ID.

        Args:
            image_name: The name of the image to fetch

        Returns:
            The image data as bytes
        """
        url = f"{self._base_url}/api/v1/parsing/job/{self.job_id}/result/image/{image_name}"
        response = await make_api_request(self._client, "GET", url)
        return response.content

    def get_image_data(self, image_name: str) -> bytes:
        """
        Get image data by name using the job ID (synchronous version).

        Args:
            image_name: The name of the image to fetch

        Returns:
            The image data as bytes
        """
        return asyncio_run(self.aget_image_data(image_name))

    async def aget_pdf_data(self) -> bytes:
        """
        Get the PDF data for the job.

        Returns:
            The PDF data as bytes
        """
        url = f"{self._base_url}/api/v1/parsing/job/{self.job_id}/result/pdf"
        response = await make_api_request(self._client, "GET", url)
        return response.content

    def get_pdf_data(self) -> bytes:
        """
        Get the PDF data for the job (synchronous version).

        Returns:
            The PDF data as bytes
        """
        return asyncio_run(self.aget_pdf_data())

    async def aget_xlsx_data(self) -> bytes:
        """
        Get the XLSX data for the job.

        Returns:
            The XLSX data as bytes
        """
        url = f"{self._base_url}/api/v1/parsing/job/{self.job_id}/result/xlsx"
        response = await make_api_request(self._client, "GET", url)
        return response.content

    def get_xlsx_data(self) -> bytes:
        """
        Get the XLSX data for the job (synchronous version).

        Returns:
            The XLSX data as bytes
        """
        return asyncio_run(self.aget_xlsx_data())

    async def asave_image(self, image_name: str, output_dir: str) -> str:
        """
        Save an image to a file.

        Args:
            image_name: The name of the image to fetch
            output_dir: The directory to save the image to

        Returns:
            The path to the saved image
        """
        image_data = await self.aget_image_data(image_name)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Save image to file
        output_path = os.path.join(output_dir, image_name)
        with open(output_path, "wb") as f:
            f.write(image_data)

        return output_path

    def save_image(self, image_name: str, output_dir: str) -> str:
        """
        Save an image to a file (synchronous version).

        Args:
            image_name: The name of the image to fetch
            output_dir: The directory to save the image to

        Returns:
            The path to the saved image
        """
        return asyncio_run(self.asave_image(image_name, output_dir))

    async def asave_all_images(self, output_dir: str) -> List[str]:
        """
        Save all images to files.

        Args:
            output_dir: The directory to save the images to

        Returns:
            A list of paths to the saved images
        """
        image_names = self.get_image_names()
        saved_paths = []

        for name in image_names:
            path = await self.asave_image(name, output_dir)
            saved_paths.append(path)

        return saved_paths

    def save_all_images(self, output_dir: str) -> List[str]:
        """
        Save all images to files (synchronous version).

        Args:
            output_dir: The directory to save the images to

        Returns:
            A list of paths to the saved images
        """
        return asyncio_run(self.asave_all_images(output_dir))

    def get_metadata(self) -> JobMetadata:
        """
        Get metadata and usage information about the document and parsing job.

        Returns:
            JobMetadata object
        """
        return self._job_result.job_metadata

    def get_status(self) -> str:
        """
        Get the current status of the parsing job.

        Returns:
            The status of the job ("SUCCESS", "ERROR", "PENDING")
        """
        if self._job_result.error:
            return "ERROR"
        return "SUCCESS"
