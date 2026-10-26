"""
AnswerIQ: AI-Based Computer Networking Answer Evaluation System
Main Flask entry point.
"""

import os
import sys
import webbrowser
import threading
from typing import Optional
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

# Ensure the root project directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.evaluator import EvaluatorOrchestrator
from src.dataset_loader import DatasetLoaderError
from src.history_manager import HistoryManager

# Load environment configuration
load_dotenv()

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "answeriq-secret-key-production-change")

# Global instances (cached in memory)
evaluator: Optional[EvaluatorOrchestrator] = None
history_mgr = HistoryManager()


def get_evaluator() -> EvaluatorOrchestrator:
    global evaluator
    if evaluator is None:
        evaluator = EvaluatorOrchestrator.get_instance(data_dir="data")
    return evaluator


@app.route("/", methods=["GET"])
def index():
    """Renders the main question & answer submission form and loads history."""
    all_history = history_mgr.load_all()
    active_tab = request.args.get("tab", "evaluate")
    return render_template("index.html", history=all_history, active_tab=active_tab)


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """Processes student submission, validates inputs, records history, and renders results."""
    question = request.form.get("question", "").strip()
    student_answer = request.form.get("student_answer", "").strip()
    max_marks_raw = request.form.get("max_marks", "").strip()

    all_history = history_mgr.load_all()

    # Server-Side Input Validation
    if not question:
        return render_template(
            "index.html",
            error_message="Question field cannot be empty. Please provide a computer networking question.",
            prefill_question=question,
            prefill_student_answer=student_answer,
            prefill_max_marks=max_marks_raw or "5.0",
            history=all_history
        ), 400

    if not student_answer:
        return render_template(
            "index.html",
            error_message="Student answer cannot be empty. Please enter the student's text to evaluate.",
            prefill_question=question,
            prefill_student_answer=student_answer,
            prefill_max_marks=max_marks_raw or "5.0",
            history=all_history
        ), 400

    if len(question) > 2000:
        return render_template(
            "index.html",
            error_message="Question is too long (maximum 2,000 characters allowed).",
            prefill_question=question[:2000],
            prefill_student_answer=student_answer,
            prefill_max_marks=max_marks_raw,
            history=all_history
        ), 400

    if len(student_answer) > 8000:
        return render_template(
            "index.html",
            error_message="Student answer is too long (maximum 8,000 characters allowed).",
            prefill_question=question,
            prefill_student_answer=student_answer[:8000],
            prefill_max_marks=max_marks_raw,
            history=all_history
        ), 400

    try:
        max_marks = float(max_marks_raw)
        if max_marks <= 0 or max_marks > 100:
            raise ValueError()
    except (ValueError, TypeError):
        return render_template(
            "index.html",
            error_message="Maximum marks must be a valid positive number between 1 and 100.",
            prefill_question=question,
            prefill_student_answer=student_answer,
            prefill_max_marks="5.0",
            history=all_history
        ), 400

    try:
        engine = get_evaluator()
        result = engine.evaluate(
            question=question,
            student_answer=student_answer,
            max_marks=max_marks
        )

        # Persist evaluation result to data/history.json
        record_id = history_mgr.save_record(result)
        result["history_id"] = record_id

        return render_template("results.html", res=result)

    except DatasetLoaderError as de:
        return render_template(
            "error.html",
            error_title="Dataset Not Found or Corrupted",
            error_message=str(de),
            error_hint="Ensure that at least one valid .parquet file is placed inside the data/ folder."
        ), 500

    except Exception as e:
        # Avoid leaking sensitive stack traces or environment variables
        return render_template(
            "error.html",
            error_title="Evaluation Processing Error",
            error_message="An unexpected error occurred during answer evaluation.",
            error_hint="Please verify that your inputs and local dataset are correctly formatted."
        ), 500


@app.route("/history/<record_id>", methods=["GET"])
def view_history(record_id: str):
    """Retrieves and displays a historical evaluation result."""
    record = history_mgr.get_by_id(record_id)
    if not record:
        return render_template(
            "error.html",
            error_title="Evaluation Record Not Found",
            error_message=f"The evaluation history record '{record_id}' does not exist.",
            error_hint="It may have been cleared or not saved."
        ), 404

    eval_result = record.get("evaluation_result", {})
    return render_template("results.html", res=eval_result, from_history=True, record_meta=record)


@app.route("/history/clear", methods=["POST"])
def clear_history():
    """Clears all stored evaluations from history.json."""
    history_mgr.clear_all()
    return redirect(url_for("index", tab="history"))


@app.errorhandler(400)
def handle_bad_request(e):
    return render_template(
        "error.html",
        error_title="Bad Request (400)",
        error_message="The submitted form data was invalid or malformed.",
        error_hint="Please return to the home page and re-enter your submission."
    ), 400


@app.errorhandler(404)
def handle_not_found(e):
    return render_template(
        "error.html",
        error_title="Page Not Found (404)",
        error_message="The requested page does not exist on this local server.",
        error_hint="Click below to navigate back to the AnswerIQ home page."
    ), 404


@app.errorhandler(500)
def handle_server_error(e):
    return render_template(
        "error.html",
        error_title="Internal Server Error (500)",
        error_message="The local evaluation server encountered an unexpected error.",
        error_hint="Check server terminal logs for details."
    ), 500


def open_browser(url: str):
    """Opens default web browser after server has started."""
    try:
        webbrowser.open_new(url)
    except Exception:
        pass


def run_app():
    port = int(os.getenv("FLASK_PORT", "5000"))
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    url = f"http://{host}:{port}"

    print("=" * 60)
    print(" AnswerIQ – Performance Rating and Natural-language Intelligent Text Assessment")
    print(f" Local Web Interface: {url}")
    print(" Grounding Policy: Strictly Local Parquet Datasets")
    print(f" Persistent History: {history_mgr.file_path}")
    print("=" * 60)

    # Launch browser automatically once server starts (prevent duplicate tabs)
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1.2, open_browser, args=[url]).start()

    # Local development server with debug=False by default
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_app()
