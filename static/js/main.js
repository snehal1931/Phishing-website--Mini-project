/* Main JS for CyberShield India */

// Password visibility toggle
function togglePassword(fieldId, btn) {
  const field = document.getElementById(fieldId);
  const icon  = btn.querySelector('i');
  if (field.type === 'password') {
    field.type = 'text';
    icon.className = 'bi bi-eye-slash';
  } else {
    field.type = 'password';
    icon.className = 'bi bi-eye';
  }
}

// Auto-dismiss alert toasts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
  const toasts = document.querySelectorAll('.alert-toast');
  toasts.forEach(function (toast) {
    setTimeout(function () {
      toast.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 500);
    }, 4000);
  });

  // Animate confidence bars on result page
  const fills = document.querySelectorAll('.confidence-fill, .mini-bar');
  fills.forEach(function (fill) {
    const target = fill.style.width;
    fill.style.width = '0%';
    setTimeout(() => { fill.style.width = target; }, 100);
  });
});
