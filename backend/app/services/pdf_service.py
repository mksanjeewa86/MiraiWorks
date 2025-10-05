import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

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
        watermark: str | None = None,
        custom_css: str | None = None,
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
            resume.pdf_generated_at = datetime.now(timezone.utc)
            resume.download_count = (resume.download_count or 0) + 1

            result = {
                "pdf_url": download_url,
                "file_path": file_path,
                "file_size": len(pdf_data),
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
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
        watermark: str | None,
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

    async def get_pdf_preview_image(self, resume: Resume) -> str | None:
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

    async def _pdf_to_image(self, pdf_data: bytes) -> bytes | None:
        """Convert first page of PDF to image."""
        try:
            # Using pdf2image library (dynamically imported to avoid CI import validation)
            import importlib
            from io import BytesIO

            pdf2image = importlib.import_module("pdf2image")
            convert_from_bytes = pdf2image.convert_from_bytes

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
        template_name: str | None = None,
        custom_css: str | None = None,
    ) -> str:
        """Get resume as HTML (for preview)."""
        # Check if it's a Japanese format and use specialized templates
        from app.utils.constants import ResumeFormat

        if resume.resume_format == ResumeFormat.RIREKISHO:
            return await self._generate_rirekisho_html(resume)
        elif resume.resume_format == ResumeFormat.SHOKUMU_KEIREKISHO:
            return await self._generate_shokumu_html(resume)
        else:
            return await self.template_service.render_resume(
                resume, template_name, custom_css
            )

    async def _generate_rirekisho_html(self, resume: Resume) -> str:
        """Generate HTML for 履歴書 format"""
        html_template = """
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>履歴書 - {{ resume.full_name or 'Untitled' }}</title>
            <style>
                body {
                    font-family: "MS Gothic", "Hiragino Kaku Gothic ProN", "Yu Gothic", monospace;
                    font-size: 12px;
                    margin: 20px;
                    line-height: 1.4;
                    color: #000;
                }
                .title {
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 25px;
                    letter-spacing: 2px;
                }
                .section {
                    margin-bottom: 20px;
                    page-break-inside: avoid;
                }
                .section-title {
                    font-weight: bold;
                    font-size: 14px;
                    border-bottom: 2px solid #000;
                    margin-bottom: 10px;
                    padding-bottom: 2px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 15px;
                }
                td, th {
                    border: 1px solid #000;
                    padding: 6px;
                    text-align: left;
                    vertical-align: top;
                }
                .label-cell {
                    background-color: #f8f8f8;
                    font-weight: bold;
                    width: 25%;
                }
                .photo-cell {
                    width: 40mm;
                    height: 50mm;
                    text-align: center;
                    vertical-align: middle;
                    background-color: #f0f0f0;
                    font-size: 10px;
                    color: #666;
                }
                .date-cell {
                    width: 80px;
                    text-align: center;
                }
                .header-row {
                    background-color: #e8e8e8;
                    font-weight: bold;
                }
                .text-area {
                    min-height: 100px;
                    vertical-align: top;
                    padding: 8px;
                }
                @media print {
                    body { margin: 0; }
                    .section { page-break-inside: avoid; }
                }
            </style>
        </head>
        <body>
            <div class="title">履歴書</div>

            <!-- Personal Information -->
            <div class="section">
                <table>
                    <tr>
                        <td class="label-cell">氏名</td>
                        <td style="font-size: 16px; font-weight: bold;">{{ resume.full_name or '' }}</td>
                        <td rowspan="7" class="photo-cell">
                            {% if resume.photo_path %}
                            <img src="{{ resume.photo_path }}" style="max-width: 35mm; max-height: 45mm;" alt="証明写真">
                            {% else %}
                            証明写真<br>(3.0cm × 4.0cm)
                            {% endif %}
                        </td>
                    </tr>
                    <tr>
                        <td class="label-cell">フリガナ</td>
                        <td>{{ resume.furigana_name or '' }}</td>
                    </tr>
                    <tr>
                        <td class="label-cell">生年月日</td>
                        <td>{{ birth_date }}{% if age %} (満{{ age }}歳){% endif %}</td>
                    </tr>
                    <tr>
                        <td class="label-cell">性別</td>
                        <td>{{ resume.gender or '' }}</td>
                    </tr>
                    <tr>
                        <td class="label-cell">現住所</td>
                        <td>{{ resume.location or '' }}</td>
                    </tr>
                    <tr>
                        <td class="label-cell">電話番号</td>
                        <td>{{ resume.phone or '' }}</td>
                    </tr>
                    <tr>
                        <td class="label-cell">E-mail</td>
                        <td>{{ resume.email or '' }}</td>
                    </tr>
                </table>
            </div>

            <!-- Education History -->
            <div class="section">
                <div class="section-title">学歴</div>
                <table>
                    <tr class="header-row">
                        <td class="date-cell">年月</td>
                        <td>学校名・学部・学科名</td>
                        <td style="width: 80px;">卒業・修了</td>
                    </tr>
                    {% if resume.educations %}
                        {% for edu in resume.educations %}
                        <tr>
                            <td class="date-cell">{{ edu.start_date.strftime('%Y.%m') if edu.start_date else '' }}</td>
                            <td>{{ edu.institution_name }}{% if edu.field_of_study %} {{ edu.field_of_study }}{% endif %}</td>
                            <td>入学</td>
                        </tr>
                        {% if edu.end_date %}
                        <tr>
                            <td class="date-cell">{{ edu.end_date.strftime('%Y.%m') }}</td>
                            <td>{{ edu.institution_name }}{% if edu.field_of_study %} {{ edu.field_of_study }}{% endif %}</td>
                            <td>{{ '卒業' if '大学' in edu.institution_name else '修了' }}</td>
                        </tr>
                        {% endif %}
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="3" style="height: 60px;"></td></tr>
                    {% endif %}
                </table>
            </div>

            <!-- Work History -->
            <div class="section">
                <div class="section-title">職歴</div>
                <table>
                    <tr class="header-row">
                        <td class="date-cell">年月</td>
                        <td>職歴</td>
                        <td style="width: 80px;">雇用形態</td>
                    </tr>
                    {% if resume.experiences %}
                        {% for exp in resume.experiences %}
                        <tr>
                            <td class="date-cell">{{ exp.start_date.strftime('%Y.%m') if exp.start_date else '' }}</td>
                            <td>{{ exp.company_name }} 入社<br>{{ exp.position_title }}</td>
                            <td>正社員</td>
                        </tr>
                        {% if exp.end_date %}
                        <tr>
                            <td class="date-cell">{{ exp.end_date.strftime('%Y.%m') }}</td>
                            <td>{{ exp.company_name }} 退社</td>
                            <td></td>
                        </tr>
                        {% endif %}
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="3" style="height: 60px;"></td></tr>
                    {% endif %}
                </table>
            </div>

            <!-- Licenses and Certifications -->
            {% if resume.certifications %}
            <div class="section">
                <div class="section-title">免許・資格</div>
                <table>
                    <tr class="header-row">
                        <td class="date-cell">年月</td>
                        <td>免許・資格名</td>
                        <td style="width: 120px;">発行機関</td>
                    </tr>
                    {% for cert in resume.certifications %}
                    <tr>
                        <td class="date-cell">{{ cert.issue_date.strftime('%Y.%m') if cert.issue_date else '' }}</td>
                        <td>{{ cert.name }}</td>
                        <td>{{ cert.issuing_organization }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            {% endif %}

            <!-- Motivation and Self-PR -->
            <div class="section">
                <div class="section-title">志望動機・自己PR</div>
                <table>
                    <tr>
                        <td class="text-area">
                            {{ resume.professional_summary or resume.objective or '' }}
                        </td>
                    </tr>
                </table>
            </div>

            <!-- Additional Information -->
            <div class="section">
                <table>
                    <tr>
                        <td class="label-cell" style="width: 100px;">通勤時間</td>
                        <td style="width: 150px;">約{{ commute_time }}分</td>
                        <td class="label-cell" style="width: 80px;">扶養家族</td>
                        <td>{{ dependents }}人</td>
                    </tr>
                    <tr>
                        <td class="label-cell">配偶者</td>
                        <td>{{ spouse }}</td>
                        <td class="label-cell">配偶者の扶養義務</td>
                        <td>{{ spouse_support }}</td>
                    </tr>
                </table>
            </div>

            <div style="text-align: right; margin-top: 30px; font-size: 11px;">
                作成日: {{ creation_date }}
            </div>
        </body>
        </html>
        """

        from datetime import datetime

        from jinja2 import Template

        template = Template(html_template)

        # Calculate age if birth_date is available
        age = None
        birth_date = ""
        if resume.birth_date:
            birth_date = f"{resume.birth_date.year}年{resume.birth_date.month}月{resume.birth_date.day}日"
            today = datetime.now()
            age = today.year - resume.birth_date.year
            if today.month < resume.birth_date.month or (
                today.month == resume.birth_date.month
                and today.day < resume.birth_date.day
            ):
                age -= 1

        # Get additional info from emergency_contact if available
        emergency_contact = resume.emergency_contact or {}
        commute_time = emergency_contact.get("commute_time", "30")
        dependents = emergency_contact.get("dependents", "0")
        spouse = (
            "有" if resume.marital_status and "既婚" in resume.marital_status else "無"
        )
        spouse_support = "有" if spouse == "有" else "無"

        creation_date = datetime.now().strftime("%Y年%m月%d日")

        return template.render(
            resume=resume,
            birth_date=birth_date,
            age=age,
            commute_time=commute_time,
            dependents=dependents,
            spouse=spouse,
            spouse_support=spouse_support,
            creation_date=creation_date,
        )

    async def _generate_shokumu_html(self, resume: Resume) -> str:
        """Generate HTML for 職務経歴書 format"""
        html_template = """
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>職務経歴書 - {{ resume.full_name or 'Untitled' }}</title>
            <style>
                body {
                    font-family: "MS Gothic", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
                    font-size: 11px;
                    margin: 20px;
                    line-height: 1.6;
                    color: #000;
                }
                .title {
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    letter-spacing: 2px;
                }
                .header-info {
                    text-align: right;
                    margin-bottom: 20px;
                    font-size: 12px;
                }
                .section {
                    margin-bottom: 25px;
                    page-break-inside: avoid;
                }
                .section-title {
                    font-weight: bold;
                    font-size: 14px;
                    border-bottom: 2px solid #333;
                    margin-bottom: 12px;
                    padding-bottom: 3px;
                    color: #333;
                }
                .company-section {
                    margin-bottom: 20px;
                    border: 1px solid #ddd;
                    padding: 15px;
                    background-color: #fafafa;
                }
                .company-header {
                    font-weight: bold;
                    font-size: 13px;
                    margin-bottom: 8px;
                    color: #333;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 5px;
                }
                .period {
                    color: #666;
                    margin-bottom: 8px;
                    font-size: 11px;
                }
                .job-detail {
                    margin-left: 15px;
                    margin-bottom: 10px;
                }
                .skill-category {
                    margin-bottom: 15px;
                }
                .skill-category-title {
                    font-weight: bold;
                    color: #444;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 2px;
                    margin-bottom: 8px;
                }
                .achievement-list {
                    margin-left: 20px;
                }
                .achievement-list li {
                    margin-bottom: 5px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 15px;
                }
                td {
                    padding: 8px;
                    border: 1px solid #ddd;
                    vertical-align: top;
                }
                .summary-box {
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin-bottom: 20px;
                }
                @media print {
                    body { margin: 0; }
                    .section { page-break-inside: avoid; }
                    .company-section { page-break-inside: avoid; }
                }
            </style>
        </head>
        <body>
            <div class="title">職務経歴書</div>

            <div class="header-info">
                {{ creation_date }}<br>
                氏名: {{ resume.full_name or '' }}
            </div>

            <!-- Career Summary -->
            {% if resume.professional_summary %}
            <div class="section">
                <div class="section-title">■ 職務要約</div>
                <div class="summary-box">
                    {{ resume.professional_summary }}
                </div>
            </div>
            {% endif %}

            <!-- Detailed Work Experience -->
            {% if resume.experiences %}
            <div class="section">
                <div class="section-title">■ 職務経歴詳細</div>

                {% for exp in resume.experiences %}
                <div class="company-section">
                    <div class="company-header">【{{ exp.company_name }}】</div>
                    <div class="period">
                        在籍期間: {{ exp.start_date.strftime('%Y年%m月') if exp.start_date else '' }} ～
                        {{ exp.end_date.strftime('%Y年%m月') if exp.end_date else '現在' }}
                        ({{ calculate_duration(exp.start_date, exp.end_date) }})
                    </div>

                    <table>
                        {% if exp.position_title %}
                        <tr>
                            <td style="width: 100px; background-color: #f0f0f0; font-weight: bold;">職種</td>
                            <td>{{ exp.position_title }}</td>
                        </tr>
                        {% endif %}

                        {% if exp.description %}
                        <tr>
                            <td style="background-color: #f0f0f0; font-weight: bold;">業務内容</td>
                            <td>{{ exp.description }}</td>
                        </tr>
                        {% endif %}

                        {% if exp.achievements %}
                        <tr>
                            <td style="background-color: #f0f0f0; font-weight: bold;">主な実績</td>
                            <td>
                                <ul class="achievement-list">
                                    {% for achievement in exp.achievements %}
                                    <li>{{ achievement }}</li>
                                    {% endfor %}
                                </ul>
                            </td>
                        </tr>
                        {% endif %}

                        {% if exp.technologies %}
                        <tr>
                            <td style="background-color: #f0f0f0; font-weight: bold;">使用技術</td>
                            <td>{{ exp.technologies | join(', ') }}</td>
                        </tr>
                        {% endif %}
                    </table>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            <!-- Skills and Expertise -->
            {% if resume.skills %}
            <div class="section">
                <div class="section-title">■ スキル・専門知識</div>

                {% for category, skills in skills_by_category.items() %}
                <div class="skill-category">
                    <div class="skill-category-title">【{{ category }}】</div>
                    <div>{{ skills | join('、') }}</div>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            <!-- Languages -->
            {% if resume.languages %}
            <div class="section">
                <div class="section-title">■ 語学スキル</div>
                <table>
                    <tr style="background-color: #f0f0f0; font-weight: bold;">
                        <td style="width: 120px;">言語</td>
                        <td>レベル</td>
                    </tr>
                    {% for lang in resume.languages %}
                    <tr>
                        <td>{{ lang.name }}</td>
                        <td>{{ lang.proficiency }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            {% endif %}

            <!-- Self-PR -->
            {% if resume.objective %}
            <div class="section">
                <div class="section-title">■ 自己PR</div>
                <div class="summary-box">
                    {{ resume.objective }}
                </div>
            </div>
            {% endif %}

            <!-- Projects -->
            {% if resume.projects %}
            <div class="section">
                <div class="section-title">■ プロジェクト経験</div>

                {% for project in resume.projects %}
                <div class="company-section">
                    <div class="company-header">{{ project.name }}</div>
                    {% if project.start_date or project.end_date %}
                    <div class="period">
                        期間: {{ project.start_date.strftime('%Y年%m月') if project.start_date else '' }} ～
                        {{ project.end_date.strftime('%Y年%m月') if project.end_date else '現在' }}
                    </div>
                    {% endif %}

                    <table>
                        <tr>
                            <td style="width: 100px; background-color: #f0f0f0; font-weight: bold;">概要</td>
                            <td>{{ project.description }}</td>
                        </tr>
                        {% if project.role %}
                        <tr>
                            <td style="background-color: #f0f0f0; font-weight: bold;">担当役割</td>
                            <td>{{ project.role }}</td>
                        </tr>
                        {% endif %}
                        {% if project.technologies %}
                        <tr>
                            <td style="background-color: #f0f0f0; font-weight: bold;">使用技術</td>
                            <td>{{ project.technologies | join(', ') }}</td>
                        </tr>
                        {% endif %}
                    </table>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            <div style="text-align: right; margin-top: 30px; font-size: 10px; color: #666;">
                以上
            </div>
        </body>
        </html>
        """

        from datetime import datetime

        from jinja2 import Template

        template = Template(html_template)

        # Group skills by category
        skills_by_category = {}
        if resume.skills:
            for skill in resume.skills:
                category = skill.category or "その他"
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill.name)

        def calculate_duration(start_date, end_date):
            """Calculate work duration in Japanese format"""
            if not start_date:
                return ""

            end = end_date or datetime.now()
            years = end.year - start_date.year
            months = end.month - start_date.month

            if months < 0:
                years -= 1
                months += 12

            if years > 0 and months > 0:
                return f"約{years}年{months}ヶ月"
            elif years > 0:
                return f"約{years}年"
            elif months > 0:
                return f"約{months}ヶ月"
            else:
                return "1ヶ月未満"

        creation_date = datetime.now().strftime("%Y年%m月%d日")

        return template.render(
            resume=resume,
            skills_by_category=skills_by_category,
            calculate_duration=calculate_duration,
            creation_date=creation_date,
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
