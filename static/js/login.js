const passwordInput = document.getElementById('password');
const togglePassword = document.getElementById('togglePassword');

togglePassword.addEventListener('click', () => {
  const visible = passwordInput.type === 'password';
  passwordInput.type = visible ? 'text' : 'password';
  togglePassword.textContent = visible ? 'Hide' : 'Show';
  togglePassword.setAttribute('aria-label', visible ? 'Hide password' : 'Show password');
  togglePassword.setAttribute('aria-pressed', String(visible));
});
