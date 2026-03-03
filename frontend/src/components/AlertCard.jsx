import {
  AlertTriangle,
  AlertOctagon,
  Info,
  ShieldAlert,
  Lightbulb,
} from "lucide-react";
import { riskColor, riskLabel } from "../utils/formatters";

const RISK_ICONS = {
  low: Info,
  medium: AlertTriangle,
  high: ShieldAlert,
  critical: AlertOctagon,
};

export default function AlertCard({ anomaly }) {
  const { code, title, description, risk_level, category, suggestion } =
    anomaly;
  const colors = riskColor(risk_level);
  const Icon = RISK_ICONS[risk_level] || AlertTriangle;

  const categoryLabels = {
    cash: "Tien mat",
    tax: "Thue",
    structure: "Cau truc",
    activity: "Hoat dong",
  };

  return (
    <div
      className={`rounded-xl border ${colors.border} ${colors.bg} p-5 transition-shadow hover:shadow-md`}
    >
      {/* Header */}
      <div className="flex items-start gap-3">
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${colors.badge}`}
        >
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="text-xs font-mono text-gray-400">{code}</span>
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold ${colors.badge}`}
            >
              {riskLabel(risk_level)}
            </span>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-gray-100 text-gray-600">
              {categoryLabels[category] || category}
            </span>
          </div>
          <h3 className={`text-sm font-semibold ${colors.text}`}>{title}</h3>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 mt-3 leading-relaxed">
        {description}
      </p>

      {/* Suggestion */}
      {suggestion && (
        <div className="mt-3 flex items-start gap-2 bg-white/60 rounded-lg px-3 py-2.5 border border-gray-100">
          <Lightbulb className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
          <p className="text-xs text-gray-600 leading-relaxed">{suggestion}</p>
        </div>
      )}
    </div>
  );
}
