import { useState, useMemo } from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  AlertOctagon,
  Filter,
  Search,
} from "lucide-react";
import { formatVND, severityColor, severityLabel } from "../utils/formatters";

const SEVERITY_ORDER = { critical: 0, error: 1, warning: 2, ok: 3 };

const SEVERITY_ICONS = {
  ok: CheckCircle2,
  warning: AlertTriangle,
  error: XCircle,
  critical: AlertOctagon,
};

export default function CrossCheck({ data }) {
  const { validation } = data;
  const [filterSeverity, setFilterSeverity] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("severity");

  const details = validation?.details || [];

  // Filter and sort
  const filteredResults = useMemo(() => {
    let results = [...details];

    // Filter by severity
    if (filterSeverity !== "all") {
      results = results.filter((r) => r.severity === filterSeverity);
    }

    // Search
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      results = results.filter(
        (r) =>
          r.rule_id.toLowerCase().includes(q) ||
          r.rule_name.toLowerCase().includes(q) ||
          r.message.toLowerCase().includes(q)
      );
    }

    // Sort
    if (sortBy === "severity") {
      results.sort(
        (a, b) =>
          (SEVERITY_ORDER[a.severity] ?? 99) -
          (SEVERITY_ORDER[b.severity] ?? 99)
      );
    } else if (sortBy === "rule_id") {
      results.sort((a, b) => a.rule_id.localeCompare(b.rule_id));
    } else if (sortBy === "difference") {
      results.sort(
        (a, b) => Math.abs(b.difference || 0) - Math.abs(a.difference || 0)
      );
    }

    return results;
  }, [details, filterSeverity, searchQuery, sortBy]);

  // Severity counts
  const counts = useMemo(() => {
    const c = { ok: 0, warning: 0, error: 0, critical: 0 };
    details.forEach((r) => {
      c[r.severity] = (c[r.severity] || 0) + 1;
    });
    return c;
  }, [details]);

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <SummaryCard
          label="Tong so"
          value={details.length}
          color="gray"
          active={filterSeverity === "all"}
          onClick={() => setFilterSeverity("all")}
        />
        <SummaryCard
          label="Dat"
          value={counts.ok}
          color="emerald"
          active={filterSeverity === "ok"}
          onClick={() =>
            setFilterSeverity(filterSeverity === "ok" ? "all" : "ok")
          }
        />
        <SummaryCard
          label="Canh bao"
          value={counts.warning}
          color="amber"
          active={filterSeverity === "warning"}
          onClick={() =>
            setFilterSeverity(
              filterSeverity === "warning" ? "all" : "warning"
            )
          }
        />
        <SummaryCard
          label="Loi"
          value={counts.error}
          color="red"
          active={filterSeverity === "error"}
          onClick={() =>
            setFilterSeverity(filterSeverity === "error" ? "all" : "error")
          }
        />
        <SummaryCard
          label="Nghiem trong"
          value={counts.critical}
          color="rose"
          active={filterSeverity === "critical"}
          onClick={() =>
            setFilterSeverity(
              filterSeverity === "critical" ? "all" : "critical"
            )
          }
        />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tim kiem quy tac..."
              className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-sm border border-gray-300 rounded-lg px-3 py-2
                focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="severity">Sap xep theo muc do</option>
              <option value="rule_id">Sap xep theo ma quy tac</option>
              <option value="difference">Sap xep theo chenh lech</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-700 w-12">
                  TT
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700 w-28">
                  Ma
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">
                  Quy tac kiem tra
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700 w-28">
                  Ket qua
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">
                  Chi tiet
                </th>
                <th className="px-4 py-3 text-right font-semibold text-gray-700 w-36">
                  Chenh lech
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredResults.map((result, index) => {
                const colors = severityColor(result.severity);
                const Icon = SEVERITY_ICONS[result.severity] || CheckCircle2;

                return (
                  <tr
                    key={result.rule_id + index}
                    className={`border-b border-gray-100 ${colors.bg} hover:brightness-95 transition-all`}
                  >
                    <td className="px-4 py-3 text-gray-400 text-xs">
                      {index + 1}
                    </td>
                    <td className="px-4 py-3">
                      <code className="text-xs font-mono text-gray-600 bg-gray-100 px-1.5 py-0.5 rounded">
                        {result.rule_id}
                      </code>
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-700">
                      {result.rule_name}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${colors.badge}`}
                      >
                        <Icon className="w-3 h-3" />
                        {severityLabel(result.severity)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs max-w-xs truncate">
                      {result.message}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums">
                      {result.difference !== 0 && result.difference != null ? (
                        <span
                          className={`text-xs font-medium ${
                            Math.abs(result.difference) > 0
                              ? "text-red-600"
                              : "text-gray-400"
                          }`}
                        >
                          {formatVND(result.difference)}
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">0</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredResults.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <CheckCircle2 className="w-10 h-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">Khong tim thay ket qua phu hop.</p>
          </div>
        )}
      </div>

      {/* Pass rate bar */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">
          Ty le dat
        </h3>
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          {details.length > 0 && (
            <div className="h-full flex">
              <div
                className="bg-emerald-500 h-full"
                style={{
                  width: `${(counts.ok / details.length) * 100}%`,
                }}
              />
              <div
                className="bg-amber-400 h-full"
                style={{
                  width: `${(counts.warning / details.length) * 100}%`,
                }}
              />
              <div
                className="bg-red-500 h-full"
                style={{
                  width: `${(counts.error / details.length) * 100}%`,
                }}
              />
              <div
                className="bg-rose-700 h-full"
                style={{
                  width: `${(counts.critical / details.length) * 100}%`,
                }}
              />
            </div>
          )}
        </div>
        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 bg-emerald-500 rounded-full" />
            Dat ({counts.ok})
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 bg-amber-400 rounded-full" />
            Canh bao ({counts.warning})
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 bg-red-500 rounded-full" />
            Loi ({counts.error})
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 bg-rose-700 rounded-full" />
            Nghiem trong ({counts.critical})
          </span>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ label, value, color, active, onClick }) {
  const colorMap = {
    gray: active
      ? "bg-gray-200 border-gray-400 text-gray-800"
      : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100",
    emerald: active
      ? "bg-emerald-100 border-emerald-400 text-emerald-800"
      : "bg-emerald-50 border-emerald-200 text-emerald-600 hover:bg-emerald-100",
    amber: active
      ? "bg-amber-100 border-amber-400 text-amber-800"
      : "bg-amber-50 border-amber-200 text-amber-600 hover:bg-amber-100",
    red: active
      ? "bg-red-100 border-red-400 text-red-800"
      : "bg-red-50 border-red-200 text-red-600 hover:bg-red-100",
    rose: active
      ? "bg-rose-100 border-rose-400 text-rose-800"
      : "bg-rose-50 border-rose-200 text-rose-600 hover:bg-rose-100",
  };

  return (
    <button
      onClick={onClick}
      className={`rounded-xl border p-3 text-center transition-all cursor-pointer ${colorMap[color]}`}
    >
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs font-medium mt-0.5">{label}</p>
    </button>
  );
}
