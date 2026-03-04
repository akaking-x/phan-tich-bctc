import { useState } from "react";
import axios from "axios";
import {
  Wrench,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Download,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  RotateCcw,
} from "lucide-react";
import { formatVND } from "../utils/formatters";

const API_BASE = import.meta.env.VITE_API_BASE || "";

const REPORT_LABELS = {
  cdkt: "Can doi KT",
  kqhdkd: "Ket qua HDKD",
  lctt: "Luu chuyen TT",
};

const SECTION_LABELS = {
  so_cuoi_nam: "So cuoi nam",
  so_dau_nam: "So dau nam",
  nam_nay: "Nam nay",
  nam_truoc: "Nam truoc",
};

export default function AutoCorrect({ data, xmlFile, onCorrectedData }) {
  const [corrections, setCorrections] = useState([]);
  const [selected, setSelected] = useState({});
  const [correctedAnalysis, setCorrectedAnalysis] = useState(null);
  const [originalAnalysis, setOriginalAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");
  const [step, setStep] = useState(1);
  const [showComparison, setShowComparison] = useState(false);

  const validation = data?.validation || {};
  const errorCount = validation.errors || 0;
  const warningCount = validation.warnings || 0;
  const failedDetails = (validation.details || []).filter(
    (d) => d.severity !== "ok"
  );

  // Step 2: Goi API auto-correct
  const handleAutoCorrect = async () => {
    if (!xmlFile) {
      setError("Khong tim thay file XML goc. Vui long tai len lai.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", xmlFile);

    try {
      const response = await axios.post(
        `${API_BASE}/api/auto-correct`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 60000,
        }
      );

      const result = response.data;
      if (result.success) {
        setCorrections(result.corrections || []);
        setCorrectedAnalysis(result.corrected_analysis || null);
        setOriginalAnalysis(result.original_analysis || null);

        // Chon tat ca corrections mac dinh
        const sel = {};
        (result.corrections || []).forEach((_, i) => {
          sel[i] = true;
        });
        setSelected(sel);
        setStep(2);
      } else {
        setError("Khong the tu dong sua. Vui long thu lai.");
      }
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        "Loi khi tu dong sua. Vui long thu lai.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Download XML da sua
  const handleDownload = async () => {
    if (!xmlFile) {
      setError("Khong tim thay file XML goc.");
      return;
    }

    const selectedCorr = corrections.filter((_, i) => selected[i]);
    if (selectedCorr.length === 0) {
      setError("Vui long chon it nhat 1 muc sua.");
      return;
    }

    setDownloading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", xmlFile);
    formData.append("corrections", JSON.stringify(selectedCorr));

    try {
      const response = await axios.post(
        `${API_BASE}/api/apply-corrections`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          responseType: "blob",
          timeout: 60000,
        }
      );

      // Tao link download
      const blob = new Blob([response.data], { type: "application/xml" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download =
        xmlFile.name.replace(".xml", "_corrected.xml") || "corrected.xml";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setStep(3);

      // Cap nhat analysis data neu co callback
      if (onCorrectedData && correctedAnalysis) {
        onCorrectedData(correctedAnalysis);
      }
    } catch (err) {
      setError("Loi khi tai XML da sua. Vui long thu lai.");
    } finally {
      setDownloading(false);
    }
  };

  const toggleAll = (checked) => {
    const sel = {};
    corrections.forEach((_, i) => {
      sel[i] = checked;
    });
    setSelected(sel);
  };

  const selectedCount = Object.values(selected).filter(Boolean).length;

  return (
    <div className="p-4 lg:p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center">
          <Wrench className="w-5 h-5 text-orange-600" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            Tu dong sua so lieu
          </h1>
          <p className="text-sm text-gray-500">
            Phat hien va sua loi logic trong BCTC
          </p>
        </div>
      </div>

      {/* Step 1: Hien thi loi hien tai */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <div className="flex items-center gap-2 mb-4">
          <span className="w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
            1
          </span>
          <h2 className="text-base font-semibold text-gray-800">
            Loi phat hien
          </h2>
          {errorCount + warningCount > 0 ? (
            <span className="ml-auto text-sm text-red-600 font-medium">
              {errorCount} loi, {warningCount} canh bao
            </span>
          ) : (
            <span className="ml-auto text-sm text-emerald-600 font-medium">
              Khong co loi
            </span>
          )}
        </div>

        {failedDetails.length > 0 ? (
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {failedDetails.map((d, i) => (
              <div
                key={i}
                className={`flex items-center gap-2 text-sm px-3 py-2 rounded-lg ${
                  d.severity === "critical"
                    ? "bg-rose-50 text-rose-700"
                    : d.severity === "error"
                      ? "bg-red-50 text-red-700"
                      : "bg-amber-50 text-amber-700"
                }`}
              >
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span className="font-medium">{d.rule_id}</span>
                <span className="flex-1 truncate">{d.rule_name}</span>
                {d.difference !== 0 && (
                  <span className="text-xs font-mono">
                    {formatVND(d.difference)}
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-emerald-600 bg-emerald-50 px-4 py-3 rounded-lg">
            <CheckCircle2 className="w-4 h-4" />
            Tat ca cac quy tac deu dat. Khong can sua.
          </div>
        )}

        {/* Nut Tu dong sua */}
        {failedDetails.length > 0 && step === 1 && (
          <div className="mt-4 flex justify-center">
            <button
              onClick={handleAutoCorrect}
              disabled={loading || !xmlFile}
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-orange-600 text-white rounded-xl
                text-sm font-semibold hover:bg-orange-700 transition-colors
                disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Dang phan tich va sua...
                </>
              ) : (
                <>
                  <Wrench className="w-4 h-4" />
                  Tu dong sua so lieu
                </>
              )}
            </button>
          </div>
        )}

        {!xmlFile && failedDetails.length > 0 && (
          <p className="mt-2 text-xs text-gray-400 text-center">
            Can tai len lai file XML de su dung chuc nang nay
          </p>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Step 2: Bang corrections */}
      {step >= 2 && corrections.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <span className="w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
              2
            </span>
            <h2 className="text-base font-semibold text-gray-800">
              De xuat sua doi
            </h2>
            <span className="ml-auto text-sm text-gray-500">
              {selectedCount}/{corrections.length} muc da chon
            </span>
          </div>

          {/* Select all */}
          <div className="flex items-center gap-2 mb-3 pb-3 border-b border-gray-100">
            <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedCount === corrections.length}
                onChange={(e) => toggleAll(e.target.checked)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              Chon tat ca
            </label>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 text-xs border-b border-gray-200">
                  <th className="pb-2 pr-2 w-8"></th>
                  <th className="pb-2 pr-3">Bao cao</th>
                  <th className="pb-2 pr-3">Ma so</th>
                  <th className="pb-2 pr-3 text-right">Gia tri cu</th>
                  <th className="pb-2 pr-3 text-center w-8"></th>
                  <th className="pb-2 pr-3 text-right">Gia tri moi</th>
                  <th className="pb-2 pr-3 text-right">Chenh lech</th>
                  <th className="pb-2">Quy tac</th>
                </tr>
              </thead>
              <tbody>
                {corrections.map((c, i) => {
                  const diff = c.new_value - c.old_value;
                  return (
                    <tr
                      key={i}
                      className={`border-b border-gray-50 ${selected[i] ? "bg-orange-50/50" : ""}`}
                    >
                      <td className="py-2.5 pr-2">
                        <input
                          type="checkbox"
                          checked={!!selected[i]}
                          onChange={(e) =>
                            setSelected({ ...selected, [i]: e.target.checked })
                          }
                          className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                        />
                      </td>
                      <td className="py-2.5 pr-3">
                        <span className="inline-flex items-center px-2 py-0.5 bg-gray-100 text-gray-700 text-xs font-medium rounded">
                          {REPORT_LABELS[c.report] || c.report}
                        </span>
                      </td>
                      <td className="py-2.5 pr-3 font-mono text-gray-800">
                        {c.code}
                      </td>
                      <td className="py-2.5 pr-3 text-right font-mono text-gray-500">
                        {formatVND(c.old_value)}
                      </td>
                      <td className="py-2.5 pr-3 text-center">
                        <ArrowRight className="w-3.5 h-3.5 text-orange-500 inline" />
                      </td>
                      <td className="py-2.5 pr-3 text-right font-mono font-semibold text-orange-700">
                        {formatVND(c.new_value)}
                      </td>
                      <td
                        className={`py-2.5 pr-3 text-right font-mono text-xs ${
                          diff > 0
                            ? "text-emerald-600"
                            : diff < 0
                              ? "text-red-600"
                              : "text-gray-400"
                        }`}
                      >
                        {diff > 0 ? "+" : ""}
                        {formatVND(diff)}
                      </td>
                      <td className="py-2.5">
                        <div className="text-xs text-gray-500">
                          <span className="font-medium text-gray-700">
                            {c.rule_id}
                          </span>
                          <span className="ml-1">{c.reason}</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Nut Download */}
          {step === 2 && (
            <div className="mt-5 flex items-center gap-3 justify-center">
              <button
                onClick={() => {
                  setStep(1);
                  setCorrections([]);
                  setSelected({});
                  setCorrectedAnalysis(null);
                }}
                className="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-300 text-gray-700 rounded-xl
                  text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                Lam lai
              </button>
              <button
                onClick={handleDownload}
                disabled={downloading || selectedCount === 0}
                className="inline-flex items-center gap-2 px-6 py-2.5 bg-indigo-600 text-white rounded-xl
                  text-sm font-semibold hover:bg-indigo-700 transition-colors
                  disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {downloading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Dang tao file...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Xac nhan & Tai XML da sua
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Khong co gi de sua */}
      {step >= 2 && corrections.length === 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 text-sm text-emerald-600 bg-emerald-50 px-4 py-3 rounded-lg">
            <CheckCircle2 className="w-4 h-4" />
            So lieu da hop le, khong can sua doi.
          </div>
        </div>
      )}

      {/* Step 3: Download xong */}
      {step === 3 && (
        <div className="bg-white rounded-xl border border-emerald-200 p-5">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-6 h-6 bg-emerald-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
              3
            </span>
            <h2 className="text-base font-semibold text-gray-800">
              Hoan thanh
            </h2>
          </div>
          <div className="flex items-center gap-2 text-sm text-emerald-700 bg-emerald-50 px-4 py-3 rounded-lg">
            <CheckCircle2 className="w-5 h-5" />
            <div>
              <p className="font-medium">
                Da tai xuong file XML da sua thanh cong!
              </p>
              <p className="text-emerald-600 mt-0.5">
                Hay tai len lai file da sua de kiem tra ket qua.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* So sanh before/after */}
      {step >= 2 && correctedAnalysis && originalAnalysis && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <button
            onClick={() => setShowComparison(!showComparison)}
            className="flex items-center gap-2 w-full text-left"
          >
            {showComparison ? (
              <ChevronUp className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            )}
            <h2 className="text-base font-semibold text-gray-800">
              So sanh truoc / sau khi sua
            </h2>
          </button>

          {showComparison && (
            <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Before */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-red-700 mb-3">
                  Truoc khi sua
                </h3>
                <ValidationSummary validation={originalAnalysis.validation} />
              </div>
              {/* After */}
              <div className="border border-emerald-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-emerald-700 mb-3">
                  Sau khi sua
                </h3>
                <ValidationSummary validation={correctedAnalysis.validation} />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ValidationSummary({ validation }) {
  if (!validation) return null;

  const { total_checks = 0, passed = 0, warnings = 0, errors = 0, details = [] } = validation;
  const passRate = total_checks > 0 ? Math.round((passed / total_checks) * 100) : 0;

  return (
    <div>
      <div className="flex items-center gap-4 mb-3">
        <div className="text-2xl font-bold text-gray-800">{passRate}%</div>
        <div className="text-xs text-gray-500">
          <div>{passed}/{total_checks} dat</div>
          <div>{errors} loi, {warnings} canh bao</div>
        </div>
      </div>
      <div className="space-y-1 max-h-40 overflow-y-auto">
        {details.slice(0, 10).map((d, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span
              className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                d.severity === "ok" ? "bg-emerald-500" : d.severity === "warning" ? "bg-amber-500" : "bg-red-500"
              }`}
            />
            <span className="text-gray-600 truncate">{d.rule_id}: {d.rule_name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
