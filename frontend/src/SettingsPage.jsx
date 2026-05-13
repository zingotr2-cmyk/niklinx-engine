import { useState, useEffect } from "react";
import { Settings as SettingsIcon, Key, RefreshCw, Check, AlertCircle } from "lucide-react";

const API = "https://niklinx-engine-v2.onrender.com";

export default function SettingsPage() {
  const [status, setStatus] = useState(null);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    fetch(`${API}/api/settings/status`, { cache: "no-store" })
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => {});
  }, []);

  const testEndpoint = async (ep) => {
    setTesting(true);
    setTestResult(null);
    try {
      const r = await fetch(`${API}${ep}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ep.includes("search") ? { max_price: 50 } : { product_id: "prod_001" }),
      });
      const data = await r.json();
      setTestResult({ endpoint: ep, status: r.status, ok: r.ok });
    } catch (e) {
      setTestResult({ endpoint: ep, status: 0, ok: false, error: e.message });
    }
    setTesting(false);
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold text-[#111111] tracking-tight">Settings</h1>
        <p className="text-[#6B6B6B] mt-1">System configuration, API keys, and infrastructure diagnostics.</p>
      </div>

      {status && (
        <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
          <h3 className="text-lg font-semibold text-[#111111] mb-4">System Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">AI Service</div>
              <div className="text-sm font-semibold text-[#111111] capitalize">{status.active_service}</div>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">HWID</div>
              <div className="text-sm font-mono text-[#111111]">{status.hwid}</div>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">OpenAI</div>
              <div className="text-sm flex items-center gap-1">
                {status.has_openai ? <Check size={14} className="text-green-500" /> : <AlertCircle size={14} className="text-yellow-400" />}
                <span className={status.has_openai ? "text-green-600" : "text-[#6B6B6B]"}>
                  {status.has_openai ? "Configured" : "Not set"}
                </span>
              </div>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">Claude</div>
              <div className="text-sm flex items-center gap-1">
                {status.has_claude ? <Check size={14} className="text-green-500" /> : <AlertCircle size={14} className="text-yellow-400" />}
                <span className={status.has_claude ? "text-green-600" : "text-[#6B6B6B]"}>
                  {status.has_claude ? "Configured" : "Not set"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-[#111111]">API Diagnostics</h3>
          <button onClick={() => testEndpoint("/api/research/search")} disabled={testing}
            className="px-4 py-2 rounded-xl bg-[#2563EB] text-white text-sm font-medium hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            <RefreshCw size={14} className={testing ? "animate-spin" : ""} />
            Test API
          </button>
        </div>
        {testResult && (
          <div className="rounded-2xl p-4 bg-white shadow-sm">
            <div className="flex items-center gap-2">
              {testResult.ok ? <Check size={16} className="text-green-500" /> : <AlertCircle size={16} className="text-red-500" />}
              <span className="text-sm font-medium text-[#111111]">{testResult.endpoint}</span>
              <span className="text-xs text-[#6B6B6B]">HTTP {testResult.status}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
