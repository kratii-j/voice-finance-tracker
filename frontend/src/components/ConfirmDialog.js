import React from 'react';

const normalizeOption = (option) => {
  if (!option) {
    return { key: 'option-null', label: 'Unknown option' };
  }
  if (typeof option === 'string') {
    return { key: option, label: option, value: option };
  }
  const label = option.label || option.text || option.command || String(option.value ?? option);
  const value = option.value ?? option.command ?? option.text ?? option;
  return {
    key: option.key || label,
    label,
    value,
  };
};

const ConfirmDialog = ({ open, title, message, options = [], onConfirm, onCancel }) => {
  if (!open) {
    return null;
  }

  const normalized = options.map(normalizeOption);

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-2xl">
        <div className="border-b border-blue-100 bg-blue-600/10 px-6 py-4">
          <h3 className="text-lg font-semibold text-blue-900">{title || 'Please confirm'}</h3>
        </div>
        <div className="px-6 py-5 space-y-4">
          {message && <p className="text-sm text-blue-800">{message}</p>}
          <div className="space-y-2">
            {normalized.map((option) => (
              <button
                key={option.key}
                type="button"
                onClick={() => onConfirm?.(option)}
                className="w-full rounded-lg border border-blue-200 px-4 py-2 text-left text-sm font-medium text-blue-900 transition-colors hover:border-blue-400 hover:bg-blue-50"
              >
                {option.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={onCancel}
            className="w-full rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
