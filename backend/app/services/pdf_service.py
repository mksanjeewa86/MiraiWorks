import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from app.models.resume import Resume
from app.services.storage_service import get_storage_service
from app.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF resumes from HTML templates."""

    def __init__(self):
        self.template_service = TemplateService()
        # Storage service will be lazily loaded when needed

    async def generate_pdf(
        self,
        resume: Resume,
        format: str = "A4",
        include_contact_info: bool = True,
        watermark: Optional[str] = None,
        custom_css: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate PDF from resume data."""
        try:
            # Render HTML
            html_content = await self.template_service.render_resume(
                resume, resume.template_id, custom_css
            )

            # Modify HTML for PDF generation
            pdf_html = self._prepare_html_for_pdf(
                html_content, format, include_contact_info, watermark
            )

            # Generate PDF
            pdf_data = await self._convert_html_to_pdf(pdf_html, format)

            # Upload to storage
            filename = f"resume_{resume.id}_{uuid.uuid4().hex[:8]}.pdf"
            file_path = await get_storage_service().upload_file(
                pdf_data, filename, "resumes/pdfs", content_type="application/pdf"
            )

            # Generate temporary download URL
            download_url = await get_storage_service().generate_presigned_url(
                file_path,
                expires_in=3600,  # 1 hour
            )

            # Update resume record
            resume.pdf_file_path = file_path
            resume.pdf_generated_at = datetime.utcnow()
            resume.download_count = (resume.download_count or 0) + 1

            result = {
                "pdf_url": download_url,
                "file_path": file_path,
                "file_size": len(pdf_data),
                "expires_at": datetime.utcnow() + timedelta(hours=1),
            }

            logger.info(
                f"Generated PDF for resume {resume.id}, size: {len(pdf_data)} bytes"
            )
            return result

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

    async def _convert_html_to_pdf(
        self, html_content: str, format: str = "A4"
    ) -> bytes:
        """Convert HTML content to PDF using playwright or weasyprint."""
        try:
            # Option 1: Using playwright (recommended for better CSS support)
            if await self._is_playwright_available():
                return await self._convert_with_playwright(html_content, format)

            # Option 2: Using weasyprint (fallback)
            elif await self._is_weasyprint_available():
                return await self._convert_with_weasyprint(html_content, format)

            else:
                raise RuntimeError(
                    "No PDF generation library available (playwright or weasyprint)"
                )

        except Exception as e:
            logger.error(f"Error converting HTML to PDF: {str(e)}")
            raise

    async def _convert_with_playwright(self, html_content: str, format: str) -> bytes:
        """Convert HTML to PDF using Playwright."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Set content
                await page.set_content(html_content, wait_until="networkidle")

                # Configure PDF options
                pdf_options = {
                    "format": format,
                    "print_background": True,
                    "margin": {
                        "top": "0.5in",
                        "right": "0.5in",
                        "bottom": "0.5in",
                        "left": "0.5in",
                    },
                }

                # Generate PDF
                pdf_data = await page.pdf(**pdf_options)
                await browser.close()

                return pdf_data

        except ImportError:
            raise RuntimeError(
                "Playwright not installed. Install with: pip install playwright"
            )
        except Exception as e:
            logger.error(f"Playwright PDF conversion error: {str(e)}")
            raise

    async def _convert_with_weasyprint(self, html_content: str, format: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint."""
        try:
            import weasyprint

            # Configure CSS for print
            css_string = f"""
            @page {{
                size: {format};
                margin: 0.5in;
            }}

            body {{
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
            """

            # Convert to PDF
            html_doc = weasyprint.HTML(string=html_content)
            css_doc = weasyprint.CSS(string=css_string)

            pdf_data = html_doc.write_pdf(stylesheets=[css_doc])
            return pdf_data

        except ImportError:
            raise RuntimeError(
                "WeasyPrint not installed. Install with: pip install weasyprint"
            )
        except Exception as e:
            logger.error(f"WeasyPrint PDF conversion error: {str(e)}")
            raise

    def _prepare_html_for_pdf(
        self,
        html_content: str,
        format: str,
        include_contact_info: bool,
        watermark: Optional[str],
    ) -> str:
        """Prepare HTML content for PDF generation."""

        # Add PDF-specific styles
        pdf_css = (
            """
        <style>
        @media print {
            .no-print { display: none !important; }
            .page-break { page-break-before: always; }
            .avoid-break { page-break-inside: avoid; }

            body {
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }

            a {
                color: inherit !important;
                text-decoration: none !important;
            }

            .resume-container {
                box-shadow: none !important;
                border: none !important;
            }
        }

        @page {
            margin: 0.5in;
            size: """
            + format
            + """;
        }

        .watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 4rem;
            color: rgba(0, 0, 0, 0.1);
            z-index: -1;
            pointer-events: none;
        }
        </style>
        """
        )

        # Remove contact info if requested
        if not include_contact_info:
            # This is a simple approach - in production, you'd want more sophisticated handling
            html_content = html_content.replace("contact-info", "contact-info no-print")

        # Add watermark if specified
        watermark_html = ""
        if watermark:
            watermark_html = f'<div class="watermark">{watermark}</div>'

        # Insert PDF styles and watermark
        html_content = html_content.replace("</head>", f"{pdf_css}</head>")
        html_content = html_content.replace("<body>", f"<body>{watermark_html}")

        return html_content

    async def _is_playwright_available(self) -> bool:
        """Check if Playwright is available."""
        try:
            return True
        except ImportError:
            return False

    async def _is_weasyprint_available(self) -> bool:
        """Check if WeasyPrint is available."""
        try:
            return True
        except ImportError:
            return False

    async def get_pdf_preview_image(self, resume: Resume) -> Optional[str]:
        """Generate a preview image of the PDF."""
        try:
            # This would generate a thumbnail/preview image of the first page
            # Implementation depends on available libraries (pdf2image, etc.)

            if not resume.pdf_file_path:
                return None

            # Download PDF from storage
            pdf_data = await get_storage_service().download_file(resume.pdf_file_path)

            # Convert first page to image
            preview_data = await self._pdf_to_image(pdf_data)

            if preview_data:
                # Upload preview image
                preview_filename = (
                    f"resume_preview_{resume.id}_{uuid.uuid4().hex[:8]}.png"
                )
                preview_path = await get_storage_service().upload_file(
                    preview_data,
                    preview_filename,
                    "resumes/previews",
                    content_type="image/png",
                )

                return await get_storage_service().generate_presigned_url(preview_path)

            return None

        except Exception as e:
            logger.error(f"Error generating PDF preview: {str(e)}")
            return None

    async def _pdf_to_image(self, pdf_data: bytes) -> Optional[bytes]:
        """Convert first page of PDF to image."""
        try:
            # Using pdf2image library
            from io import BytesIO

            from pdf2image import convert_from_bytes

            images = convert_from_bytes(pdf_data, first_page=1, last_page=1, dpi=150)

            if images:
                img_buffer = BytesIO()
                images[0].save(img_buffer, format="PNG", optimize=True)
                return img_buffer.getvalue()

            return None

        except ImportError:
            logger.warning("pdf2image not available for preview generation")
            return None
        except Exception as e:
            logger.error(f"Error converting PDF to image: {str(e)}")
            return None

    async def bulk_generate_pdfs(
        self, resume_ids: list[int], user_id: int
    ) -> dict[str, Any]:
        """Generate PDFs for multiple resumes."""
        results = {"success": [], "errors": [], "total": len(resume_ids)}

        # This could be implemented as a background task for large batches
        for resume_id in resume_ids:
            try:
                # Get resume with ownership check
                from app.database import get_db

                async with get_db() as db:
                    from app.services.resume_service import ResumeService

                    resume_service = ResumeService()

                    resume = await resume_service.get_resume(db, resume_id, user_id)
                    if not resume:
                        results["errors"].append(f"Resume {resume_id} not found")
                        continue

                    pdf_result = await self.generate_pdf(resume)
                    results["success"].append(
                        {
                            "resume_id": resume_id,
                            "pdf_url": pdf_result["pdf_url"],
                            "file_size": pdf_result["file_size"],
                        }
                    )

                    await db.commit()

            except Exception as e:
                logger.error(f"Error generating PDF for resume {resume_id}: {str(e)}")
                results["errors"].append(f"Resume {resume_id}: {str(e)}")

        return results

    async def get_resume_as_html(
        self,
        resume: Resume,
        template_name: Optional[str] = None,
        custom_css: Optional[str] = None,
    ) -> str:
        """Get resume as HTML (for preview)."""
        return await self.template_service.render_resume(
            resume, template_name, custom_css
        )

    async def cleanup_old_pdfs(self, older_than_days: int = 30) -> int:
        """Clean up old generated PDFs to save storage space."""
        try:

            # This would query for resumes with old PDF files and clean them up
            # Implementation depends on your cleanup strategy

            cleanup_count = 0
            # ... cleanup logic here ...

            logger.info(f"Cleaned up {cleanup_count} old PDF files")
            return cleanup_count

        except Exception as e:
            logger.error(f"Error cleaning up old PDFs: {str(e)}")
            raise
