import { useState, useMemo } from "react";
import {
  BookOpen,
  Filter,
  Search,
  ArrowUpDown,
  ChevronDown,
  ChevronUp,
  HelpCircle,
} from "lucide-react";
import { formatVND, categoryLabel } from "../utils/formatters";

const CATEGORY_OPTIONS = [
  { value: "all", label: "Tat ca loai" },
  { value: "operating", label: "Hoat dong kinh doanh" },
  { value: "investing", label: "Hoat dong dau tu" },
  { value: "financing", label: "Hoat dong tai chinh" },
  { value: "unknown", label: "Chua xac dinh" },
];

const CONFIDENCE_OPTIONS = [
  { value: "all", label: "Tat ca muc" },
  { value: "high", label: "Cao (>= 0.8)" },
  { value: "medium", label: "Trung binh (0.5 - 0.8)" },
  { value: "low", label: "Thap (< 0.5)" },
];

function confidenceLevel(c) {
  if (c >= 0.8) return "high";
  if (c >= 0.5) return "medium";
  return "low";
}

function confidenceColor(c) {
  if (c >= 0.8) return "bg-emerald-100 text-emerald-800";
  if (c >= 0.5) return "bg-amber-100 text-amber-800";
  return "bg-red-100 text-red-800";
}

function categoryColor(cat) {
  const map = {
    operating: "bg-blue-100 text-blue-800",
    investing: "bg-purple-100 text-purple-800",
    financing: "bg-teal-100 text-teal-800",
    unknown: "bg-gray-100 text-gray-600",
  };
  return map[cat] || "bg-gray-100 text-gray-600";
}

export default function JournalView({ data }) {
  const journals = data?.journals || [];

  const [filterCategory, setFilterCategory] = useState("all");
  const [filterConfidence, setFilterConfidence] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState("amount");
  const [sortDir, setSortDir] = useState("desc");

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  const filteredJournals = useMemo(() => {
    let results = [...journals];

    // Filter by category
    if (filterCategory !== "all") {
      results = results.filter((j) => j.category === filterCategory);
    }

    // Filter by confidence
    if (filterConfidence !== "all") {
      results = results.filter(
        (j) => confidenceLevel(j.confidence) === filterConfidence
      );
    }

    // Search
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      results = results.filter(
        (j) =>
          j.description.toLowerCase().includes(q) ||
          j.debit.includes(q) ||
          j.debit_name.toLowerCase().includes(q) ||
          j.credit.includes(q) ||
          j.credit_name.toLowerCase().includes(q)
      );
    }

    // Sort
    results.sort((a, b) => {
      let cmp = 0;
      if (sortField === "amount") {
        cmp = a.amount - b.amount;
      } else if (sortField === "confidence") {
        cmp = a.confidence - b.confidence;
      } else if (sortField === "description") {
        cmp = a.description.localeCompare(b.description);
      }
      return sortDir === "asc" ? cmp : -cmp;
    });

    return results;
  }, [journals, filterCategory, filterConfidence, searchQuery, sortField, sortDir]);

  // Summary stats
  const stats = useMemo(() => {
    const total = filteredJournals.reduce((sum, j) => sum + j.amount, 0);
    const byCat = {};
    filteredJournals.forEach((j) => {
      byCat[j.category] = (byCat[j.category] || 0) + 1;
    });
    return { total, byCat, count: filteredJournals.length };
  }, [filteredJournals]);

  const SortIcon = ({ field }) => {
    if (sortField !== field) return <ArrowUpDown className="w-3 h-3 text-gray-300" />;
    return sortDir === "asc" ? (
      <ChevronUp className="w-3 h-3 text-indigo-600" />
    ) : (
      <ChevronDown className="w-3 h-3 text-indigo-600" />
    );
  };

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs text-gray-500">Tong but toan</p>
          <p className="text-2xl font-bold text-gray-800">{stats.count}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs text-gray-500">Tong gia tri</p>
          <p className="text-xl font-bold text-gray-800 tabular-nums">
            {formatVND(stats.total)}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs text-gray-500">Do tin cay cao</p>
          <p className="text-2xl font-bold text-emerald-600">
            {journals.filter((j) => j.confidence >= 0.8).length}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs text-gray-500">Chua xac dinh</p>
          <p className="text-2xl font-bold text-amber-600">
            {journals.filter((j) => j.category === "unknown").length}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tim kiem but toan, tai khoan..."
              className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-3 py-2
              focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {CATEGORY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          <select
            value={filterConfidence}
            onChange={(e) => setFilterConfidence(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-3 py-2
              focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {CONFIDENCE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-700 w-10">
                  #
                </th>
                <th
                  className="px-4 py-3 text-left font-semibold text-gray-700 cursor-pointer hover:text-indigo-600"
                  onClick={() => handleSort("description")}
                >
                  <span className="flex items-center gap-1">
                    Dien giai
                    <SortIcon field="description" />
                  </span>
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700 w-32">
                  TK No
                </th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700 w-32">
                  TK Co
                </th>
                <th
                  className="px-4 py-3 text-right font-semibold text-gray-700 w-36 cursor-pointer hover:text-indigo-600"
                  onClick={() => handleSort("amount")}
                >
                  <span className="flex items-center justify-end gap-1">
                    So tien
                    <SortIcon field="amount" />
                  </span>
                </th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700 w-28">
                  Loai
                </th>
                <th
                  className="px-4 py-3 text-center font-semibold text-gray-700 w-28 cursor-pointer hover:text-indigo-600"
                  onClick={() => handleSort("confidence")}
                >
                  <span className="flex items-center justify-center gap-1">
                    Do tin cay
                    <SortIcon field="confidence" />
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredJournals.map((journal, index) => (
                <tr
                  key={index}
                  className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <td className="px-4 py-2.5 text-gray-400 text-xs">
                    {index + 1}
                  </td>
                  <td className="px-4 py-2.5 text-gray-700 font-medium">
                    {journal.description}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="text-xs">
                      <span className="font-mono font-semibold text-gray-800">
                        {journal.debit}
                      </span>
                      <p className="text-gray-400 truncate">
                        {journal.debit_name}
                      </p>
                    </div>
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="text-xs">
                      <span className="font-mono font-semibold text-gray-800">
                        {journal.credit}
                      </span>
                      <p className="text-gray-400 truncate">
                        {journal.credit_name}
                      </p>
                    </div>
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums font-medium text-gray-800">
                    {formatVND(journal.amount)}
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <span
                      className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold ${categoryColor(journal.category)}`}
                    >
                      {categoryLabel(journal.category)}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <span
                      className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold ${confidenceColor(journal.confidence)}`}
                    >
                      {Math.round(journal.confidence * 100)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredJournals.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <BookOpen className="w-10 h-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">Khong co but toan nao phu hop voi bo loc.</p>
          </div>
        )}
      </div>

      {/* Info note */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
        <HelpCircle className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
        <div className="text-xs text-blue-700 space-y-1">
          <p className="font-semibold">Luu y ve but toan tai tao</p>
          <p>
            But toan duoc suy luan tu phat sinh No/Co tren bang Can doi Tai khoan.
            Do tin cay phan anh muc do chinh xac cua viec doi ung tai khoan.
          </p>
          <p>
            But toan co do tin cay thap hoac "Chua xac dinh" can duoc kiem tra
            them voi so chi tiet.
          </p>
        </div>
      </div>
    </div>
  );
}
