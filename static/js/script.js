/**
 * AnswerIQ: Client-side Form Logic, Inline Field Clearing, Tabs & History Management
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('evaluationForm');
  const questionInput = document.getElementById('question');
  const answerInput = document.getElementById('student_answer');
  const maxMarksInput = document.getElementById('max_marks');
  const submitBtn = document.getElementById('submitBtn');
  const loadingOverlay = document.getElementById('loadingOverlay');

  const clearQuestionBtn = document.getElementById('clearQuestionBtn');
  const clearAnswerBtn = document.getElementById('clearAnswerBtn');

  const questionCount = document.getElementById('questionCount');
  const answerCount = document.getElementById('answerCount');

  // Toggle in-textarea clear buttons based on content presence
  function toggleClearButtons() {
    if (questionInput && clearQuestionBtn) {
      if (questionInput.value.trim().length > 0) {
        clearQuestionBtn.classList.remove('hidden');
      } else {
        clearQuestionBtn.classList.add('hidden');
      }
    }

    if (answerInput && clearAnswerBtn) {
      if (answerInput.value.trim().length > 0) {
        clearAnswerBtn.classList.remove('hidden');
      } else {
        clearAnswerBtn.classList.add('hidden');
      }
    }
  }

  // Character counter helper
  function updateCounts() {
    if (questionInput && questionCount) {
      questionCount.textContent = `${questionInput.value.length} / 1000 chars`;
    }
    if (answerInput && answerCount) {
      answerCount.textContent = `${answerInput.value.length} / 4000 chars`;
    }
    toggleClearButtons();
  }

  if (questionInput) {
    questionInput.addEventListener('input', updateCounts);
  }
  if (answerInput) {
    answerInput.addEventListener('input', updateCounts);
  }
  updateCounts();

  // Form submission handling
  if (form) {
    form.addEventListener('submit', (e) => {
      const qVal = questionInput ? questionInput.value.trim() : '';
      const aVal = answerInput ? answerInput.value.trim() : '';
      const mVal = maxMarksInput ? parseFloat(maxMarksInput.value) : 0;

      if (!qVal) {
        alert('Please enter a Computer Networking question.');
        e.preventDefault();
        return;
      }
      if (!aVal) {
        alert("Please enter the student's answer to evaluate.");
        e.preventDefault();
        return;
      }
      if (isNaN(mVal) || mVal <= 0) {
        alert('Please enter a valid positive number for maximum marks (e.g. 5.0).');
        e.preventDefault();
        return;
      }

      // Show loading overlay and disable submit button to avoid duplicate submits
      if (loadingOverlay) {
        loadingOverlay.classList.remove('hidden');
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add('btn-loading');
      }
    });
  }
});

// Clear an individual field using the in-field button
function clearField(fieldId) {
  const elem = document.getElementById(fieldId);
  if (elem) {
    elem.value = '';
    elem.focus();
    
    if (fieldId === 'question') {
      const qCount = document.getElementById('questionCount');
      if (qCount) qCount.textContent = '0 / 1000 chars';
      const btn = document.getElementById('clearQuestionBtn');
      if (btn) btn.classList.add('hidden');
    } else if (fieldId === 'student_answer') {
      const aCount = document.getElementById('answerCount');
      if (aCount) aCount.textContent = '0 / 4000 chars';
      const btn = document.getElementById('clearAnswerBtn');
      if (btn) btn.classList.add('hidden');
    }
  }
}

// Clear Entire Form
function clearEntireForm() {
  clearField('question');
  clearField('student_answer');
}

// Switch between 'evaluate' and 'history' tabs
function switchTab(tabName) {
  const evalPanel = document.getElementById('tabContentEval');
  const historyPanel = document.getElementById('tabContentHistory');
  const evalBtn = document.getElementById('tabBtnEval');
  const historyBtn = document.getElementById('tabBtnHistory');

  if (tabName === 'history') {
    if (evalPanel) evalPanel.classList.add('hidden');
    if (historyPanel) historyPanel.classList.remove('hidden');
    if (evalBtn) evalBtn.classList.remove('active');
    if (historyBtn) historyBtn.classList.add('active');
  } else {
    if (historyPanel) historyPanel.classList.add('hidden');
    if (evalPanel) evalPanel.classList.remove('hidden');
    if (historyBtn) historyBtn.classList.remove('active');
    if (evalBtn) evalBtn.classList.add('active');
  }

  // Update browser URL state without reloading
  const url = new URL(window.location);
  url.searchParams.set('tab', tabName);
  window.history.replaceState({}, '', url);
}

// Load a previous submission from History into the active evaluation form
function loadHistoryToForm(questionText, maxMarks, answerText) {
  const qElem = document.getElementById('question');
  const mElem = document.getElementById('max_marks');
  const aElem = document.getElementById('student_answer');

  if (qElem) qElem.value = questionText || '';
  if (mElem) mElem.value = maxMarks || 5.0;
  if (aElem) aElem.value = answerText || '';

  const qCount = document.getElementById('questionCount');
  const aCount = document.getElementById('answerCount');
  if (qCount && qElem) qCount.textContent = `${qElem.value.length} / 1000 chars`;
  if (aCount && aElem) aCount.textContent = `${aElem.value.length} / 4000 chars`;

  // Show clear buttons
  const qClear = document.getElementById('clearQuestionBtn');
  const aClear = document.getElementById('clearAnswerBtn');
  if (qClear && qElem && qElem.value) qClear.classList.remove('hidden');
  if (aClear && aElem && aElem.value) aClear.classList.remove('hidden');

  // Switch to the evaluate tab
  switchTab('evaluate');

  // Smooth scroll to form
  const form = document.getElementById('evaluationForm');
  if (form) {
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// Handler for history buttons using data attributes
function loadHistoryFromButton(btn) {
  if (!btn) return;
  const q = btn.getAttribute('data-question') || '';
  const m = parseFloat(btn.getAttribute('data-marks')) || 5.0;
  const a = btn.getAttribute('data-answer') || '';
  loadHistoryToForm(q, m, a);
}

