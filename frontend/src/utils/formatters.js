/**
 * Format number as Vietnamese Dong with dots separator.
 * e.g., 1234567 => "1.234.567"
 */
export function formatVND(number) {
  if (number === null || number === undefined) return "—";
  const num = Number(number);
  if (isNaN(num)) return "—";
  if (num === 0) return "0";

  const isNegative = num < 0;
  const absStr = Math.abs(Math.round(num)).toString();
  let result = "";
  let count = 0;
  for (let i = absStr.length - 1; i >= 0; i--) {
    if (count > 0 && count % 3 === 0) {
      result = "." + result;
    }
    result = absStr[i] + result;
    count++;
  }
  return isNegative ? `(${result})` : result;
}

/**
 * Format number as percentage.
 * e.g., 45.678 => "45,68%"
 */
export function formatPercent(number) {
  if (number === null || number === undefined) return "—";
  const num = Number(number);
  if (isNaN(num)) return "—";
  return num.toFixed(2).replace(".", ",") + "%";
}

/**
 * Format ratio with 2 decimal places using Vietnamese format.
 * e.g., 1.2345 => "1,23"
 */
export function formatRatio(number) {
  if (number === null || number === undefined) return "—";
  const num = Number(number);
  if (isNaN(num)) return "—";
  return num.toFixed(2).replace(".", ",");
}

/**
 * Return Tailwind CSS color classes based on severity level.
 */
export function severityColor(severity) {
  switch (severity) {
    case "ok":
      return {
        bg: "bg-emerald-50",
        text: "text-emerald-700",
        border: "border-emerald-200",
        badge: "bg-emerald-100 text-emerald-800",
        dot: "bg-emerald-500",
      };
    case "warning":
      return {
        bg: "bg-amber-50",
        text: "text-amber-700",
        border: "border-amber-200",
        badge: "bg-amber-100 text-amber-800",
        dot: "bg-amber-500",
      };
    case "error":
      return {
        bg: "bg-red-50",
        text: "text-red-700",
        border: "border-red-200",
        badge: "bg-red-100 text-red-800",
        dot: "bg-red-500",
      };
    case "critical":
      return {
        bg: "bg-rose-50",
        text: "text-rose-800",
        border: "border-rose-300",
        badge: "bg-rose-200 text-rose-900",
        dot: "bg-rose-700",
      };
    default:
      return {
        bg: "bg-gray-50",
        text: "text-gray-700",
        border: "border-gray-200",
        badge: "bg-gray-100 text-gray-800",
        dot: "bg-gray-500",
      };
  }
}

/**
 * Return color classes based on risk level.
 */
export function riskColor(riskLevel) {
  switch (riskLevel) {
    case "low":
      return {
        bg: "bg-blue-50",
        text: "text-blue-700",
        border: "border-blue-200",
        badge: "bg-blue-100 text-blue-800",
      };
    case "medium":
      return {
        bg: "bg-amber-50",
        text: "text-amber-700",
        border: "border-amber-200",
        badge: "bg-amber-100 text-amber-800",
      };
    case "high":
      return {
        bg: "bg-orange-50",
        text: "text-orange-700",
        border: "border-orange-200",
        badge: "bg-orange-100 text-orange-800",
      };
    case "critical":
      return {
        bg: "bg-red-50",
        text: "text-red-800",
        border: "border-red-300",
        badge: "bg-red-200 text-red-900",
      };
    default:
      return {
        bg: "bg-gray-50",
        text: "text-gray-700",
        border: "border-gray-200",
        badge: "bg-gray-100 text-gray-800",
      };
  }
}

/**
 * Vietnamese label for risk level
 */
export function riskLabel(riskLevel) {
  const map = {
    low: "Thap",
    medium: "Trung binh",
    high: "Cao",
    critical: "Nghiem trong",
  };
  return map[riskLevel] || riskLevel;
}

/**
 * Vietnamese label for severity
 */
export function severityLabel(severity) {
  const map = {
    ok: "Dat",
    warning: "Canh bao",
    error: "Loi",
    critical: "Nghiem trong",
  };
  return map[severity] || severity;
}

/**
 * Vietnamese label for category
 */
export function categoryLabel(category) {
  const map = {
    operating: "Hoat dong kinh doanh",
    investing: "Hoat dong dau tu",
    financing: "Hoat dong tai chinh",
    unknown: "Chua xac dinh",
    cash: "Tien mat",
    tax: "Thue",
    structure: "Cau truc",
    activity: "Hoat dong",
    liquidity: "Thanh khoan",
    profitability: "Sinh loi",
    leverage: "Don bay",
    efficiency: "Hieu suat",
  };
  return map[category] || category;
}
