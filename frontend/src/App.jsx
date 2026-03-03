import { useState } from "react";
import { Routes, Route, Link, useLocation, Navigate } from "react-router-dom";
import {
  UploadCloud,
  LayoutDashboard,
  CheckCircle2,
  BookOpen,
  AlertTriangle,
  BarChart3,
  FileSpreadsheet,
  Menu,
  X,
  ChevronRight,
} from "lucide-react";
import Upload from "./pages/Upload";
import Dashboard from "./pages/Dashboard";
import CrossCheck from "./pages/CrossCheck";
import JournalView from "./pages/JournalView";
import Anomalies from "./pages/Anomalies";
import Ratios from "./pages/Ratios";

const NAV_ITEMS = [
  { path: "/", label: "Tai len XML", icon: UploadCloud, requiresData: false },
  {
    path: "/dashboard",
    label: "Tong quan",
    icon: LayoutDashboard,
    requiresData: true,
  },
  {
    path: "/cross-check",
    label: "Doi chieu cheo",
    icon: CheckCircle2,
    requiresData: true,
  },
  {
    path: "/journals",
    label: "But toan tai tao",
    icon: BookOpen,
    requiresData: true,
  },
  {
    path: "/anomalies",
    label: "Canh bao bat thuong",
    icon: AlertTriangle,
    requiresData: true,
  },
  {
    path: "/ratios",
    label: "Chi so tai chinh",
    icon: BarChart3,
    requiresData: true,
  },
];

export default function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const handleUploadSuccess = (data) => {
    setAnalysisData(data);
  };

  const handleNewAnalysis = () => {
    setAnalysisData(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200
          transform transition-transform duration-200 ease-in-out flex flex-col
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center gap-3 px-5 border-b border-gray-200 shrink-0">
          <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center">
            <FileSpreadsheet className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-gray-900 leading-tight">
              BCTC Analyzer
            </h1>
            <p className="text-[11px] text-gray-400 leading-tight">
              Phan tich Bao cao Tai chinh
            </p>
          </div>
          <button
            className="ml-auto lg:hidden text-gray-400 hover:text-gray-600"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3">
          <ul className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              const isDisabled = item.requiresData && !analysisData;

              return (
                <li key={item.path}>
                  {isDisabled ? (
                    <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 cursor-not-allowed text-sm">
                      <Icon className="w-[18px] h-[18px]" />
                      <span>{item.label}</span>
                    </div>
                  ) : (
                    <Link
                      to={item.path}
                      onClick={() => setSidebarOpen(false)}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                        ${
                          isActive
                            ? "bg-indigo-50 text-indigo-700"
                            : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                        }`}
                    >
                      <Icon
                        className={`w-[18px] h-[18px] ${isActive ? "text-indigo-600" : ""}`}
                      />
                      <span>{item.label}</span>
                      {isActive && (
                        <ChevronRight className="w-4 h-4 ml-auto text-indigo-400" />
                      )}
                    </Link>
                  )}
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Company info footer */}
        {analysisData && (
          <div className="border-t border-gray-200 p-4 shrink-0">
            <div className="text-xs text-gray-400 mb-1">Doanh nghiep</div>
            <div className="text-sm font-medium text-gray-800 truncate">
              {analysisData.company?.ten_dn || "—"}
            </div>
            <div className="text-xs text-gray-400 mt-0.5">
              MST: {analysisData.company?.mst || "—"}
            </div>
            <button
              onClick={handleNewAnalysis}
              className="mt-3 w-full text-xs text-indigo-600 hover:text-indigo-800
                font-medium py-1.5 border border-indigo-200 rounded-md hover:bg-indigo-50 transition-colors"
            >
              Phan tich file moi
            </button>
          </div>
        )}
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top header bar */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 lg:px-6 shrink-0">
          <button
            className="lg:hidden mr-3 text-gray-500 hover:text-gray-700"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-6 h-6" />
          </button>
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-gray-800">
              {NAV_ITEMS.find((n) => n.path === location.pathname)?.label ||
                "BCTC Analyzer"}
            </h2>
          </div>
          {analysisData && (
            <div className="hidden sm:flex items-center gap-2 text-sm text-gray-500">
              <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full" />
              Da phan tich
            </div>
          )}
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route
              path="/"
              element={
                <Upload
                  onUploadSuccess={handleUploadSuccess}
                  hasData={!!analysisData}
                />
              }
            />
            <Route
              path="/dashboard"
              element={
                analysisData ? (
                  <Dashboard data={analysisData} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/cross-check"
              element={
                analysisData ? (
                  <CrossCheck data={analysisData} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/journals"
              element={
                analysisData ? (
                  <JournalView data={analysisData} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/anomalies"
              element={
                analysisData ? (
                  <Anomalies data={analysisData} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="/ratios"
              element={
                analysisData ? (
                  <Ratios data={analysisData} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
          </Routes>
        </main>
      </div>
    </div>
  );
}
