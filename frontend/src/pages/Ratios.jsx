import { useState, useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";
import {
  Droplets,
  TrendingUp,
  Scale,
  Zap,
  Info,
} from "lucide-react";
import { formatPercent, formatRatio, categoryLabel } from "../utils/formatters";

const CATEGORY_CONFIG = {
  liquidity: {
    label: "Thanh khoan",
    icon: Droplets,
    color: "#3b82f6",
    bgLight: "bg-blue-50",
    textColor: "text-blue-700",
    borderColor: "border-blue-200",
  },
  profitability: {
    label: "Sinh loi",
    icon: TrendingUp,
    color: "#10b981",
    bgLight: "bg-emerald-50",
    textColor: "text-emerald-700",
    borderColor: "border-emerald-200",
  },
  leverage: {
    label: "Don bay",
    icon: Scale,
    color: "#f59e0b",
    bgLight: "bg-amber-50",
    textColor: "text-amber-700",
    borderColor: "border-amber-200",
  },
  efficiency: {
    label: "Hieu suat",
    icon: Zap,
    color: "#8b5cf6",
    bgLight: "bg-purple-50",
    textColor: "text-purple-700",
    borderColor: "border-purple-200",
  },
};

function getValueColor(interpretation) {
  if (!interpretation) return "text-gray-600";
  const lower = interpretation.toLowerCase();
  if (lower.includes("tot") || lower.includes("an toan")) return "text-emerald-600";
  if (lower.includes("chap nhan")) return "text-amber-600";
  if (lower.includes("can cai thien") || lower.includes("n/a"))
    return "text-red-600";
  return "text-gray-800";
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm max-w-xs">
      <p className="font-semibold text-gray-800">{d.name}</p>
      <p className="text-xs text-gray-500 mt-0.5">{d.name_en}</p>
      <div className="mt-2 space-y-1">
        <p className="text-gray-700">
          Gia tri: <strong>{d.displayValue}</strong> {d.unit}
        </p>
        <p className="text-gray-500 text-xs">Tham chieu: {d.benchmark}</p>
        <p className={`text-xs font-medium ${getValueColor(d.interpretation)}`}>
          {d.interpretation}
        </p>
      </div>
    </div>
  );
}

export default function Ratios({ data }) {
  const ratios = data?.ratios || [];
  const [activeCategory, setActiveCategory] = useState("all");

  // Group ratios by category
  const groupedRatios = useMemo(() => {
    const groups = {};
    ratios.forEach((r) => {
      if (!groups[r.category]) groups[r.category] = [];
      groups[r.category].push(r);
    });
    return groups;
  }, [ratios]);

  const displayCategories =
    activeCategory === "all"
      ? Object.keys(groupedRatios)
      : [activeCategory];

  // Chart data
  const chartData = useMemo(() => {
    const filteredRatios =
      activeCategory === "all"
        ? ratios
        : ratios.filter((r) => r.category === activeCategory);

    return filteredRatios
      .filter((r) => r.value !== null)
      .map((r) => ({
        name: r.name,
        name_en: r.name_en,
        value: r.value,
        displayValue: r.unit === "%" ? formatPercent(r.value) : formatRatio(r.value),
        unit: r.unit,
        benchmark: r.benchmark,
        interpretation: r.interpretation,
        color: CATEGORY_CONFIG[r.category]?.color || "#6b7280",
      }));
  }, [ratios, activeCategory]);

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Category tabs */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveCategory("all")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
              ${
                activeCategory === "all"
                  ? "bg-indigo-100 text-indigo-700"
                  : "text-gray-500 hover:bg-gray-100"
              }`}
          >
            Tat ca ({ratios.length})
          </button>
          {Object.entries(CATEGORY_CONFIG).map(([key, config]) => {
            const count = groupedRatios[key]?.length || 0;
            if (count === 0) return null;
            const Icon = config.icon;
            return (
              <button
                key={key}
                onClick={() => setActiveCategory(key)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                  ${
                    activeCategory === key
                      ? `${config.bgLight} ${config.textColor}`
                      : "text-gray-500 hover:bg-gray-100"
                  }`}
              >
                <Icon className="w-4 h-4" />
                {config.label} ({count})
              </button>
            );
          })}
        </div>
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-base font-semibold text-gray-800 mb-4">
            Bieu do chi so
          </h3>
          <ResponsiveContainer width="100%" height={Math.max(250, chartData.length * 50)}>
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 160, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: "#6b7280" }} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontSize: 11, fill: "#374151" }}
                width={150}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine x={0} stroke="#9ca3af" />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={28}>
                {chartData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Ratio cards by category */}
      {displayCategories.map((cat) => {
        const config = CATEGORY_CONFIG[cat];
        const items = groupedRatios[cat] || [];
        if (items.length === 0) return null;
        const Icon = config?.icon || Info;

        return (
          <div
            key={cat}
            className={`bg-white rounded-xl border ${config?.borderColor || "border-gray-200"} overflow-hidden`}
          >
            {/* Category header */}
            <div
              className={`px-5 py-3 ${config?.bgLight || "bg-gray-50"} border-b ${config?.borderColor || "border-gray-200"} flex items-center gap-2`}
            >
              <Icon
                className={`w-5 h-5 ${config?.textColor || "text-gray-600"}`}
              />
              <h3
                className={`text-base font-semibold ${config?.textColor || "text-gray-800"}`}
              >
                {config?.label || cat}
              </h3>
            </div>

            {/* Ratio items */}
            <div className="divide-y divide-gray-100">
              {items.map((ratio) => (
                <div
                  key={ratio.code}
                  className="px-5 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                    {/* Name */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <code className="text-[10px] font-mono text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                          {ratio.code}
                        </code>
                        <h4 className="text-sm font-medium text-gray-800">
                          {ratio.name}
                        </h4>
                      </div>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {ratio.name_en}
                      </p>
                    </div>

                    {/* Value */}
                    <div className="text-right sm:w-32">
                      <p
                        className={`text-xl font-bold tabular-nums ${getValueColor(ratio.interpretation)}`}
                      >
                        {ratio.value !== null
                          ? ratio.unit === "%"
                            ? formatPercent(ratio.value)
                            : formatRatio(ratio.value)
                          : "N/A"}
                      </p>
                      <p className="text-xs text-gray-400">{ratio.unit}</p>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <div className="bg-gray-50 rounded-lg px-3 py-2">
                      <p className="text-[11px] text-gray-400 mb-0.5">
                        Tham chieu
                      </p>
                      <p className="text-xs text-gray-600">
                        {ratio.benchmark}
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg px-3 py-2">
                      <p className="text-[11px] text-gray-400 mb-0.5">
                        Nhan xet
                      </p>
                      <p
                        className={`text-xs font-medium ${getValueColor(ratio.interpretation)}`}
                      >
                        {ratio.interpretation}
                      </p>
                    </div>
                  </div>

                  {/* Visual gauge bar */}
                  {ratio.value !== null && ratio.unit === "lan" && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{
                            width: `${Math.min(Math.max(ratio.value / 3, 0) * 100, 100)}%`,
                            backgroundColor: config?.color || "#6b7280",
                          }}
                        />
                      </div>
                    </div>
                  )}
                  {ratio.value !== null && ratio.unit === "%" && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{
                            width: `${Math.min(Math.abs(ratio.value), 100)}%`,
                            backgroundColor:
                              ratio.value >= 0
                                ? config?.color || "#6b7280"
                                : "#ef4444",
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {ratios.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <Info className="w-10 h-10 mx-auto mb-2 opacity-30" />
          <p className="text-sm">
            Khong co du lieu de tinh toan chi so tai chinh.
          </p>
        </div>
      )}
    </div>
  );
}
