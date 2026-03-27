"""
Routes package for ExamSaaS platform.
Flask blueprints for API endpoints.
"""
from app.routes.auth import auth_bp
from app.routes.exams import exams_bp
from app.routes.results import results_bp
from app.routes.attempts import attempts_bp
from app.routes.institutes import institutes_bp
from app.routes.support import support_bp
from app.routes.analytics import analytics_bp
from app.routes.superadmin_analytics import superadmin_bp
from app.routes.pdfs import pdfs_bp
from app.routes.certificates import certificates_bp
from app.routes.ebooks import ebooks_bp
from app.routes.ai import ai_bp
from app.routes.users import users_bp
from app.routes.questions import questions_bp
from app.routes.plans import plans_bp
from app.routes.subscriptions import subscriptions_bp
from app.routes.payments import payments_bp
from app.routes.wallet import wallet_bp

__all__ = [
    "auth_bp",
    "exams_bp",
    "results_bp",
    "attempts_bp",
    "institutes_bp",
    "support_bp",
    "analytics_bp",
    "superadmin_bp",
    "pdfs_bp",
    "certificates_bp",
    "ebooks_bp",
    "ai_bp",
    "users_bp",
    "questions_bp",
    "plans_bp",
    "subscriptions_bp",
    "payments_bp",
    "wallet_bp",
]
