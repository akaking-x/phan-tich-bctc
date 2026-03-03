import { useState, useMemo } from "react";
import {
  AlertTriangle,
  AlertOctagon,
  ShieldAlert,
  Info,
  Filter,
  ShieldCheck,
} from "lucide-react";
import AlertCard from "../components/AlertCard";
import { riskColor, riskLabel } from "../utils/formatters";

const CATEGORY_OPTIONS = [
  { value: "all", label: "Tat ca danh muc" },
  { value: "cash", label: "Tien mat" },
  { value: "tax", label: "Thue" },
  { value: "structure", label: "Cau truc" },
  { value: "activity", label: "Hoat dong" },
];

const RISK_OPTIONS = [
  { value: "all", label: "Tat ca muc do" },
  { value: "critical", label: "Nghiem trong" },
  { value: "high", label: "Cao" },
  { value: "medium", label: "Trung binh" },
  { value: "low", label: "Thap" },
];

const RISK_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };

export default function Anomalies({ data }) {
  const anomalies = data?.anomalies || [];
  const [filterCategory, setFilterCategory] = useState("all");
  const [filterRisk, setFilterRisk] = useState("all");

  // Risk counts
  const riskCounts = useMemo(() => {
    const c = { critical: 0, high: 0, medium: 0, low: 0 };
    anomalies.forEach((a) => {
      c[a.risk_level] = (c[a.risk_level] || 0) + 1;
    });
    return c;
  }, [anomalies]);

  // Category counts
  const categoryCounts = useMemo(() => {
    const c = {};
    anomalies.forEach((a) => {
      c[a.category] = (c[a.category] || 0) + 1;
    });
    return c;
  }, [anomalies]);

  // Filter
  const filteredAnomalies = useMemo(() => {
    let results = [...anomalies];

    if (filterCategory !== "all") {
      results = results.filter((a) => a.category === filterCategory);
    }

    if (filterRisk !== "all") {
      results = results.filter((a) => a.risk_level === filterRisk);
    }

    // Sort by risk level
    results.sort(
      (a, b) =>
        (RISK_ORDER[a.risk_level] ?? 99) - (RISK_ORDER[b.risk_level] ?? 99)
    );

    return results;
  }, [anomalies, filterCategory, filterRisk]);

  if (anomalies.length === 0) {
    return (
      <div className="p-4 lg:p-6">
        <div className="text-center py-20">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-100 rounded-2xl mb-4">
            <ShieldCheck className="w-8 h-8 text-emerald-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-800">
            Khong phat hien bat thuong
          </h2>
          <p className="text-gray-500 mt-2 text-sm max-w-md mx-auto">
            He thong da kiem tra va khong phat hien dieu bat thuong nao trong
            Bao cao Tai chinh cua doanh nghiep.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Risk summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <RiskSummaryCard
          icon={AlertOctagon}
          label="Nghiem trong"
          count={riskCounts.critical}
          color="red"
          active={filterRisk === "critical"}
          onClick={() =>
            setFilterRisk(filterRisk === "critical" ? "all" : "critical")
          }
        />
        <RiskSummaryCard
          icon={ShieldAlert}
          label="Cao"
          count={riskCounts.high}
          color="orange"
          active={filterRisk === "high"}
          onClick={() =>
            setFilterRisk(filterRisk === "high" ? "all" : "high")
          }
        />
        <RiskSummaryCard
          icon={AlertTriangle}
          label="Trung binh"
          count={riskCounts.medium}
          color="amber"
          active={filterRisk === "medium"}
          onClick={() =>
            setFilterRisk(filterRisk === "medium" ? "all" : "medium")
          }
        />
        <RiskSummaryCard
          icon={Info}
          label="Thap"
          count={riskCounts.low}
          color="blue"
          active={filterRisk === "low"}
          onClick={() =>
            setFilterRisk(filterRisk === "low" ? "all" : "low")
          }
        />
      </div>

      {/* Category filter */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex flex-wrap items-center gap-3">
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-500">Danh muc:</span>
          {CATEGORY_OPTIONS.map((opt) => {
            const isActive = filterCategory === opt.value;
            const count =
              opt.value === "all"
                ? anomalies.length
                : categoryCounts[opt.value] || 0;
            return (
              <button
                key={opt.value}
                onClick={() => setFilterCategory(opt.value)}
                className={`text-sm px-3 py-1.5 rounded-lg font-medium transition-colors
                  ${
                    isActive
                      ? "bg-indigo-100 text-indigo-700"
                      : "text-gray-500 hover:bg-gray-100"
                  }`}
              >
                {opt.label}
                {count > 0 && (
                  <span className="ml-1.5 text-xs opacity-60">({count})</span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Anomaly cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredAnomalies.map((anomaly, index) => (
          <AlertCard key={anomaly.code + index} anomaly={anomaly} />
        ))}
      </div>

      {filteredAnomalies.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <AlertTriangle className="w-10 h-10 mx-auto mb-2 opacity-30" />
          <p className="text-sm">
            Khong co canh bao nao phu hop voi bo loc hien tai.
          </p>
        </div>
      )}
    </div>
  );
}

function RiskSummaryCard({ icon: Icon, label, count, color, active, onClick }) {
  const colorMap = {
    red: active
      ? "bg-red-100 border-red-400 text-red-800"
      : "bg-red-50 border-red-200 text-red-600 hover:bg-red-100",
    orange: active
      ? "bg-orange-100 border-orange-400 text-orange-800"
      : "bg-orange-50 border-orange-200 text-orange-600 hover:bg-orange-100",
    amber: active
      ? "bg-amber-100 border-amber-400 text-amber-800"
      : "bg-amber-50 border-amber-200 text-amber-600 hover:bg-amber-100",
    blue: active
      ? "bg-blue-100 border-blue-400 text-blue-800"
      : "bg-blue-50 border-blue-200 text-blue-600 hover:bg-blue-100",
  };

  return (
    <button
      onClick={onClick}
      className={`rounded-xl border p-4 text-center transition-all cursor-pointer ${colorMap[color]}`}
    >
      <Icon className="w-5 h-5 mx-auto mb-1" />
      <p className="text-2xl font-bold">{count}</p>
      <p className="text-xs font-medium">{label}</p>
    </button>
  );
}
