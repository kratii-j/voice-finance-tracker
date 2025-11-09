const DEFAULT_TIMEOUT = 10000;

async function apiFetch(path, options = {}) {
  const { timeout = DEFAULT_TIMEOUT, ...rest } = options;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(path, {
      credentials: 'same-origin',
      ...rest,
      signal: controller.signal,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const error = new Error(
        (data && (data.error || data.message)) || `Request failed: ${response.status}`,
      );
      error.status = response.status;
      error.body = data;
      throw error;
    }

    return data;
  } finally {
    clearTimeout(timer);
  }
}

export const getSummary = () => apiFetch('/api/summary');
export const getRecent = (limit = 10) => apiFetch(`/api/recent?limit=${limit}`);
export const getCategoryBreakdown = () => apiFetch('/api/charts/category-breakdown');
export const getDailyTotals = (days = 7) => apiFetch(`/api/charts/daily-totals?days=${days}`);
export const getMonthlyTotals = (months = 6) => apiFetch(`/api/charts/monthly-totals?months=${months}`);

export const addExpense = (payload) =>
  apiFetch('/api/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

export const sendVoiceCommand = (command) =>
  apiFetch('/api/voice_command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command }),
    timeout: 15000,
  });

export default apiFetch;
