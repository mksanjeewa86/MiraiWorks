from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.models.video_call import VideoCall
from app.services.email_service import email_service


class VideoNotificationService:
    """Service for handling video call email notifications."""

    async def send_interview_scheduled_notification(
        self,
        db: AsyncSession,
        video_call: VideoCall,
        interviewer: User,
        candidate: User,
    ) -> None:
        """Send email notification when a video interview is scheduled."""

        # Email to candidate
        await self._send_candidate_scheduled_email(video_call, interviewer, candidate)

        # Email to interviewer
        await self._send_interviewer_scheduled_email(video_call, interviewer, candidate)

    async def send_interview_reminder_24h(
        self,
        db: AsyncSession,
        video_call: VideoCall,
        interviewer: User,
        candidate: User,
    ) -> None:
        """Send 24-hour reminder email for video interview."""

        # Email to candidate
        await self._send_candidate_reminder_email(
            video_call, interviewer, candidate, "24時間"
        )

        # Email to interviewer
        await self._send_interviewer_reminder_email(
            video_call, interviewer, candidate, "24時間"
        )

    async def send_interview_reminder_1h(
        self,
        db: AsyncSession,
        video_call: VideoCall,
        interviewer: User,
        candidate: User,
    ) -> None:
        """Send 1-hour reminder email for video interview."""

        # Email to candidate
        await self._send_candidate_reminder_email(
            video_call, interviewer, candidate, "1時間"
        )

        # Email to interviewer
        await self._send_interviewer_reminder_email(
            video_call, interviewer, candidate, "1時間"
        )

    async def send_interview_cancelled_notification(
        self,
        db: AsyncSession,
        video_call: VideoCall,
        interviewer: User,
        candidate: User,
        cancelled_by: User,
        reason: str | None = None,
    ) -> None:
        """Send email notification when a video interview is cancelled."""

        # Email to candidate (if not cancelled by candidate)
        if cancelled_by.id != candidate.id:
            await self._send_candidate_cancelled_email(
                video_call, interviewer, candidate, cancelled_by, reason
            )

        # Email to interviewer (if not cancelled by interviewer)
        if cancelled_by.id != interviewer.id:
            await self._send_interviewer_cancelled_email(
                video_call, interviewer, candidate, cancelled_by, reason
            )

    async def send_interview_rescheduled_notification(
        self,
        db: AsyncSession,
        video_call: VideoCall,
        interviewer: User,
        candidate: User,
        old_time: datetime,
        rescheduled_by: User,
    ) -> None:
        """Send email notification when a video interview is rescheduled."""

        # Email to candidate
        await self._send_candidate_rescheduled_email(
            video_call, interviewer, candidate, old_time, rescheduled_by
        )

        # Email to interviewer
        await self._send_interviewer_rescheduled_email(
            video_call, interviewer, candidate, old_time, rescheduled_by
        )

    async def send_technical_issue_notification(
        self,
        db: AsyncSession,
        video_call: VideoCall,
        user: User,
        issue_description: str,
    ) -> None:
        """Send notification about technical issues during video call."""

        subject = f"ビデオ面接での技術的問題 - {video_call.room_id}"

        # Get interview details
        join_url = f"{settings.app_base_url}/video-calls/{video_call.id}/join"

        template_data = {
            "user_name": user.full_name or user.email,
            "video_call": video_call,
            "issue_description": issue_description,
            "join_url": join_url,
            "support_email": "support@miraiworks.com",
            "scheduled_time": video_call.scheduled_at.strftime("%Y年%m月%d日 %H:%M"),
        }

        await email_service.send_template_email(
            to_email=user.email,
            subject=subject,
            template_name="video_call_technical_issue",
            template_data=template_data,
        )

    # Private helper methods

    async def _send_candidate_scheduled_email(
        self, video_call: VideoCall, interviewer: User, candidate: User
    ) -> None:
        """Send scheduled notification to candidate."""
        subject = f"ビデオ面接が予定されました - {video_call.scheduled_at.strftime('%m月%d日')}"

        join_url = f"{settings.app_base_url}/video-calls/{video_call.id}/join"

        template_data = {
            "candidate_name": candidate.full_name or candidate.email,
            "interviewer_name": interviewer.full_name or interviewer.email,
            "company_name": interviewer.company.name
            if interviewer.company
            else "未設定",
            "scheduled_time": video_call.scheduled_at.strftime("%Y年%m月%d日 %H:%M"),
            "join_url": join_url,
            "room_id": video_call.room_id,
            "transcription_enabled": video_call.transcription_enabled,
            "preparation_notes": "システムテストを事前に実行してください。",
        }

        await email_service.send_template_email(
            to_email=candidate.email,
            subject=subject,
            template_name="candidate_video_interview_scheduled",
            template_data=template_data,
        )

    async def _send_interviewer_scheduled_email(
        self, video_call: VideoCall, interviewer: User, candidate: User
    ) -> None:
        """Send scheduled notification to interviewer."""
        subject = f"ビデオ面接を予定しました - {candidate.full_name or candidate.email}"

        join_url = f"{settings.app_base_url}/video-calls/{video_call.id}/join"

        template_data = {
            "interviewer_name": interviewer.full_name or interviewer.email,
            "candidate_name": candidate.full_name or candidate.email,
            "candidate_email": candidate.email,
            "scheduled_time": video_call.scheduled_at.strftime("%Y年%m月%d日 %H:%M"),
            "join_url": join_url,
            "room_id": video_call.room_id,
            "transcription_enabled": video_call.transcription_enabled,
        }

        await email_service.send_template_email(
            to_email=interviewer.email,
            subject=subject,
            template_name="interviewer_video_interview_scheduled",
            template_data=template_data,
        )

    async def _send_candidate_reminder_email(
        self, video_call: VideoCall, interviewer: User, candidate: User, timeframe: str
    ) -> None:
        """Send reminder email to candidate."""
        subject = f"ビデオ面接リマインダー - {timeframe}後開始"

        join_url = f"{settings.app_base_url}/video-calls/{video_call.id}/join"

        template_data = {
            "candidate_name": candidate.full_name or candidate.email,
            "interviewer_name": interviewer.full_name or interviewer.email,
            "company_name": interviewer.company.name
            if interviewer.company
            else "未設定",
            "scheduled_time": video_call.scheduled_at.strftime("%Y年%m月%d日 %H:%M"),
            "timeframe": timeframe,
            "join_url": join_url,
            "checklist": [
                "インターネット接続を確認",
                "カメラとマイクをテスト",
                "静かな環境を準備",
                "必要な書類を手元に準備",
            ],
        }

        await email_service.send_template_email(
            to_email=candidate.email,
            subject=subject,
            template_name="candidate_video_interview_reminder",
            template_data=template_data,
        )

    async def _send_interviewer_reminder_email(
        self, video_call: VideoCall, interviewer: User, candidate: User, timeframe: str
    ) -> None:
        """Send reminder email to interviewer."""
        subject = f"ビデオ面接リマインダー - {candidate.full_name or candidate.email}"

        join_url = f"{settings.app_base_url}/video-calls/{video_call.id}/join"

        template_data = {
            "interviewer_name": interviewer.full_name or interviewer.email,
            "candidate_name": candidate.full_name or candidate.email,
            "scheduled_time": video_call.scheduled_at.strftime("%Y年%m月%d日 %H:%M"),
            "timeframe": timeframe,
            "join_url": join_url,
            "candidate_profile_url": f"{settings.app_base_url}/candidates/{candidate.id}",
        }

        await email_service.send_template_email(
            to_email=interviewer.email,
            subject=subject,
            template_name="interviewer_video_interview_reminder",
            template_data=template_data,
        )

    async def _send_candidate_cancelled_email(
        self,
        video_call: VideoCall,
        interviewer: User,
        candidate: User,
        cancelled_by: User,
        reason: str | None,
    ) -> None:
        """Send cancellation notification to candidate."""
        subject = f"ビデオ面接がキャンセルされました - {video_call.scheduled_at.strftime('%m月%d日')}"

        template_data = {
            "candidate_name": candidate.full_name or candidate.email,
            "interviewer_name": interviewer.full_name or interviewer.email,
            "company_name": interviewer.company.name
            if interviewer.company
            else "未設定",
            "scheduled_time": video_call.scheduled_at.strftime("%Y年%m月%d日 %H:%M"),
            "cancelled_by_name": cancelled_by.full_name or cancelled_by.email,
            "reason": reason or "理由は提供されていません",
            "contact_email": interviewer.email,
        }

        await email_service.send_template_email(
            to_email=candidate.email,
            subject=subject,
            template_name="candidate_video_interview_cancelled",
            template_data=template_data,
        )

    async def _send_interviewer_cancelled_email(
        self,
        video_call: VideoCall,
        interviewer: User,
        candidate: User,
        cancelled_by: User,
        reason: str | None,
    ) -> None:
        """Send cancellation notification to interviewer."""
        subject = f"ビデオ面接がキャンセルされました - {candidate.full_name or candidate.email}"

        template_data = {
            "interviewer_name": interviewer.full_name or interviewer.email,
            "candidate_name": candidate.full_name or candidate.email,
            "scheduled_time": video_call.scheduled_at.strftime("%Y年%m月%d日 %H:%M"),
            "cancelled_by_name": cancelled_by.full_name or cancelled_by.email,
            "reason": reason or "理由は提供されていません",
        }

        await email_service.send_template_email(
            to_email=interviewer.email,
            subject=subject,
            template_name="interviewer_video_interview_cancelled",
            template_data=template_data,
        )

    async def _send_candidate_rescheduled_email(
        self,
        video_call: VideoCall,
        interviewer: User,
        candidate: User,
        old_time: datetime,
        rescheduled_by: User,
    ) -> None:
        """Send rescheduled notification to candidate."""
        subject = "ビデオ面接が再スケジュールされました"

        join_url = f"{settings.app_base_url}/video-calls/{video_call.id}/join"

        template_data = {
            "candidate_name": candidate.full_name or candidate.email,
            "interviewer_name": interviewer.full_name or interviewer.email,
            "old_time": old_time.strftime("%Y年%m月%d日 %H:%M"),
            "new_time": video_call.scheduled_at.strftime("%Y年%m月%d日 %H:%M"),
            "rescheduled_by_name": rescheduled_by.full_name or rescheduled_by.email,
            "join_url": join_url,
        }

        await email_service.send_template_email(
            to_email=candidate.email,
            subject=subject,
            template_name="candidate_video_interview_rescheduled",
            template_data=template_data,
        )

    async def _send_interviewer_rescheduled_email(
        self,
        video_call: VideoCall,
        interviewer: User,
        candidate: User,
        old_time: datetime,
        rescheduled_by: User,
    ) -> None:
        """Send rescheduled notification to interviewer."""
        subject = f"ビデオ面接が再スケジュールされました - {candidate.full_name or candidate.email}"

        join_url = f"{settings.app_base_url}/video-calls/{video_call.id}/join"

        template_data = {
            "interviewer_name": interviewer.full_name or interviewer.email,
            "candidate_name": candidate.full_name or candidate.email,
            "old_time": old_time.strftime("%Y年%m月%d日 %H:%M"),
            "new_time": video_call.scheduled_at.strftime("%Y年%m月%d日 %H:%M"),
            "rescheduled_by_name": rescheduled_by.full_name or rescheduled_by.email,
            "join_url": join_url,
        }

        await email_service.send_template_email(
            to_email=interviewer.email,
            subject=subject,
            template_name="interviewer_video_interview_rescheduled",
            template_data=template_data,
        )


video_notification_service = VideoNotificationService()
