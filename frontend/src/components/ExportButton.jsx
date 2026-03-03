import { useState } from "react";
import { Download, FileText, FileSpreadsheet, Loader2 } from "lucide-react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "";

export default function ExportButton({ analysisData }) {
  const [exporting, setExporting] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [error, setError] = useState("");

  const handleExport = async (format) => {
    setShowMenu(false);
    setExporting(true);
    setError("");

    try {
      const response = await axios.post(
        `${API_BASE}/api/export/${format}`,
        analysisData,
        {
          responseType: "blob",
          timeout: 30000,
        }
      );

      const contentType =
        format === "pdf" ? "application/pdf" : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
      const extension = format === "pdf" ? "pdf" : "xlsx";
      const companyName = analysisData?.company?.ten_dn || "BCTC";
      const fileName = `${companyName}_BaoCao.${extension}`;

      const blob = new Blob([response.data], { type: contentType });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(
        `Khong the xuat file ${format.toUpperCase()}. Vui long thu lai.`
      );
      setTimeout(() => setError(""), 5000);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        disabled={exporting}
        className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg
          text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {exporting ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Download className="w-4 h-4" />
        )}
        {exporting ? "Dang xuat..." : "Xuat bao cao"}
      </button>

      {showMenu && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowMenu(false)}
          />
          <div className="absolute right-0 mt-2 w-52 bg-white rounded-lg shadow-lg border border-gray-200 z-20 py-1">
            <button
              onClick={() => handleExport("excel")}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700
                hover:bg-gray-50 transition-colors"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
              Xuat Excel (.xlsx)
            </button>
            <button
              onClick={() => handleExport("pdf")}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700
                hover:bg-gray-50 transition-colors"
            >
              <FileText className="w-4 h-4 text-red-600" />
              Xuat PDF (.pdf)
            </button>
          </div>
        </>
      )}

      {error && (
        <div className="absolute right-0 mt-2 w-64 bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-xs text-red-600 z-20">
          {error}
        </div>
      )}
    </div>
  );
}
