'use strict';

const progress = document.getElementById('progress');
const decisionButtons = [...document.querySelectorAll('[data-decision]')];
const decisionResult = document.getElementById('decisionResult');
const evidenceInputs = [...document.querySelectorAll('[data-evidence]')];
const evidenceTitle = document.getElementById('evidenceTitle');
const evidenceText = document.getElementById('evidenceText');

const decisionCopy = {
  conscious: {
    title: 'Your judgment treats present organization as more important than historical origin.',
    text: 'You are not claiming that the being is the original person. You are separating numerical identity from present subjectivity. The unresolved burden now moves to architecture: what, exactly, makes the current process capable of experience?'
  },
  uncertain: {
    title: 'Your judgment preserves the distinction the book is built around.',
    text: 'The biography is false, but that fact does not answer whether a subject exists now. Uncertainty here is not indecision. It is refusal to let one question impersonate another.'
  },
  empty: {
    title: 'Your judgment requires an additional criterion.',
    text: 'Artificial origin alone cannot do the work. To conclude that nobody is present, you need a further reason: biological dependence, missing causal organization, absence of integration, or another substantive theory of consciousness.'
  }
};

decisionButtons.forEach(button => {
  button.addEventListener('click', () => {
    decisionButtons.forEach(item => item.classList.remove('active'));
    button.classList.add('active');
    const copy = decisionCopy[button.dataset.decision];
    decisionResult.innerHTML = `<strong>${copy.title}</strong><span>${copy.text}</span>`;
    decisionResult.classList.add('show');
    localStorage.setItem('constructed-subject-decision', button.dataset.decision);
  });
});

const evidenceCopy = {
  0: ['No subject-specific case yet', 'Fluent language, intelligence, and self-reference remain compatible with learned behavioral simulation.'],
  1: ['One line of evidence', 'This changes one part of the explanation, but a single feature is easily reproduced by a nonconscious controller.'],
  2: ['A partial architecture appears', 'Multiple features begin to constrain rival explanations, but the case remains fragile and theory-dependent.'],
  3: ['Converging evidence', 'The system now has a more serious subjectivity profile. The strongest remaining question is whether these mechanisms jointly constitute experience or only sophisticated control.'],
  4: ['A strong candidate system', 'Architecture, persistence, causal role, and self-indexing now converge. Consciousness is still inferred rather than observed, but categorical dismissal becomes harder to defend.'],
  5: ['A morally serious candidate', 'The system displays integrated organization plus candidate valence. This still does not prove experience, but it raises welfare risk enough that destructive testing would require justification.']
};

function updateEvidence() {
  const count = evidenceInputs.filter(input => input.checked).length;
  const copy = evidenceCopy[count];
  evidenceTitle.textContent = copy[0];
  evidenceText.textContent = copy[1];
  localStorage.setItem('constructed-subject-evidence', JSON.stringify(evidenceInputs.filter(i => i.checked).map(i => i.value)));
}

evidenceInputs.forEach(input => input.addEventListener('change', updateEvidence));

const savedDecision = localStorage.getItem('constructed-subject-decision');
if (savedDecision) document.querySelector(`[data-decision="${savedDecision}"]`)?.click();

try {
  const savedEvidence = JSON.parse(localStorage.getItem('constructed-subject-evidence') || '[]');
  evidenceInputs.forEach(input => { input.checked = savedEvidence.includes(input.value); });
  updateEvidence();
} catch { updateEvidence(); }

function setProgress() {
  const height = document.documentElement.scrollHeight - window.innerHeight;
  const value = height > 0 ? (window.scrollY / height) * 100 : 0;
  progress.style.width = `${Math.min(100, Math.max(0, value))}%`;
}
window.addEventListener('scroll', setProgress, { passive: true });
setProgress();
