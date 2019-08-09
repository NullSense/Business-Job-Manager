let BACKEND_URL;
const hostname = window && window.location && window.location.hostname;

if (hostname === 'moldflow.ml') {
  // production
  BACKEND_URL = 'https://moldflow.ml';
} else if (hostname === 'mold.ga') {
  // staging
  BACKEND_URL = 'https://mold.ga';
} else {
  // development
  BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:8000';
}

export const API_URL = `${BACKEND_URL}/api`;
