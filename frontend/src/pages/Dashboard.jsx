import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Building2,
  CalendarDays,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  BarChart3,
  BookOpen,
  AlertOctagon,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import { formatVND } from "../utils/formatters";
import ExportButton from "../components/ExportButton";
import BalanceSheet from "../components/BalanceSheet";
import IncomeStatement from "../components/IncomeStatement";
import CashFlowChart from "../components/CashFlowChart";

export default function Dashboard({ data }) {
  const [activeTab, setActiveTab] = useState("overview");
  const { company, validation, anomalies, ratios, reports, circular } = data;

  // Health score
  const healthScore =
    validation.total_checks > 0
      ? Math.round((validation.passed / validation.total_checks) * 100)
      : 0;

  // Risk counts
  const riskCounts = {
    critical: anomalies.filter((a) => a.risk_level === "critical").length,
    high: anomalies.filter((a) => a.risk_level === "high").length,
    medium: anomalies.filter((a) => a.risk_level === "medium").length,
    low: anomalies.filter((a) => a.risk_level === "low").length,
  };

  // Key financial figures
  const cdkt = reports?.cdkt?.so_cuoi_nam || {};
  const kqhdkd = reports?.kqhdkd?.nam_nay || {};
  const tongTS = cdkt.ct300 || 0;
  const tongNV = cdkt.ct600 || 0;
  const doanhThu = kqhdkd.ct10 || kqhdkd.ct01 || 0;
  const lnst = kqhdkd.ct60 || 0;

  const tabs = [
    { id: "overview", label: "Tong quan" },
    { id: "cdkt", label: "Can doi KT" },
    { id: "kqhdkd", label: "Ket qua HDKD" },
    { id: "lctt", label: "Luu chuyen TT" },
  ];

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Company Info + Export */}
      <div className="flex flex-col sm:flex-row gap-4 items-start justify-between">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex-1 w-full sm:w-auto">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center shrink-0">
              <Building2 className="w-6 h-6 text-indigo-600" />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl font-bold text-gray-900 truncate">
                {company?.ten_dn || "Doanh nghiep"}
              </h1>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5 text-sm text-gray-500">
                <span>MST: {company?.mst || "—"}</span>
                <span className="hidden sm:inline text-gray-300">|</span>
                <span className="flex items-center gap-1">
                  <CalendarDays className="w-3.5 h-3.5" />
                  {company?.tu_ngay || "—"} den {company?.den_ngay || "—"}
                </span>
                <span className="inline-flex items-center px-2 py-0.5 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-full">
                  {circular || "TT133"}
                </span>
              </div>
              {company?.dia_chi && (
                <p className="text-xs text-gray-400 mt-1 truncate">
                  {company.dia_chi}
                </p>
              )}
            </div>
          </div>
        </div>
        <ExportButton analysisData={data} />
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <ScoreCard
          icon={ShieldCheck}
          title="Health Score"
          value={`${healthScore}%`}
          subtitle={`${validation.passed}/${validation.total_checks} dieu kien dat`}
          color={
            healthScore > 80
              ? "emerald"
              : healthScore > 50
                ? "amber"
                : "red"
          }
        />
        <ScoreCard
          icon={CheckCircle2}
          title="Doi chieu dung"
          value={`${validation.passed}`}
          subtitle={`/ ${validation.total_checks} quy tac`}
          color="blue"
          link="/cross-check"
        />
        <ScoreCard
          icon={AlertTriangle}
          title="Canh bao"
          value={`${riskCounts.critical + riskCounts.high}`}
          subtitle={`${riskCounts.medium} muc trung binh`}
          color={riskCounts.critical > 0 ? "red" : riskCounts.high > 0 ? "orange" : "emerald"}
          link="/anomalies"
        />
        <ScoreCard
          icon={BarChart3}
          title="Chi so TC"
          value={`${ratios.length}`}
          subtitle="chi so da tinh"
          color="purple"
          link="/ratios"
        />
      </div>

      {/* Quick Alerts */}
      {(riskCounts.critical > 0 || riskCounts.high > 0) && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertOctagon className="w-5 h-5 text-red-600" />
            <h3 className="font-semibold text-red-800 text-sm">
              Phat hien van de nghiem trong
            </h3>
          </div>
          <div className="space-y-1.5">
            {anomalies
              .filter(
                (a) =>
                  a.risk_level === "critical" || a.risk_level === "high"
              )
              .slice(0, 3)
              .map((a, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 text-sm text-red-700"
                >
                  <span className="w-1.5 h-1.5 bg-red-500 rounded-full shrink-0" />
                  {a.title}
                </div>
              ))}
          </div>
          <Link
            to="/anomalies"
            className="inline-flex items-center gap-1 mt-2 text-xs font-medium text-red-600 hover:text-red-800"
          >
            Xem tat ca canh bao
            <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
      )}

      {/* Key Financial Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Tong tai san"
          value={formatVND(tongTS)}
          change={null}
        />
        <MetricCard
          label="Doanh thu thuan"
          value={formatVND(doanhThu)}
          change={null}
        />
        <MetricCard
          label="Loi nhuan sau thue"
          value={formatVND(lnst)}
          change={lnst >= 0 ? "positive" : "negative"}
        />
        <MetricCard
          label="Von chu so huu"
          value={formatVND(cdkt.ct500)}
          change={null}
        />
      </div>

      {/* Tab navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-6 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors
                ${
                  activeTab === tab.id
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div>
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quick links */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-base font-semibold text-gray-800 mb-4">
                Phan tich chi tiet
              </h3>
              <div className="space-y-2">
                <QuickLink
                  to="/cross-check"
                  icon={CheckCircle2}
                  label="Doi chieu cheo 4 bao cao"
                  count={`${validation.passed}/${validation.total_checks}`}
                  color="blue"
                />
                <QuickLink
                  to="/journals"
                  icon={BookOpen}
                  label="But toan tai tao"
                  count={`${data.journals?.length || 0} but toan`}
                  color="emerald"
                />
                <QuickLink
                  to="/anomalies"
                  icon={AlertTriangle}
                  label="Canh bao bat thuong"
                  count={`${anomalies.length} phat hien`}
                  color="amber"
                />
                <QuickLink
                  to="/ratios"
                  icon={BarChart3}
                  label="Chi so tai chinh"
                  count={`${ratios.length} chi so`}
                  color="purple"
                />
              </div>
            </div>

            {/* Validation summary */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-base font-semibold text-gray-800 mb-4">
                Ket qua doi chieu
              </h3>
              <div className="space-y-3">
                {validation.details?.slice(0, 6).map((item, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span
                      className={`w-2 h-2 rounded-full shrink-0 ${
                        item.severity === "ok"
                          ? "bg-emerald-500"
                          : item.severity === "warning"
                            ? "bg-amber-500"
                            : "bg-red-500"
                      }`}
                    />
                    <span className="text-gray-600 truncate flex-1">
                      {item.rule_name}
                    </span>
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        item.severity === "ok"
                          ? "bg-emerald-100 text-emerald-700"
                          : item.severity === "warning"
                            ? "bg-amber-100 text-amber-700"
                            : "bg-red-100 text-red-700"
                      }`}
                    >
                      {item.severity === "ok"
                        ? "Dat"
                        : item.severity === "warning"
                          ? "Canh bao"
                          : "Loi"}
                    </span>
                  </div>
                ))}
                {validation.details?.length > 6 && (
                  <Link
                    to="/cross-check"
                    className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    Xem tat ca {validation.details.length} quy tac...
                  </Link>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === "cdkt" && <BalanceSheet cdktData={reports?.cdkt} />}

        {activeTab === "kqhdkd" && (
          <IncomeStatement kqhdkdData={reports?.kqhdkd} />
        )}

        {activeTab === "lctt" && <CashFlowChart lcttData={reports?.lctt} />}
      </div>
    </div>
  );
}

function ScoreCard({ icon: Icon, title, value, subtitle, color, link }) {
  const colorMap = {
    emerald: "bg-emerald-50 text-emerald-700 border-emerald-200",
    blue: "bg-blue-50 text-blue-700 border-blue-200",
    red: "bg-red-50 text-red-700 border-red-200",
    orange: "bg-orange-50 text-orange-700 border-orange-200",
    amber: "bg-amber-50 text-amber-700 border-amber-200",
    purple: "bg-purple-50 text-purple-700 border-purple-200",
  };

  const iconColorMap = {
    emerald: "text-emerald-600",
    blue: "text-blue-600",
    red: "text-red-600",
    orange: "text-orange-600",
    amber: "text-amber-600",
    purple: "text-purple-600",
  };

  const Wrapper = link ? Link : "div";
  const wrapperProps = link ? { to: link } : {};

  return (
    <Wrapper
      {...wrapperProps}
      className={`rounded-xl border p-4 ${colorMap[color]} ${link ? "hover:shadow-md transition-shadow cursor-pointer" : ""}`}
    >
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${iconColorMap[color]}`} />
        <span className="text-xs font-medium opacity-80">{title}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs opacity-70 mt-0.5">{subtitle}</p>
    </Wrapper>
  );
}

function MetricCard({ label, value, change }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-lg font-semibold text-gray-800 tabular-nums">
        {value}
      </p>
      {change && (
        <div className="flex items-center gap-1 mt-1">
          {change === "positive" ? (
            <TrendingUp className="w-3 h-3 text-emerald-500" />
          ) : change === "negative" ? (
            <TrendingDown className="w-3 h-3 text-red-500" />
          ) : (
            <Minus className="w-3 h-3 text-gray-400" />
          )}
        </div>
      )}
    </div>
  );
}

function QuickLink({ to, icon: Icon, label, count, color }) {
  const iconColors = {
    blue: "text-blue-600 bg-blue-100",
    emerald: "text-emerald-600 bg-emerald-100",
    amber: "text-amber-600 bg-amber-100",
    purple: "text-purple-600 bg-purple-100",
  };

  return (
    <Link
      to={to}
      className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors group"
    >
      <div
        className={`w-9 h-9 rounded-lg flex items-center justify-center ${iconColors[color]}`}
      >
        <Icon className="w-4 h-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
          {label}
        </p>
      </div>
      <span className="text-xs text-gray-400 font-medium">{count}</span>
      <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-gray-500" />
    </Link>
  );
}
