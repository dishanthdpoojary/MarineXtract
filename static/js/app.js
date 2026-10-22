const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('imageUpload');
const uploadBox = document.querySelector('.upload-box');
const previewWrap = document.getElementById('previewWrap');
const previewImage = document.getElementById('previewImage');
const fileName = document.getElementById('fileName');
const feedback = document.getElementById('uploadFeedback');
const predictButton = document.getElementById('predictButton');
const predictLabel = document.getElementById('predictLabel');
const resultPanel = document.querySelector('.result-panel');
const resultState = document.getElementById('resultState');
const stateTitle = document.getElementById('stateTitle');
const stateMessage = document.getElementById('stateMessage');
const resultCard = document.getElementById('resultCard');
const speciesName = document.getElementById('speciesName');
const confidenceValue = document.getElementById('confidenceValue');
const commonName = document.getElementById('commonName');
const commercialValue = document.getElementById('commercialValue');
const commercialUses = document.getElementById('commercialUses');
let selectedFile = null;
let previewUrl = null;
let busy = false;

function showState(title, message, isError = false) {
  resultCard.classList.add('hidden');
  resultState.classList.remove('hidden');
  resultState.classList.toggle('is-error', isError);
  stateTitle.textContent = title;
  stateMessage.textContent = message;
}

function selectFile(file) {
  if (!file || busy) return;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
  selectedFile = null;
  previewImage.removeAttribute('src');
  previewWrap.classList.add('hidden');
  feedback.classList.add('hidden');
  predictButton.disabled = true;
  showState('Ready when you are', 'Upload a sample and select Analyze sample to view its predicted species, confidence and estimated value.');
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    feedback.textContent = 'Please choose a JPG, PNG or WebP image.';
    feedback.classList.remove('hidden');
    fileInput.value = '';
    return;
  }
  selectedFile = file;
  previewUrl = URL.createObjectURL(file);
  previewImage.src = previewUrl;
  fileName.textContent = file.name;
  previewWrap.classList.remove('hidden');
  predictButton.disabled = false;
}

fileInput.addEventListener('change', () => selectFile(fileInput.files[0]));
previewImage.addEventListener('error', () => {
  selectedFile = null;
  predictButton.disabled = true;
  previewWrap.classList.add('hidden');
  feedback.textContent = 'This image could not be opened. Please choose another file.';
  feedback.classList.remove('hidden');
});

['dragenter', 'dragover'].forEach((type) => {
  uploadBox.addEventListener(type, (event) => {
    event.preventDefault();
    if (!busy) uploadBox.classList.add('drag-active');
  });
});
uploadBox.addEventListener('dragleave', (event) => {
  if (!uploadBox.contains(event.relatedTarget)) uploadBox.classList.remove('drag-active');
});
uploadBox.addEventListener('drop', (event) => {
  event.preventDefault();
  uploadBox.classList.remove('drag-active');
  selectFile(event.dataTransfer.files[0]);
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (busy || !selectedFile) return;
  busy = true;
  predictButton.disabled = true;
  fileInput.disabled = true;
  predictButton.classList.add('is-loading');
  predictLabel.textContent = 'Analyzing sample…';
  resultPanel.setAttribute('aria-busy', 'true');
  showState('Analyzing your sample', 'Identifying the species and preparing your results. This may take a moment.');
  const formData = new FormData();
  formData.append('image', selectedFile);

  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content },
      body: formData,
    });
    if (response.status === 401) {
      window.location.assign('/login');
      return;
    }
    const payload = await response.json().catch(() => null);
    if (!response.ok || !payload || payload.error) {
      const message = response.status >= 500
        ? 'We could not analyze this sample. Please try a different image or try again later.'
        : (payload?.error || 'Unable to upload this image. Please try again.');
      throw new Error(message);
    }
    speciesName.textContent = payload.predicted_species;
    confidenceValue.textContent = `${Number(payload.confidence).toFixed(2)}%`;
    commonName.textContent = payload.common_name;
    commercialValue.textContent = `${new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(payload.commercial_value_inr)} / kg`;
    commercialUses.replaceChildren();
    payload.commercial_uses.forEach((item) => {
      const li = document.createElement('li');
      li.textContent = item;
      commercialUses.appendChild(li);
    });
    resultState.classList.add('hidden');
    resultCard.classList.remove('hidden');
  } catch (error) {
    showState('Analysis could not be completed', error instanceof TypeError
      ? 'Connection interrupted. Check your connection and try again.' : error.message, true);
  } finally {
    busy = false;
    fileInput.disabled = false;
    predictButton.disabled = !selectedFile;
    predictButton.classList.remove('is-loading');
    predictLabel.textContent = 'Analyze sample';
    resultPanel.setAttribute('aria-busy', 'false');
  }
});
window.addEventListener('pagehide', () => {
  if (previewUrl) URL.revokeObjectURL(previewUrl);
});
