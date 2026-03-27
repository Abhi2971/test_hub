"""
Marshmallow schemas for plan operations.
"""
from marshmallow import Schema, fields, validate


class FeatureFlagsSchema(Schema):
    """Schema for plan feature flags."""
    ebook_access = fields.Boolean(missing=False)
    ai_recommendations = fields.Boolean(missing=False)
    pdf_exam_generation = fields.Boolean(missing=False)
    certificate_generation = fields.Boolean(missing=False)
    live_monitoring = fields.Boolean(missing=False)
    excel_export = fields.Boolean(missing=False)
    marketplace_access = fields.Boolean(missing=False)


class PlanCreateSchema(Schema):
    """Schema for creating a plan."""
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    slug = fields.String(missing=None)
    price = fields.Integer(required=True, validate=validate.Range(min=0))
    duration_days = fields.Integer(missing=365, validate=validate.Range(min=1))
    max_students = fields.Integer(missing=0)
    max_teachers = fields.Integer(missing=0)
    exam_limit = fields.Integer(missing=0)
    ai_usage_limit = fields.Integer(missing=0)
    feature_flags = fields.Nested(FeatureFlagsSchema, missing=dict)
    is_for = fields.String(
        missing="institute",
        validate=validate.OneOf(["student", "institute"])
    )
    is_active = fields.Boolean(missing=True)


class PlanUpdateSchema(Schema):
    """Schema for updating a plan."""
    name = fields.String(validate=validate.Length(min=2, max=100))
    price = fields.Integer(validate=validate.Range(min=0))
    duration_days = fields.Integer(validate=validate.Range(min=1))
    max_students = fields.Integer(missing=None)
    max_teachers = fields.Integer(missing=None)
    exam_limit = fields.Integer(missing=None)
    ai_usage_limit = fields.Integer(missing=None)
    feature_flags = fields.Nested(FeatureFlagsSchema, missing=dict)
    is_active = fields.Boolean(missing=None)
    is_for = fields.String(validate=validate.OneOf(["student", "institute"]))


class PlanListSchema(Schema):
    """Schema for listing plans."""
    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    limit = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))
    is_for = fields.String(
        missing=None,
        validate=validate.OneOf(["student", "institute", "all"])
    )
    is_active = fields.Boolean(missing=None)
