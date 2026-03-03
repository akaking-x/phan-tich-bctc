import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";
import { formatVND } from "../utils/formatters";

const LCTT_ITEMS = {
  operating: [
    { code: "ct01", name: "Tien thu ban hang, CCDV" },
    { code: "ct02", name: "Tien chi tra NCC" },
    { code: "ct03", name: "Tien chi tra NLD" },
    { code: "ct04", name: "Tien chi tra lai vay" },
    { code: "ct05", name: "Tien chi nop thue TNDN" },
    { code: "ct06", name: "Tien thu khac tu HDKD" },
    { code: "ct07", name: "Tien chi khac cho HDKD" },
  ],
  investing: [
    { code: "ct21", name: "Tien chi mua TSCD" },
    { code: "ct22", name: "Tien thu thanh ly TSCD" },
    { code: "ct23", name: "Tien chi cho vay" },
    { code: "ct24", name: "Tien thu hoi cho vay" },
    { code: "ct25", name: "Tien thu lai cho vay, co tuc" },
  ],
  financing: [
    { code: "ct31", name: "Tien thu phat hanh CP" },
    { code: "ct32", name: "Tien chi tra von gop" },
    { code: "ct33", name: "Tien thu tu di vay" },
    { code: "ct34", name: "Tien chi tra no goc vay" },
    { code: "ct35", name: "Tien chi tra no thue TC" },
  ],
};

const FLOW_COLORS = {
  operating: "#6366f1",
  investing: "#f59e0b",
  financing: "#10b981",
};

const FLOW_LABELS = {
  operating: "Hoat dong KD",
  investing: "Hoat dong DT",
  financing: "Hoat dong TC",
};

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0].payload;
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm">
      <p className="font-medium text-gray-800 mb-1">{data.name}</p>
      <p className={`tabular-nums ${data.value < 0 ? "text-red-600" : "text-emerald-600"}`}>
        {formatVND(data.value)}
      </p>
    </div>
  );
}

export default function CashFlowChart({ lcttData }) {
  if (!lcttData || !lcttData.nam_nay) return null;

  const namNay = lcttData.nam_nay;

  // Stacked bar chart data for 3 flow types
  const summaryData = [
    {
      name: "HDKD",
      fullName: "Hoat dong kinh doanh",
      value: namNay.ct20 || 0,
      color: FLOW_COLORS.operating,
    },
    {
      name: "HDDT",
      fullName: "Hoat dong dau tu",
      value: namNay.ct30 || 0,
      color: FLOW_COLORS.investing,
    },
    {
      name: "HDTC",
      fullName: "Hoat dong tai chinh",
      value: namNay.ct40 || 0,
      color: FLOW_COLORS.financing,
    },
    {
      name: "Tang/Giam",
      fullName: "Tang/giam tien thuan",
      value: namNay.ct50 || 0,
      color: "#8b5cf6",
    },
  ];

  // Waterfall data - detailed breakdown
  const waterfallData = [];
  for (const [flowType, items] of Object.entries(LCTT_ITEMS)) {
    for (const item of items) {
      const val = namNay[item.code];
      if (val && val !== 0) {
        waterfallData.push({
          name: item.name,
          value: val,
          flowType,
          color: val >= 0 ? "#10b981" : "#ef4444",
        });
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Summary Bar Chart */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
        <h3 className="text-base font-semibold text-gray-800 mb-4">
          Tong hop dong tien theo hoat dong
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={summaryData} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#6b7280" }} />
            <YAxis
              tick={{ fontSize: 11, fill: "#6b7280" }}
              tickFormatter={(v) => {
                if (Math.abs(v) >= 1e9) return (v / 1e9).toFixed(1) + " ty";
                if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(0) + " tr";
                return v.toLocaleString("vi-VN");
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#9ca3af" />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={60}>
              {summaryData.map((entry, index) => (
                <Cell key={index} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        {/* Legend */}
        <div className="flex items-center justify-center gap-6 mt-2">
          {Object.entries(FLOW_LABELS).map(([key, label]) => (
            <div key={key} className="flex items-center gap-2 text-xs text-gray-600">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: FLOW_COLORS[key] }}
              />
              {label}
            </div>
          ))}
        </div>
      </div>

      {/* Waterfall Breakdown Chart */}
      {waterfallData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="text-base font-semibold text-gray-800 mb-4">
            Chi tiet dong tien
          </h3>
          <ResponsiveContainer width="100%" height={Math.max(300, waterfallData.length * 36)}>
            <BarChart
              data={waterfallData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 160, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={false} />
              <XAxis
                type="number"
                tick={{ fontSize: 11, fill: "#6b7280" }}
                tickFormatter={(v) => {
                  if (Math.abs(v) >= 1e9) return (v / 1e9).toFixed(1) + " ty";
                  if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(0) + " tr";
                  return v.toLocaleString("vi-VN");
                }}
              />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontSize: 11, fill: "#374151" }}
                width={150}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine x={0} stroke="#9ca3af" />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={24}>
                {waterfallData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Cash summary */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
        <h3 className="text-base font-semibold text-gray-800 mb-3">
          Bien dong tien
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-xs text-gray-500 mb-1">Tien dau ky</p>
            <p className="text-lg font-semibold text-gray-800 tabular-nums">
              {formatVND(namNay.ct60)}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-xs text-gray-500 mb-1">Tang/giam trong ky</p>
            <p
              className={`text-lg font-semibold tabular-nums ${
                (namNay.ct50 || 0) < 0 ? "text-red-600" : "text-emerald-600"
              }`}
            >
              {formatVND(namNay.ct50)}
            </p>
          </div>
          <div className="bg-indigo-50 rounded-lg p-4">
            <p className="text-xs text-indigo-600 mb-1">Tien cuoi ky</p>
            <p className="text-lg font-semibold text-indigo-700 tabular-nums">
              {formatVND(namNay.ct70)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
