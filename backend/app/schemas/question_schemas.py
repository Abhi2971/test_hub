"""
Question schemas for ExamSaaS platform.
Marshmallow validators for question inputs.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class QuestionOptionSchema(Schema):
    """Schema for question option."""
    option_id = fields.String(required=False)
    text = fields.String(required=True, validate=validate.Length(min=1, max=1000))


class CreateQuestionSchema(Schema):
    """Schema for creating a question."""
    text = fields.String(required=True, validate=validate.Length(min=1, max=5000))
    question_type = fields.String(required=True, validate=validate.OneOf(["mcq", "true_false", "multiple_select"]))
    options = fields.List(fields.Nested(QuestionOptionSchema), required=True, validate=validate.Length(min=2, max=6))
    correct_option_id = fields.String(required=True)
    explanation = fields.String(required=False, allow_none=True, validate=validate.Length(max=2000))
    subject = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    topic = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    difficulty = fields.String(required=False, load_default="medium", validate=validate.OneOf(["easy", "medium", "hard"]))
    marks = fields.Integer(required=False, load_default=1, validate=validate.Range(min=1, max=100))
    source = fields.String(required=False, load_default="manual", validate=validate.OneOf(["manual", "pdf", "ai_generated"]))


class UpdateQuestionSchema(Schema):
    """Schema for updating a question."""
    text = fields.String(required=False, validate=validate.Length(min=1, max=5000))
    question_type = fields.String(required=False, validate=validate.OneOf(["mcq", "true_false", "multiple_select"]))
    options = fields.List(fields.Nested(QuestionOptionSchema), required=False)
    correct_option_id = fields.String(required=False)
    explanation = fields.String(required=False, allow_none=True, validate=validate.Length(max=2000))
    subject = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    topic = fields.String(required=False, allow_none=True, validate=validate.Length(max=100))
    difficulty = fields.String(required=False, validate=validate.OneOf(["easy", "medium", "hard"]))
    marks = fields.Integer(required=False, validate=validate.Range(min=1, max=100))


class BulkCreateQuestionSchema(Schema):
    """Schema for bulk creating questions."""
    questions = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1, max=100))


class QuestionListSchema(Schema):
    """Schema for listing questions with filters."""
    page = fields.Integer(required=False, load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(required=False, load_default=20, validate=validate.Range(min=1, max=100))
    institute_id = fields.String(required=False)
    subject = fields.String(required=False)
    topic = fields.String(required=False)
    difficulty = fields.String(required=False, validate=validate.OneOf(["easy", "medium", "hard"]))
    is_approved = fields.Boolean(required=False)
    is_reviewed = fields.Boolean(required=False)
    search = fields.String(required=False)
    question_type = fields.String(required=False, validate=validate.OneOf(["mcq", "true_false", "multiple_select"]))


class ReviewQuestionSchema(Schema):
    """Schema for reviewing a question."""
    action = fields.String(required=True, validate=validate.OneOf(["approve", "reject"]))


create_question_schema = CreateQuestionSchema()
update_question_schema = UpdateQuestionSchema()
bulk_create_question_schema = BulkCreateQuestionSchema()
question_list_schema = QuestionListSchema()
review_question_schema = ReviewQuestionSchema()
