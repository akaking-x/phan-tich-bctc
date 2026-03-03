import { formatVND } from "../utils/formatters";

const KQHDKD_ITEMS = [
  {
    code: "ct01",
    name: "Doanh thu ban hang va cung cap dich vu",
    ms: "01",
    level: 0,
  },
  {
    code: "ct02",
    name: "Cac khoan giam tru doanh thu",
    ms: "02",
    level: 0,
  },
  { code: "ct10", name: "Doanh thu thuan", ms: "10", level: 0, bold: true },
  { code: "ct11", name: "Gia von hang ban", ms: "11", level: 0 },
  { code: "ct20", name: "Loi nhuan gop", ms: "20", level: 0, bold: true },
  {
    code: "ct21",
    name: "Doanh thu hoat dong tai chinh",
    ms: "21",
    level: 0,
  },
  { code: "ct22", name: "Chi phi tai chinh", ms: "22", level: 0 },
  { code: "ct23", name: "Chi phi ban hang", ms: "23", level: 0 },
  {
    code: "ct24",
    name: "Chi phi quan ly doanh nghiep",
    ms: "24",
    level: 0,
  },
  {
    code: "ct30",
    name: "Loi nhuan thuan tu HDKD",
    ms: "30",
    level: 0,
    bold: true,
  },
  { code: "ct31", name: "Thu nhap khac", ms: "31", level: 0 },
  { code: "ct32", name: "Chi phi khac", ms: "32", level: 0 },
  { code: "ct40", name: "Loi nhuan khac", ms: "40", level: 0, bold: true },
  {
    code: "ct50",
    name: "Tong loi nhuan ke toan truoc thue",
    ms: "50",
    level: 0,
    bold: true,
    highlight: true,
  },
  { code: "ct51", name: "Chi phi thue TNDN", ms: "51", level: 0 },
  {
    code: "ct60",
    name: "Loi nhuan sau thue TNDN",
    ms: "60",
    level: 0,
    bold: true,
    highlight: true,
  },
];

export default function IncomeStatement({ kqhdkdData }) {
  if (!kqhdkdData) return null;

  const { nam_nay = {}, nam_truoc = {} } = kqhdkdData;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-200 bg-gray-50">
        <h3 className="text-base font-semibold text-gray-800">
          Ket qua Hoat dong Kinh doanh
        </h3>
        <p className="text-xs text-gray-400 mt-0.5">
          Bieu mau B02-DNN (Thong tu 133/2016)
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-indigo-50 text-indigo-800">
              <th className="px-4 py-2.5 text-left font-semibold w-16">
                Ma so
              </th>
              <th className="px-4 py-2.5 text-left font-semibold">
                Chi tieu
              </th>
              <th className="px-4 py-2.5 text-right font-semibold w-40">
                Nam nay
              </th>
              <th className="px-4 py-2.5 text-right font-semibold w-40">
                Nam truoc
              </th>
            </tr>
          </thead>
          <tbody>
            {KQHDKD_ITEMS.map((item) => {
              const namNay = nam_nay[item.code];
              const namTruoc = nam_truoc[item.code];

              return (
                <tr
                  key={item.code}
                  className={`border-b border-gray-100 ${
                    item.highlight
                      ? "bg-indigo-50/50"
                      : item.bold
                        ? "bg-gray-50"
                        : "hover:bg-gray-50"
                  }`}
                >
                  <td className="px-4 py-2.5 text-gray-500 font-mono text-xs">
                    {item.ms}
                  </td>
                  <td
                    className={`px-4 py-2.5 ${item.bold ? "font-semibold text-gray-800" : "text-gray-600"}`}
                  >
                    {item.name}
                  </td>
                  <td
                    className={`px-4 py-2.5 text-right tabular-nums ${
                      item.bold ? "font-semibold" : ""
                    } ${namNay < 0 ? "text-red-600" : "text-gray-800"}`}
                  >
                    {formatVND(namNay)}
                  </td>
                  <td
                    className={`px-4 py-2.5 text-right tabular-nums ${
                      namTruoc < 0 ? "text-red-600" : "text-gray-800"
                    }`}
                  >
                    {formatVND(namTruoc)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
