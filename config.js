// API URL: local dev uses Vite proxy; live site uses Render backend
window.AIRDOSA_API = (() => {
  const host = window.location.hostname;
  if (host === 'localhost' || host === '127.0.0.1') {
    return '/api';
  }
  return 'https://crispy-dosa-api.onrender.com/api';
})();
