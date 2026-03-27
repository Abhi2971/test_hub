"""
Exam schemas for ExamSaaS platform.
Marshmallow validators for exam inputs.
"""
import re
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load, post_load
from typing import Optional


class ScheduleSchema(Schema):
    """Schema for exam schedule."""
    start_at = fields.DateTime(required=False, allow_none=True)
    end_at = fields.DateTime(required=False, allow_none=True)
    grace_minutes = fields.Integer(required=False, load_default=5, validate=validate.Range(min=0, max=60))


class SecuritySchema(Schema):
    """Schema for exam security settings."""
    camera_required = fields.Boolean(required=False, load_default=False)
    tab_switch_limit = fields.Integer(required=False, load_default=3, validate=validate.Range(min=0, max=20))
    fullscreen_required = fields.Boolean(required=False, load_default=False)
    copy_paste_disabled = fields.Boolean(required=False, load_default=False)
    shuffle_questions = fields.Boolean(required=False, load_default=False)
    shuffle_options = fields.Boolean(required=False, load_default=False)


class CreateExamSchema(Schema):
    """Schema for creating an exam."""
    title = fields.String(required=True, validate=validate.Length(min=3, max=255))
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=2000))
    subject = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    topic = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    duration_minutes = fields.Integer(required=False, load_default=60, validate=validate.Range(min=1, max=600))
    total_marks = fields.Integer(required=False, load_default=0, validate=validate.Range(min=0))
    passing_percentage = fields.Float(required=False, load_default=40.0, validate=validate.Range(min=0, max=100))
    exam_type = fields.String(required=False, load_default="institute", validate=validate.OneOf(["institute", "public"]))
    result_mode = fields.String(required=False, load_default="instant", validate=validate.OneOf(["instant", "delayed"]))
    access_mode = fields.String(required=False, load_default="open", validate=validate.OneOf(["open", "passcode", "magic_link"]))
    price = fields.Integer(required=False, load_default=0, validate=validate.Range(min=0))
    allowed_attempts = fields.Integer(required=False, load_default=1, validate=validate.Range(min=1, max=10))
    certificate_enabled = fields.Boolean(required=False, load_default=False)
    schedule = fields.Nested(ScheduleSchema, required=False)
    security = fields.Nested(SecuritySchema, required=False)
    passcode = fields.String(required=False, allow_none=True, load_default=None)

    @validates("title")
    def validate_title(self, value):
        if not value or not value.strip():
            raise ValidationError("Title is required")


class UpdateExamSchema(Schema):
    """Schema for updating an exam."""
    title = fields.String(required=False, validate=validate.Length(min=3, max=255))
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=2000))
    subject = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    topic = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    duration_minutes = fields.Integer(required=False, validate=validate.Range(min=1, max=600))
    total_marks = fields.Integer(required=False, validate=validate.Range(min=0))
    passing_percentage = fields.Float(required=False, validate=validate.Range(min=0, max=100))
    result_mode = fields.String(required=False, validate=validate.OneOf(["instant", "delayed"]))
    access_mode = fields.String(required=False, validate=validate.OneOf(["open", "passcode", "magic_link"]))
    price = fields.Integer(required=False, validate=validate.Range(min=0))
    allowed_attempts = fields.Integer(required=False, validate=validate.Range(min=1, max=10))
    certificate_enabled = fields.Boolean(required=False)
    schedule = fields.Nested(ScheduleSchema, required=False)
    security = fields.Nested(SecuritySchema, required=False)
    passcode = fields.String(required=False, allow_none=True)


class StartExamSchema(Schema):
    """Schema for starting an exam attempt."""
    passcode = fields.String(required=False, allow_none=True, load_default=None)


class SaveAnswersSchema(Schema):
    """Schema for saving answers."""
    answers = fields.List(fields.Dict(), required=True)

    @validates("answers")
    def validate_answers(self, value):
        if not value:
            raise ValidationError("Answers are required")


class LogViolationSchema(Schema):
    """Schema for logging violations."""
    violation_type = fields.String(required=True, validate=validate.OneOf([
        "tab_switch", "face_mismatch", "fullscreen_exit", "copy_paste"
    ]))
    screenshot_url = fields.URL(required=False, allow_none=True)


class ForceSubmitSchema(Schema):
    """Schema for force submitting an attempt."""
    reason = fields.String(required=False, load_default="Admin forced submission")


class GenerateMagicLinkSchema(Schema):
    """Schema for generating magic links."""
    student_ids = fields.List(fields.String(), required=False)
    valid_hours = fields.Integer(required=False, load_default=24, validate=validate.Range(min=1, max=168))


class AssignQuestionsSchema(Schema):
    """Schema for assigning questions to exam."""
    question_ids = fields.List(fields.String(), required=True)
    marks_per_question = fields.Integer(required=False, allow_none=True)


class ExamListSchema(Schema):
    """Schema for listing exams with filters."""
    page = fields.Integer(required=False, load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(required=False, load_default=20, validate=validate.Range(min=1, max=100))
    status = fields.String(required=False, validate=validate.OneOf([
        "draft", "pending_approval", "published", "active", "closed", "archived"
    ]))
    institute_id = fields.String(required=False)
    search = fields.String(required=False)
    exam_type = fields.String(required=False, validate=validate.OneOf(["institute", "public"]))


class MagicLinkVerifySchema(Schema):
    """Schema for verifying magic link."""
    token = fields.String(required=True)


create_exam_schema = CreateExamSchema()
update_exam_schema = UpdateExamSchema()
start_exam_schema = StartExamSchema()
save_answers_schema = SaveAnswersSchema()
log_violation_schema = LogViolationSchema()
force_submit_schema = ForceSubmitSchema()
generate_magic_link_schema = GenerateMagicLinkSchema()
assign_questions_schema = AssignQuestionsSchema()
exam_list_schema = ExamListSchema()
magic_link_verify_schema = MagicLinkVerifySchema()
