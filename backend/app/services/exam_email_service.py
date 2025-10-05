"""Email service for exam notifications."""
import logging
from datetime import datetime
from typing import Optional

from app.models.exam import Exam
from app.models.user import User
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class ExamEmailService:
    """Service for sending exam-related email notifications."""

    def __init__(self):
        self.email_service = email_service

    async def send_exam_assignment_notification(
        self,
        candidate: User,
        exam: Exam,
        assignment_id: int,
        due_date: Optional[datetime] = None,
        assigned_by: Optional[User] = None,
        exam_url: Optional[str] = None,
    ) -> bool:
        """
        Send exam assignment notification to candidate.

        Args:
            candidate: The candidate user
            exam: The exam being assigned
            assignment_id: Assignment ID
            due_date: Optional due date
            assigned_by: User who assigned the exam
            exam_url: URL to take the exam

        Returns:
            True if email sent successfully
        """
        try:
            subject = f"New Exam Assignment: {exam.title}"

            # Create HTML body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4F46E5; color: white; padding: 20px; border-radius: 5px; }}
                    .content {{ padding: 20px; background-color: #f9fafb; border-radius: 5px; margin-top: 20px; }}
                    .exam-details {{ background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .detail-row {{ padding: 8px 0; border-bottom: 1px solid #e5e7eb; }}
                    .detail-label {{ font-weight: bold; color: #6B7280; }}
                    .button {{
                        display: inline-block;
                        padding: 12px 30px;
                        background-color: #4F46E5;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{ text-align: center; color: #6B7280; margin-top: 30px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0;">New Exam Assignment</h1>
                    </div>

                    <div class="content">
                        <p>Dear {candidate.full_name},</p>

                        <p>You have been assigned a new exam to complete:</p>

                        <div class="exam-details">
                            <div class="detail-row">
                                <span class="detail-label">Exam:</span> {exam.title}
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Type:</span> {exam.exam_type}
                            </div>
                            {f'<div class="detail-row"><span class="detail-label">Due Date:</span> {due_date.strftime("%Y-%m-%d %H:%M")}</div>' if due_date else ''}
                            {f'<div class="detail-row"><span class="detail-label">Time Limit:</span> {exam.time_limit_minutes} minutes</div>' if exam.time_limit_minutes else ''}
                            <div class="detail-row">
                                <span class="detail-label">Max Attempts:</span> {exam.max_attempts}
                            </div>
                            {f'<div class="detail-row"><span class="detail-label">Passing Score:</span> {exam.passing_score}%</div>' if exam.passing_score else ''}
                        </div>

                        {f'<div style="background-color: #FEF3C7; padding: 15px; border-radius: 5px; margin: 15px 0;"><p style="margin: 0;"><strong>Instructions:</strong><br>{exam.instructions}</p></div>' if exam.instructions else ''}

                        <div style="text-align: center;">
                            <a href="{exam_url or '#'}" class="button">Start Exam</a>
                        </div>

                        {f'<p style="color: #6B7280; font-size: 14px;">Assigned by: {assigned_by.full_name}</p>' if assigned_by else ''}

                        <p>Good luck!</p>
                    </div>

                    <div class="footer">
                        <p>MiraiWorks Recruitment System</p>
                        <p>This is an automated message. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create text body
            newline = "\n"
            text_body = f"""
New Exam Assignment: {exam.title}

Dear {candidate.full_name},

You have been assigned a new exam to complete:

Exam: {exam.title}
Type: {exam.exam_type}
{f"Due Date: {due_date.strftime('%Y-%m-%d %H:%M')}" if due_date else "No due date"}
{f"Time Limit: {exam.time_limit_minutes} minutes" if exam.time_limit_minutes else "No time limit"}
Max Attempts: {exam.max_attempts}
{f"Passing Score: {exam.passing_score}%" if exam.passing_score else "No minimum score required"}

{f"Instructions:{newline}{exam.instructions}" if exam.instructions else ""}

{f"Exam Link: {exam_url}" if exam_url else ""}

{f"Assigned by: {assigned_by.full_name}" if assigned_by else ""}

Good luck!

---
MiraiWorks Recruitment System
            """

            success = await self.email_service.send_email(
                to_emails=[candidate.email],
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )

            if success:
                logger.info(
                    f"Exam assignment email sent to {candidate.email} for exam {exam.id}"
                )
            else:
                logger.error(
                    f"Failed to send exam assignment email to {candidate.email}"
                )

            return success

        except Exception as e:
            logger.error(f"Error sending exam assignment email: {e}")
            return False

    async def send_exam_reminder(
        self,
        candidate: User,
        exam: Exam,
        due_date: datetime,
        exam_url: Optional[str] = None,
    ) -> bool:
        """Send exam reminder notification."""
        try:
            days_remaining = (due_date - datetime.utcnow()).days
            hours_remaining = (due_date - datetime.utcnow()).seconds // 3600

            subject = f"Reminder: Exam Due Soon - {exam.title}"

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #F59E0B; color: white; padding: 20px; border-radius: 5px;">
                        <h1 style="margin: 0;">⏰ Exam Reminder</h1>
                    </div>

                    <div style="padding: 20px; background-color: #f9fafb; border-radius: 5px; margin-top: 20px;">
                        <p>Dear {candidate.full_name},</p>

                        <p style="color: #F59E0B; font-weight: bold;">This is a reminder that you have an exam due soon!</p>

                        <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <p><strong>Exam:</strong> {exam.title}</p>
                            <p><strong>Due Date:</strong> {due_date.strftime('%Y-%m-%d %H:%M')}</p>
                            <p><strong>Time Remaining:</strong> {days_remaining} days, {hours_remaining} hours</p>
                        </div>

                        <p>Please complete the exam before the due date to avoid missing the deadline.</p>

                        <div style="text-align: center; margin: 20px 0;">
                            <a href="{exam_url or '#'}" style="display: inline-block; padding: 12px 30px; background-color: #F59E0B; color: white; text-decoration: none; border-radius: 5px;">
                                Start Exam Now
                            </a>
                        </div>
                    </div>

                    <div style="text-align: center; color: #6B7280; margin-top: 30px; font-size: 12px;">
                        <p>MiraiWorks Recruitment System</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_body = f"""
Reminder: Exam Due Soon

Dear {candidate.full_name},

This is a reminder that you have an exam due soon!

Exam: {exam.title}
Due Date: {due_date.strftime('%Y-%m-%d %H:%M')}
Time Remaining: {days_remaining} days, {hours_remaining} hours

Please complete the exam before the due date.

{f"Exam Link: {exam_url}" if exam_url else ""}

Best regards,
MiraiWorks Recruitment System
            """

            return await self.email_service.send_email(
                to_emails=[candidate.email],
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )

        except Exception as e:
            logger.error(f"Error sending exam reminder email: {e}")
            return False

    async def send_exam_completion_notification(
        self,
        candidate: User,
        exam: Exam,
        session_id: int,
        score: Optional[float] = None,
        passed: Optional[bool] = None,
        results_url: Optional[str] = None,
    ) -> bool:
        """Send exam completion notification."""
        try:
            subject = f"Exam Completed: {exam.title}"

            result_section = ""
            if exam.show_score and score is not None:
                result_color = "#10B981" if passed else "#EF4444"
                result_text = "PASSED ✓" if passed else "NOT PASSED ✗"

                result_section = f"""
                <div style="background-color: {result_color}; color: white; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <h2 style="margin: 0 0 10px 0;">Your Score: {score:.1f}%</h2>
                    {f'<p style="margin: 0; font-size: 18px;">{result_text}</p>' if passed is not None else ''}
                </div>
                """

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #10B981; color: white; padding: 20px; border-radius: 5px;">
                        <h1 style="margin: 0;">✅ Exam Completed!</h1>
                    </div>

                    <div style="padding: 20px; background-color: #f9fafb; border-radius: 5px; margin-top: 20px;">
                        <p>Dear {candidate.full_name},</p>

                        <p>Congratulations! You have successfully completed the exam:</p>

                        <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <p><strong>Exam:</strong> {exam.title}</p>
                            <p><strong>Completion Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</p>
                        </div>

                        {result_section}

                        {f'<div style="text-align: center; margin: 20px 0;"><a href="{results_url}" style="display: inline-block; padding: 12px 30px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 5px;">View Detailed Results</a></div>' if exam.show_results_immediately and results_url else '<p>Results will be available soon.</p>'}

                        <p>Thank you for completing the exam!</p>
                    </div>

                    <div style="text-align: center; color: #6B7280; margin-top: 30px; font-size: 12px;">
                        <p>MiraiWorks Recruitment System</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_body = f"""
Exam Completed: {exam.title}

Dear {candidate.full_name},

Congratulations! You have successfully completed the exam.

Exam: {exam.title}
Completion Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}
{f"Your Score: {score:.1f}%" if exam.show_score and score is not None else ""}
{f"Result: {'PASSED' if passed else 'NOT PASSED'}" if passed is not None else ""}

{f"View Results: {results_url}" if exam.show_results_immediately and results_url else "Results will be available soon."}

Thank you for completing the exam!

Best regards,
MiraiWorks Recruitment System
            """

            return await self.email_service.send_email(
                to_emails=[candidate.email],
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )

        except Exception as e:
            logger.error(f"Error sending exam completion email: {e}")
            return False


# Singleton instance
exam_email_service = ExamEmailService()
