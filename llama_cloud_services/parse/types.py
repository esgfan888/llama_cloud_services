from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class JobMetadata(BaseModel):
    """Metadata about the job."""

    credits_used: int = Field(description="The number of credits used for the job.")
    job_credits_usage: int = Field(
        default_factory=dict, description="The credits usage for the job."
    )
    job_pages: int = Field(description="The number of pages in the job.")
    job_auto_mode_triggered_pages: int = Field(
        description="The number of pages that triggered auto mode (thus increasing the cost)."
    )
    job_is_cache_hit: bool = Field(description="Whether the job was a cache hit.")


class BBox(BaseModel):
    """A bounding box."""

    x: float = Field(description="The x-coordinate of the bounding box.")
    y: float = Field(description="The y-coordinate of the bounding box.")
    w: float = Field(description="The width of the bounding box.")
    h: float = Field(description="The height of the bounding box.")


class PageItem(BaseModel):
    """An item in a page."""

    type: str = Field(description="The type of the item.")
    lvl: Optional[int] = Field(
        default=None, description="The level of indentation of the item."
    )
    value: Optional[str] = Field(
        default=None, description="The text content of the item."
    )
    md: Optional[str] = Field(
        default=None, description="The markdown-formatted content of the item."
    )
    rows: Optional[List[List[str]]] = Field(
        default=None, description="The rows of the item."
    )
    bBox: BBox = Field(description="The bounding box of the item.")


class ImageItem(BaseModel):
    """An image in a page."""

    name: str = Field(description="The name of the image.")
    height: float = Field(description="The height of the image.")
    width: float = Field(description="The width of the image.")
    x: float = Field(description="The x-coordinate of the image.")
    y: float = Field(description="The y-coordinate of the image.")
    original_width: int = Field(description="The original width of the image.")
    original_height: int = Field(description="The original height of the image.")
    type: str = Field(description="The type of the image.")


class LayoutItem(BaseModel):
    """The layout of a page."""

    image: str = Field(description="The name of the image containing the layout item")
    confidence: float = Field(description="The confidence of the layout item.")
    label: str = Field(description="The label of the layout item.")
    bbox: BBox = Field(description="The bounding box of the layout item.")
    isLikelyNoise: bool = Field(description="Whether the layout item is likely noise.")


class Page(BaseModel):
    """A page of the document."""

    page: int = Field(description="The page number.")
    text: str = Field(description="The text of the page.")
    md: str = Field(description="The markdown of the page.")
    images: List[ImageItem] = Field(
        default_factory=list,
        description="The names of the image IDs in the page, including both objects and page screenshots.",
    )
    charts: List[str] = Field(
        default_factory=list, description="The names of the chart IDs in the page."
    )
    tables: List[str] = Field(
        default_factory=list, description="The names of the table IDs in the page."
    )
    layout: List[LayoutItem] = Field(
        default_factory=list, description="The layout of the page."
    )
    items: List[PageItem] = Field(
        default_factory=list, description="The items in the page."
    )
    status: str = Field(description="The status of the page.")
    links: List[str] = Field(default_factory=list, description="The links in the page.")
    width: int = Field(description="The width of the page.")
    height: int = Field(description="The height of the page.")
    triggeredAutoMode: bool = Field(
        description="Whether the page triggered auto mode (thus increasing the cost)."
    )
    parsingMode: str = Field(description="The parsing mode used for the page.")
    structuredData: Optional[Dict[str, Any]] = Field(
        description="The structured data of the page."
    )
    noStructuredContent: bool = Field(
        description="Whether the page has no structured data."
    )
    noTextContent: bool = Field(description="Whether the page has no text content.")


class JobResult(BaseModel):
    """The raw JSON result from the LlamaParse API."""

    pages: List[Page] = Field(description="The pages of the document.")
    job_metadata: JobMetadata = Field(description="The metadata of the job.")
    file_name: str = Field(description="The path to the file that was parsed.")
    job_id: str = Field(description="The ID of the job.")
    is_done: bool = Field(default=False, description="Whether the job is done.")
    error: Optional[str] = Field(
        default=None, description="The error message if the job failed."
    )
