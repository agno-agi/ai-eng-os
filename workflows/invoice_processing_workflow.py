import base64
import json
import uuid
from textwrap import dedent
from typing import Any, Dict, List, Optional, cast
from urllib.parse import urlparse

import httpx
from agno.agent import Agent
from agno.media import File
from agno.models.openai import OpenAIChat
from agno.utils.log import logger
from agno.workflow import Step, Workflow
from agno.workflow.types import StepInput, StepOutput
from pydantic import BaseModel, Field

from db.demo_db import demo_db


# ============================================================================
# Input/Output Schemas
# ============================================================================
class LineItem(BaseModel):
    """Individual line item in an invoice"""

    description: str = Field(description="Description of the item or service")
    quantity: Optional[float] = Field(default=None, description="Quantity of items")
    unit_price: Optional[float] = Field(default=None, description="Price per unit")
    amount: float = Field(description="Total amount for this line item")


class InvoiceData(BaseModel):
    """Structured invoice data extracted from PDF"""

    vendor_name: str = Field(description="Name of the vendor/supplier")
    vendor_address: Optional[str] = Field(default=None, description="Vendor address")
    invoice_number: str = Field(description="Invoice number")
    invoice_date: str = Field(description="Invoice date")
    due_date: Optional[str] = Field(default=None, description="Payment due date")
    line_items: List[LineItem] = Field(description="List of line items")
    subtotal: Optional[float] = Field(default=None, description="Subtotal before tax")
    tax_amount: Optional[float] = Field(default=None, description="Tax amount")
    total_amount: float = Field(description="Total invoice amount")
    currency: str = Field(default="USD", description="Currency code")
    notes: Optional[str] = Field(default=None, description="Additional notes or payment terms")


class InvoiceRequest(BaseModel):
    """Input request for invoice processing"""

    file_link: str = Field(description="Invoice PDF file URL")
    model_id: str = Field(default="gpt-4.1", description="Model to use for extraction")


# ============================================================================
# Create Invoice Processing Agents
# ============================================================================
def create_extraction_agent(model_id: str = "gpt-4.1") -> Agent:
    """Create an extraction agent with the specified model"""
    return Agent(
        name="Invoice Extraction Agent",
        role="Extract structured data from invoice PDFs",
        model=OpenAIChat(id=model_id),
        description=dedent("""\
            You are an expert at extracting structured information from invoice documents.
            You analyze PDFs and extract all relevant invoice data accurately.
            """),
        instructions=dedent("""\
            Extract structured invoice data from the provided PDF document.
            
            Your task:
            1. Identify and extract all invoice fields including vendor info, dates, line items, and amounts
            2. For line items, extract description, quantity, unit price, and total amount
            3. Extract tax information and calculate totals
            4. Handle various invoice formats and layouts
            5. If a field is not found, use None or reasonable defaults
            6. Ensure amounts are parsed as numbers (remove currency symbols)
            
            Be thorough and accurate. The extracted data will be used for payment processing.
            Return data according to the InvoiceData schema.
            """),
        output_schema=InvoiceData,
        add_history_to_context=True,
        markdown=True,
        db=demo_db,
    )


def create_validation_agent(model_id: str = "gpt-4.1") -> Agent:
    """Create a validation agent with the specified model"""
    return Agent(
        name="Invoice Validation Agent",
        role="Validate and correct extracted invoice data",
        model=OpenAIChat(id=model_id),
        description=dedent("""\
            You are a validation specialist who ensures invoice data is complete and accurate
            before processing for payment. You verify against the original PDF document.
            """),
        instructions=dedent("""\
            Review and validate the extracted invoice data against the original PDF.
            
            Your task:
            1. Compare the extracted data with the PDF to verify accuracy
            2. Check that all required fields are present and correct
            3. Verify that line item amounts sum to the correct subtotal
            4. Verify that subtotal + tax = total amount
            5. Correct any extraction errors you find
            6. Flag any discrepancies or missing information
            
            Return the validated (and corrected if needed) data according to the InvoiceData schema.
            """),
        output_schema=InvoiceData,
        add_history_to_context=True,
        markdown=True,
        db=demo_db,
    )


# ============================================================================
# Workflow Step Functions
# ============================================================================
def download_pdf_file(step_input: StepInput) -> StepOutput:
    """Download PDF from any public URL and return base64-encoded content."""
    request = cast(InvoiceRequest, step_input.input)
    url = request.file_link.strip()
    logger.info(f"Downloading file from: {url}")

    def filename_from_url(url: str) -> str:
        """Extract filename from URL or generate a unique one."""
        name = urlparse(url).path.split("/")[-1]
        return name or f"invoice_{uuid.uuid4()}.pdf"

    try:
        # Download file from public URL
        response = httpx.get(url, follow_redirects=True, timeout=30)
        response.raise_for_status()
        file_bytes = response.content

        logger.info(f"Successfully downloaded {len(file_bytes)} bytes")

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.reason_phrase}"
        logger.error(f"Failed to download file: {error_msg}")
        return StepOutput(content={"error": error_msg}, success=False, stop=True)

    except Exception as e:
        error_msg = f"Failed to download file: {str(e)}"
        logger.error(error_msg)
        return StepOutput(content={"error": error_msg}, success=False, stop=True)

    filename = filename_from_url(url)
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")

    return StepOutput(
        content={"base64_pdf": base64_pdf, "file_link": url, "filename": filename},
        success=True,
    )


async def extraction_step(step_input: StepInput) -> StepOutput:
    """Extract invoice data directly from PDF using the specified model."""
    request = cast(InvoiceRequest, step_input.input)
    pdf_data = cast(Dict[str, Any], step_input.get_step_content("Download PDF"))

    if not pdf_data or "base64_pdf" not in pdf_data:
        return StepOutput(content={"error": "No PDF data available"}, success=False, stop=True)

    file_link = pdf_data.get("file_link", request.file_link)
    model_id = request.model_id
    logger.info(f"Running invoice extraction with {model_id} for: {file_link}")

    # Recreate File object from base64 PDF
    pdf_content = base64.b64decode(pdf_data["base64_pdf"])
    pdf_file = File(
        content=pdf_content,
        filename=pdf_data.get("filename", "invoice.pdf"),
        mime_type="application/pdf",
    )

    # Create agent with specified model
    extraction_agent = create_extraction_agent(model_id)

    query = """
        Extract structured invoice data from the attached PDF.

        Analyze the document and extract all relevant fields according to the InvoiceData schema.
        Be thorough and accurate.
    """

    result = await extraction_agent.arun(query, files=[pdf_file])

    # Get the structured output
    extracted_data = result.content if hasattr(result, "content") else result

    # Serialize the data
    if extracted_data and hasattr(extracted_data, "model_dump"):
        serialized_data = extracted_data.model_dump()
    elif isinstance(extracted_data, dict):
        serialized_data = extracted_data
    else:
        serialized_data = str(extracted_data) if extracted_data else {}

    return StepOutput(
        content={
            "extracted_data": serialized_data,
            "model_used": model_id,
            "extraction_complete": True,
        },
        success=True,
    )


async def validation_step_executor(step_input: StepInput) -> StepOutput:
    """Validate extracted invoice data against the original PDF."""
    request = cast(InvoiceRequest, step_input.input)

    # Get extraction result from previous step
    extraction_data = cast(Dict[str, Any], step_input.get_step_content("Extract Invoice Data"))
    pdf_data = cast(Dict[str, Any], step_input.get_step_content("Download PDF"))

    if not extraction_data:
        return StepOutput(content={"error": "No extraction data"}, success=False, stop=True)

    if not pdf_data or "base64_pdf" not in pdf_data:
        return StepOutput(content={"error": "No PDF data"}, success=False, stop=True)

    file_link = pdf_data.get("file_link", request.file_link)
    model_id = request.model_id
    logger.info(f"Running validation with {model_id} for: {file_link}")

    # Recreate File object
    pdf_content = base64.b64decode(pdf_data["base64_pdf"])
    pdf_file = File(
        content=pdf_content,
        filename=pdf_data.get("filename", "invoice.pdf"),
        mime_type="application/pdf",
    )

    # Create validation agent with specified model
    validation_agent = create_validation_agent(model_id)

    query = f"""
        Review and validate the following invoice extraction result against the PDF.
        Verify accuracy and completeness, making corrections if needed.

        Extracted Data:
        {json.dumps(extraction_data.get("extracted_data", {}), indent=2)}

        Return the validated, corrected data according to the InvoiceData schema.
    """

    result = await validation_agent.arun(query, files=[pdf_file])

    # Get the structured output
    validated_data = result.content if hasattr(result, "content") else result

    # Serialize the data
    if validated_data and hasattr(validated_data, "model_dump"):
        serialized_data = validated_data.model_dump()
    elif isinstance(validated_data, dict):
        serialized_data = validated_data
    else:
        serialized_data = str(validated_data) if validated_data else {}

    return StepOutput(
        content={
            "invoice_data": serialized_data,
            "model_used": model_id,
            "validation_complete": True,
        },
        success=True,
    )


# ============================================================================
# Create Workflow Steps
# ============================================================================
download_pdf_step = Step(
    name="Download PDF",
    executor=download_pdf_file,
)

extraction_step_def = Step(
    name="Extract Invoice Data",
    executor=extraction_step,
)

validation_step_def = Step(
    name="Validate Invoice Data",
    executor=validation_step_executor,
)

# ============================================================================
# Create the Workflow
# ============================================================================
invoice_workflow = Workflow(
    name="Invoice Processing Workflow",
    description=dedent("""\
        Invoice Processing Workflow that extracts structured data from invoice PDFs and validates the extracted information.
        """),
    input_schema=InvoiceRequest,
    steps=[
        download_pdf_step,
        extraction_step_def,
        validation_step_def,
    ],
    db=demo_db,
)
