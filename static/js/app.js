const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('imageUpload');
const previewWrap = document.getElementById('previewWrap');
const previewImage = document.getElementById('previewImage');
const resultState = document.getElementById('resultState');
const resultCard = document.getElementById('resultCard');

const speciesName = document.getElementById('speciesName');
const confidenceValue = document.getElementById('confidenceValue');
const commonName = document.getElementById('commonName');
const commercialValue = document.getElementById('commercialValue');
const commercialUses = document.getElementById('commercialUses');

fileInput.addEventListener('change', (event) => {
  const [file] = event.target.files;
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (loadEvent) => {
    previewImage.src = loadEvent.target.result;
    previewWrap.classList.remove('hidden');
  };
  reader.readAsDataURL(file);
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const file = fileInput.files[0];
  if (!file) {
    alert('Please select an algae image first.');
    return;
  }

  const formData = new FormData();
  formData.append('image', file);

  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok || payload.error) {
      throw new Error(payload.error || 'Unable to process image.');
    }

    resultState.classList.add('hidden');
    resultCard.classList.remove('hidden');

    speciesName.textContent = payload.predicted_species;
    confidenceValue.textContent = `${payload.confidence.toFixed(2)}%`;
    commonName.textContent = payload.common_name;
    commercialValue.textContent = `₹${Number(payload.commercial_value_inr).toFixed(2)} / kg`;

    commercialUses.innerHTML = '';
    payload.commercial_uses.forEach((item) => {
      const li = document.createElement('li');
      li.textContent = item;
      commercialUses.appendChild(li);
    });
  } catch (error) {
    resultCard.classList.add('hidden');
    resultState.classList.remove('hidden');
    resultState.innerHTML = `
      <div class="empty-icon">⚠️</div>
      <p>${error.message}</p>
    `;
  }
});
