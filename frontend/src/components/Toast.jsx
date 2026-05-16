import { useState, useEffect, useCallback } from "react";
import { X, CheckCircle, AlertCircle, RefreshCw } from "lucide-react";

let toastId = 0;
let addToastFn = null;

export function toast(message, type = "success", duration = 4000) {
  if (addToastFn) {
    addToastFn({ id: ++toastId, message, type, duration });
  }
}

export function setToastHandler(fn) {
  addToastFn = fn;
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  const add = useCallback((t) => {
    setToasts((prev) => [...prev, t]);
  }, []);

  useEffect(() => {
    setToastHandler(add);
    return () => setToastHandler(null);
  }, [add]);

  const remove = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  useEffect(() => {
    if (toasts.length === 0) return;
    const t = toasts[toasts.length - 1];
    const timer = setTimeout(() => remove(t.id), t.duration);
    return () => clearTimeout(timer);
  }, [toasts]);

  if (toasts.length === 0) return null;

  const current = toasts[toasts.length - 1];
  const icons = {
    success: <CheckCircle size={14} className="text-green-500" />,
    error: <AlertCircle size={14} className="text-red-500" />,
    loading: <RefreshCw size={14} className="text-blue-500 animate-spin" />,
  };

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="flex items-center gap-2.5 px-4 py-3 rounded-2xl bg-white shadow-lg border border-gray-100 text-sm text-[#111111] animate-in slide-in-from-right-2 fade-in-0 min-w-[280px]"
          style={{ animation: "slideIn 0.3s ease-out" }}
        >
          {icons[t.type] || icons.success}
          <span className="flex-1">{t.message}</span>
          <button onClick={() => remove(t.id)} className="text-[#6B6B6B] hover:text-[#111111] transition-colors">
            <X size={14} />
          </button>
        </div>
      ))}
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}