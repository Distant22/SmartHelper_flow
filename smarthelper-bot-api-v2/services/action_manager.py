from services.feedback_action import FeedbackAction
from services.report_action import ReportAction
from services.simple_action import SimpleAction


ActionManager = {
    "FeedbackAction":FeedbackAction,
    "ReportAction":ReportAction,
    "SimpleAction":SimpleAction
}
