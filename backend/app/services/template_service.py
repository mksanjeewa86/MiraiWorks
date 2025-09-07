import logging
from typing import Any, Optional

from jinja2 import BaseLoader, Environment, Template

from app.models.resume import Resume

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for managing resume templates and rendering."""

    def __init__(self):
        self.jinja_env = Environment(loader=BaseLoader())
        self.default_templates = self._load_default_templates()

    def _load_default_templates(self) -> dict[str, dict[str, Any]]:
        """Load default resume templates."""
        return {
            "modern": {
                "name": "modern",
                "display_name": "Modern Professional",
                "description": "A clean, modern template perfect for tech professionals",
                "category": "Modern",
                "html_template": self._get_modern_template(),
                "css_styles": self._get_modern_styles(),
                "template_data": {
                    "sections": [
                        "summary",
                        "experience",
                        "education",
                        "skills",
                        "projects",
                    ],
                    "layout": "single-column",
                    "accent_color": "#2563eb",
                },
                "color_scheme": {
                    "blue": "#2563eb",
                    "green": "#059669",
                    "purple": "#7c3aed",
                    "orange": "#ea580c",
                },
                "font_options": {
                    "Inter": "Inter, sans-serif",
                    "Roboto": "Roboto, sans-serif",
                    "Open Sans": "Open Sans, sans-serif",
                },
            },
            "classic": {
                "name": "classic",
                "display_name": "Classic Professional",
                "description": "Traditional resume format suitable for all industries",
                "category": "Classic",
                "html_template": self._get_classic_template(),
                "css_styles": self._get_classic_styles(),
                "template_data": {
                    "sections": ["summary", "experience", "education", "skills"],
                    "layout": "single-column",
                    "accent_color": "#374151",
                },
                "color_scheme": {
                    "black": "#374151",
                    "navy": "#1e40af",
                    "dark-green": "#065f46",
                },
                "font_options": {
                    "Times New Roman": "Times New Roman, serif",
                    "Georgia": "Georgia, serif",
                    "Crimson Text": "Crimson Text, serif",
                },
            },
            "creative": {
                "name": "creative",
                "display_name": "Creative Designer",
                "description": "Eye-catching template for creative professionals",
                "category": "Creative",
                "html_template": self._get_creative_template(),
                "css_styles": self._get_creative_styles(),
                "template_data": {
                    "sections": [
                        "summary",
                        "experience",
                        "skills",
                        "projects",
                        "education",
                    ],
                    "layout": "two-column",
                    "accent_color": "#ec4899",
                },
                "color_scheme": {
                    "pink": "#ec4899",
                    "teal": "#0d9488",
                    "orange": "#f59e0b",
                    "indigo": "#6366f1",
                },
                "font_options": {
                    "Montserrat": "Montserrat, sans-serif",
                    "Poppins": "Poppins, sans-serif",
                    "Nunito": "Nunito, sans-serif",
                },
            },
            "minimal": {
                "name": "minimal",
                "display_name": "Minimal Clean",
                "description": "Ultra-clean, minimal design for maximum readability",
                "category": "Minimal",
                "html_template": self._get_minimal_template(),
                "css_styles": self._get_minimal_styles(),
                "template_data": {
                    "sections": ["summary", "experience", "education", "skills"],
                    "layout": "single-column",
                    "accent_color": "#000000",
                },
                "color_scheme": {
                    "black": "#000000",
                    "gray": "#6b7280",
                    "blue": "#3b82f6",
                },
                "font_options": {
                    "Helvetica": "Helvetica, Arial, sans-serif",
                    "Source Sans Pro": "Source Sans Pro, sans-serif",
                    "Lato": "Lato, sans-serif",
                },
            },
        }

    async def render_resume(
        self,
        resume: Resume,
        template_name: Optional[str] = None,
        custom_css: Optional[str] = None,
    ) -> str:
        """Render a resume to HTML using the specified template."""
        try:
            template_name = template_name or resume.template_id or "modern"
            template_config = self.default_templates.get(template_name)

            if not template_config:
                logger.warning(f"Template {template_name} not found, using modern")
                template_config = self.default_templates["modern"]

            # Prepare resume data for template
            resume_data = self._prepare_resume_data(resume)

            # Render HTML
            template = Template(template_config["html_template"])
            html_content = template.render(
                resume=resume_data,
                template_config=template_config,
                theme_color=resume.theme_color
                or template_config["template_data"]["accent_color"],
                font_family=resume.font_family
                or list(template_config["font_options"].values())[0],
            )

            # Combine CSS
            css_styles = self._combine_css(
                template_config["css_styles"],
                resume.custom_css,
                custom_css,
                resume.theme_color or template_config["template_data"]["accent_color"],
                resume.font_family or list(template_config["font_options"].values())[0],
            )

            # Wrap in full HTML document
            full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{resume.full_name or 'Resume'} - {resume.title}</title>
    <style>
        {css_styles}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
            """

            return full_html.strip()

        except Exception as e:
            logger.error(f"Error rendering resume: {str(e)}")
            raise

    def _prepare_resume_data(self, resume: Resume) -> dict[str, Any]:
        """Prepare resume data for template rendering."""
        return {
            "id": resume.id,
            "title": resume.title,
            "full_name": resume.full_name,
            "email": resume.email,
            "phone": resume.phone,
            "location": resume.location,
            "website": resume.website,
            "linkedin_url": resume.linkedin_url,
            "github_url": resume.github_url,
            "professional_summary": resume.professional_summary,
            "objective": resume.objective,
            "experiences": [
                {
                    "id": exp.id,
                    "company_name": exp.company_name,
                    "position_title": exp.position_title,
                    "location": exp.location,
                    "company_website": exp.company_website,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "is_current": exp.is_current,
                    "description": exp.description,
                    "achievements": exp.achievements or [],
                    "technologies": exp.technologies or [],
                }
                for exp in sorted(
                    resume.experiences,
                    key=lambda x: (x.display_order, -x.start_date.timestamp()),
                )
                if exp.is_visible
            ],
            "educations": [
                {
                    "id": edu.id,
                    "institution_name": edu.institution_name,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                    "location": edu.location,
                    "start_date": edu.start_date,
                    "end_date": edu.end_date,
                    "is_current": edu.is_current,
                    "gpa": edu.gpa,
                    "honors": edu.honors,
                    "description": edu.description,
                    "courses": edu.courses or [],
                }
                for edu in sorted(
                    resume.educations,
                    key=lambda x: (x.display_order, -x.start_date.timestamp()),
                )
                if edu.is_visible
            ],
            "skills": [
                {
                    "id": skill.id,
                    "name": skill.name,
                    "category": skill.category,
                    "proficiency_level": skill.proficiency_level,
                    "proficiency_label": skill.proficiency_label,
                }
                for skill in sorted(resume.skills, key=lambda x: x.display_order)
                if skill.is_visible
            ],
            "projects": [
                {
                    "id": proj.id,
                    "name": proj.name,
                    "description": proj.description,
                    "project_url": proj.project_url,
                    "github_url": proj.github_url,
                    "demo_url": proj.demo_url,
                    "start_date": proj.start_date,
                    "end_date": proj.end_date,
                    "is_ongoing": proj.is_ongoing,
                    "technologies": proj.technologies or [],
                    "role": proj.role,
                }
                for proj in sorted(resume.projects, key=lambda x: x.display_order)
                if proj.is_visible
            ],
            "certifications": [
                {
                    "id": cert.id,
                    "name": cert.name,
                    "issuing_organization": cert.issuing_organization,
                    "credential_id": cert.credential_id,
                    "credential_url": cert.credential_url,
                    "issue_date": cert.issue_date,
                    "expiration_date": cert.expiration_date,
                    "does_not_expire": cert.does_not_expire,
                    "description": cert.description,
                }
                for cert in sorted(
                    resume.certifications,
                    key=lambda x: (x.display_order, -x.issue_date.timestamp()),
                )
                if cert.is_visible
            ],
            "languages": [
                {"id": lang.id, "name": lang.name, "proficiency": lang.proficiency}
                for lang in sorted(resume.languages, key=lambda x: x.display_order)
                if lang.is_visible
            ],
            "references": [
                {
                    "id": ref.id,
                    "full_name": ref.full_name,
                    "position_title": ref.position_title,
                    "company_name": ref.company_name,
                    "email": ref.email,
                    "phone": ref.phone,
                    "relationship": ref.relationship,
                }
                for ref in sorted(resume.references, key=lambda x: x.display_order)
                if ref.is_visible
            ],
            "sections": [
                {
                    "id": section.id,
                    "section_type": section.section_type,
                    "title": section.title,
                    "content": section.content,
                }
                for section in sorted(resume.sections, key=lambda x: x.display_order)
                if section.is_visible
            ],
        }

    def _combine_css(
        self,
        template_css: str,
        resume_css: Optional[str],
        custom_css: Optional[str],
        theme_color: str,
        font_family: str,
    ) -> str:
        """Combine and customize CSS styles."""
        # Replace template variables
        css = template_css.replace("{{theme_color}}", theme_color)
        css = css.replace("{{font_family}}", font_family)

        # Add resume-specific CSS
        if resume_css:
            css += f"\n/* Resume-specific styles */\n{resume_css}"

        # Add custom CSS
        if custom_css:
            css += f"\n/* Custom styles */\n{custom_css}"

        return css

    def get_available_templates(self) -> list[dict[str, Any]]:
        """Get list of available templates."""
        return [
            {
                "name": template["name"],
                "display_name": template["display_name"],
                "description": template["description"],
                "category": template["category"],
                "color_scheme": template["color_scheme"],
                "font_options": template["font_options"],
                "is_premium": False,
            }
            for template in self.default_templates.values()
        ]

    def _get_modern_template(self) -> str:
        """Get the modern template HTML."""
        return """
        <div class="resume-container modern-template">
            <header class="resume-header">
                <div class="header-content">
                    <h1 class="name">{{ resume.full_name or 'Your Name' }}</h1>
                    <h2 class="title">{{ resume.title or 'Professional Title' }}</h2>
                </div>
                <div class="contact-info">
                    {% if resume.email %}<div class="contact-item">📧 {{ resume.email }}</div>{% endif %}
                    {% if resume.phone %}<div class="contact-item">📱 {{ resume.phone }}</div>{% endif %}
                    {% if resume.location %}<div class="contact-item">📍 {{ resume.location }}</div>{% endif %}
                    {% if resume.website %}<div class="contact-item">🌐 <a href="{{ resume.website }}">{{ resume.website }}</a></div>{% endif %}
                    {% if resume.linkedin_url %}<div class="contact-item">💼 <a href="{{ resume.linkedin_url }}">LinkedIn</a></div>{% endif %}
                    {% if resume.github_url %}<div class="contact-item">💻 <a href="{{ resume.github_url }}">GitHub</a></div>{% endif %}
                </div>
            </header>

            {% if resume.professional_summary %}
            <section class="resume-section summary">
                <h3 class="section-title">Professional Summary</h3>
                <div class="section-content">
                    <p>{{ resume.professional_summary }}</p>
                </div>
            </section>
            {% endif %}

            {% if resume.experiences %}
            <section class="resume-section experience">
                <h3 class="section-title">Professional Experience</h3>
                <div class="section-content">
                    {% for exp in resume.experiences %}
                    <div class="experience-item">
                        <div class="exp-header">
                            <div class="exp-title">
                                <h4>{{ exp.position_title }}</h4>
                                <h5>{{ exp.company_name }}</h5>
                            </div>
                            <div class="exp-meta">
                                <span class="exp-date">
                                    {{ exp.start_date.strftime('%m/%Y') }} -
                                    {% if exp.is_current %}Present{% else %}{{ exp.end_date.strftime('%m/%Y') if exp.end_date }}{% endif %}
                                </span>
                                {% if exp.location %}<span class="exp-location">{{ exp.location }}</span>{% endif %}
                            </div>
                        </div>
                        {% if exp.description %}
                        <div class="exp-description">
                            <p>{{ exp.description }}</p>
                        </div>
                        {% endif %}
                        {% if exp.achievements %}
                        <ul class="exp-achievements">
                            {% for achievement in exp.achievements %}
                            <li>{{ achievement }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                        {% if exp.technologies %}
                        <div class="exp-technologies">
                            <strong>Technologies:</strong>
                            {% for tech in exp.technologies %}
                            <span class="tech-tag">{{ tech }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endif %}

            {% if resume.educations %}
            <section class="resume-section education">
                <h3 class="section-title">Education</h3>
                <div class="section-content">
                    {% for edu in resume.educations %}
                    <div class="education-item">
                        <div class="edu-header">
                            <div class="edu-title">
                                <h4>{{ edu.degree }}</h4>
                                <h5>{{ edu.institution_name }}</h5>
                            </div>
                            <div class="edu-meta">
                                <span class="edu-date">
                                    {{ edu.start_date.strftime('%m/%Y') }} -
                                    {% if edu.is_current %}Present{% else %}{{ edu.end_date.strftime('%m/%Y') if edu.end_date }}{% endif %}
                                </span>
                                {% if edu.location %}<span class="edu-location">{{ edu.location }}</span>{% endif %}
                            </div>
                        </div>
                        {% if edu.field_of_study %}<p class="edu-field">{{ edu.field_of_study }}</p>{% endif %}
                        {% if edu.gpa %}<p class="edu-gpa">GPA: {{ edu.gpa }}</p>{% endif %}
                        {% if edu.honors %}<p class="edu-honors">{{ edu.honors }}</p>{% endif %}
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endif %}

            {% if resume.skills %}
            <section class="resume-section skills">
                <h3 class="section-title">Skills</h3>
                <div class="section-content">
                    {% set skills_by_category = resume.skills | groupby('category') %}
                    {% for category, skills in skills_by_category %}
                    <div class="skill-category">
                        {% if category %}<h4 class="skill-category-title">{{ category }}</h4>{% endif %}
                        <div class="skill-list">
                            {% for skill in skills %}
                            <span class="skill-item">{{ skill.name }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endif %}

            {% if resume.projects %}
            <section class="resume-section projects">
                <h3 class="section-title">Projects</h3>
                <div class="section-content">
                    {% for project in resume.projects %}
                    <div class="project-item">
                        <div class="project-header">
                            <h4>{{ project.name }}</h4>
                            <div class="project-links">
                                {% if project.project_url %}<a href="{{ project.project_url }}">Live</a>{% endif %}
                                {% if project.github_url %}<a href="{{ project.github_url }}">GitHub</a>{% endif %}
                                {% if project.demo_url %}<a href="{{ project.demo_url }}">Demo</a>{% endif %}
                            </div>
                        </div>
                        <p class="project-description">{{ project.description }}</p>
                        {% if project.technologies %}
                        <div class="project-technologies">
                            {% for tech in project.technologies %}
                            <span class="tech-tag">{{ tech }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endif %}
        </div>
        """

    def _get_modern_styles(self) -> str:
        """Get the modern template CSS."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: {{font_family}};
            line-height: 1.6;
            color: #333;
            background: #fff;
        }

        .resume-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            background: white;
        }

        .resume-header {
            border-bottom: 3px solid {{theme_color}};
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        .name {
            font-size: 2.5rem;
            font-weight: 700;
            color: {{theme_color}};
            margin-bottom: 5px;
        }

        .title {
            font-size: 1.2rem;
            color: #666;
            font-weight: 400;
            margin-bottom: 15px;
        }

        .contact-info {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }

        .contact-item {
            font-size: 0.9rem;
            color: #555;
        }

        .contact-item a {
            color: {{theme_color}};
            text-decoration: none;
        }

        .resume-section {
            margin-bottom: 30px;
        }

        .section-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: {{theme_color}};
            border-bottom: 2px solid #e5e5e5;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }

        .experience-item, .education-item, .project-item {
            margin-bottom: 25px;
        }

        .exp-header, .edu-header, .project-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }

        .exp-title h4, .edu-title h4, .project-header h4 {
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
        }

        .exp-title h5, .edu-title h5 {
            font-size: 1rem;
            font-weight: 500;
            color: {{theme_color}};
        }

        .exp-date, .edu-date {
            font-weight: 500;
            color: #666;
            font-size: 0.9rem;
        }

        .exp-location, .edu-location {
            font-size: 0.9rem;
            color: #666;
            display: block;
        }

        .exp-achievements {
            list-style: none;
            padding-left: 0;
            margin: 10px 0;
        }

        .exp-achievements li {
            position: relative;
            padding-left: 20px;
            margin-bottom: 5px;
        }

        .exp-achievements li:before {
            content: "▸";
            position: absolute;
            left: 0;
            color: {{theme_color}};
            font-weight: bold;
        }

        .tech-tag {
            display: inline-block;
            background: #f3f4f6;
            color: #374151;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            margin-right: 8px;
            margin-bottom: 4px;
        }

        .skill-category {
            margin-bottom: 15px;
        }

        .skill-category-title {
            font-size: 1rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }

        .skill-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .skill-item {
            background: {{theme_color}};
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 500;
        }

        .project-links {
            display: flex;
            gap: 10px;
        }

        .project-links a {
            color: {{theme_color}};
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .project-links a:hover {
            text-decoration: underline;
        }

        @media print {
            .resume-container {
                padding: 20px;
                max-width: none;
            }

            .contact-item a {
                color: inherit;
            }
        }
        """

    def _get_classic_template(self) -> str:
        """Get classic template HTML - simplified for brevity."""
        return """
        <div class="resume-container classic-template">
            <header class="resume-header">
                <h1 class="name">{{ resume.full_name or 'Your Name' }}</h1>
                <div class="contact-info">
                    {% if resume.email %}{{ resume.email }}{% endif %}
                    {% if resume.phone %} • {{ resume.phone }}{% endif %}
                    {% if resume.location %} • {{ resume.location }}{% endif %}
                </div>
            </header>
            <!-- Similar structure but different styling -->
        </div>
        """

    def _get_classic_styles(self) -> str:
        """Get classic template CSS - simplified for brevity."""
        return """
        .classic-template .name {
            text-align: center;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .classic-template .contact-info {
            text-align: center;
            margin-bottom: 20px;
        }

        /* Additional classic styles... */
        """

    # Similar methods for creative and minimal templates...
    def _get_creative_template(self) -> str:
        return "<div>Creative template HTML...</div>"

    def _get_creative_styles(self) -> str:
        return "/* Creative template CSS... */"

    def _get_minimal_template(self) -> str:
        return "<div>Minimal template HTML...</div>"

    def _get_minimal_styles(self) -> str:
        return "/* Minimal template CSS... */"
