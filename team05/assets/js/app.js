// Core forms, validation and charts work without JavaScript.
document.addEventListener('submit', (event) => {
  const message = event.target.dataset.confirm;
  if (message && !window.confirm(message)) event.preventDefault();
});
const invalid = document.querySelector('[aria-invalid="true"]');
if (invalid) invalid.focus({preventScroll: true});
