import { formatVND } from "../utils/formatters";

/**
 * Mapping ma chi tieu CDKT -> ten chi tieu, level theo TT133
 * Level 0 = header bold, level 1 = section, level 2 = detail
 */
const CDKT_ITEMS = [
  { code: "ct100", name: "TAI SAN NGAN HAN", level: 0, ms: 100 },
  {
    code: "ct110",
    name: "Tien va cac khoan tuong duong tien",
    level: 1,
    ms: 110,
  },
  {
    code: "ct120",
    name: "Dau tu tai chinh ngan han",
    level: 1,
    ms: 120,
  },
  { code: "ct121", name: "Chung khoan kinh doanh", level: 2, ms: 121 },
  {
    code: "ct122",
    name: "Du phong giam gia CKKD",
    level: 2,
    ms: 122,
  },
  {
    code: "ct123",
    name: "Dau tu nam giu den ngay dao han",
    level: 2,
    ms: 123,
  },
  {
    code: "ct130",
    name: "Cac khoan phai thu ngan han",
    level: 1,
    ms: 130,
  },
  { code: "ct131", name: "Phai thu khach hang", level: 2, ms: 131 },
  {
    code: "ct132",
    name: "Tra truoc cho nguoi ban",
    level: 2,
    ms: 132,
  },
  {
    code: "ct133",
    name: "Cac khoan phai thu khac",
    level: 2,
    ms: 133,
  },
  {
    code: "ct134",
    name: "Thue GTGT duoc khau tru",
    level: 2,
    ms: 134,
  },
  {
    code: "ct135",
    name: "Du phong phai thu ngan han kho doi",
    level: 2,
    ms: 135,
  },
  { code: "ct140", name: "Hang ton kho", level: 1, ms: 140 },
  { code: "ct141", name: "Hang ton kho", level: 2, ms: 141 },
  {
    code: "ct142",
    name: "Du phong giam gia HTK",
    level: 2,
    ms: 142,
  },
  {
    code: "ct150",
    name: "Tai san ngan han khac",
    level: 1,
    ms: 150,
  },
  {
    code: "ct151",
    name: "Thue GTGT duoc khau tru",
    level: 2,
    ms: 151,
  },
  {
    code: "ct152",
    name: "Thue va cac khoan phai thu Nha nuoc",
    level: 2,
    ms: 152,
  },
  { code: "ct200", name: "TAI SAN DAI HAN", level: 0, ms: 200 },
  { code: "ct210", name: "Tai san co dinh", level: 1, ms: 210 },
  {
    code: "ct211",
    name: "Nguyen gia TSCD huu hinh",
    level: 2,
    ms: 211,
  },
  {
    code: "ct212",
    name: "Gia tri hao mon luy ke",
    level: 2,
    ms: 212,
  },
  {
    code: "ct213",
    name: "Nguyen gia TSCD thue TC",
    level: 2,
    ms: 213,
  },
  {
    code: "ct214",
    name: "Gia tri hao mon luy ke TSCD thue TC",
    level: 2,
    ms: 214,
  },
  {
    code: "ct215",
    name: "Nguyen gia TSCD vo hinh",
    level: 2,
    ms: 215,
  },
  {
    code: "ct220",
    name: "Bat dong san dau tu",
    level: 1,
    ms: 220,
  },
  {
    code: "ct230",
    name: "Xay dung co ban do dang",
    level: 1,
    ms: 230,
  },
  {
    code: "ct240",
    name: "Dau tu tai chinh dai han",
    level: 1,
    ms: 240,
  },
  {
    code: "ct250",
    name: "Tai san dai han khac",
    level: 1,
    ms: 250,
  },
  {
    code: "ct260",
    name: "Loi the thuong mai",
    level: 1,
    ms: 260,
  },
  {
    code: "ct300",
    name: "TONG CONG TAI SAN",
    level: 0,
    ms: 300,
    bold: true,
  },
  { code: "ct400", name: "NO PHAI TRA", level: 0, ms: 400 },
  { code: "ct410", name: "No ngan han", level: 1, ms: 410 },
  {
    code: "ct411",
    name: "Phai tra nguoi ban ngan han",
    level: 2,
    ms: 411,
  },
  {
    code: "ct412",
    name: "Nguoi mua tra tien truoc ngan han",
    level: 2,
    ms: 412,
  },
  {
    code: "ct413",
    name: "Thue va cac khoan phai nop Nha nuoc",
    level: 2,
    ms: 413,
  },
  {
    code: "ct414",
    name: "Phai tra nguoi lao dong",
    level: 2,
    ms: 414,
  },
  {
    code: "ct415",
    name: "Chi phi phai tra ngan han",
    level: 2,
    ms: 415,
  },
  {
    code: "ct416",
    name: "Cac khoan phai tra, phai nop NH khac",
    level: 2,
    ms: 416,
  },
  {
    code: "ct417",
    name: "Vay va no thue tai chinh ngan han",
    level: 2,
    ms: 417,
  },
  {
    code: "ct418",
    name: "Quy khen thuong, phuc loi",
    level: 2,
    ms: 418,
  },
  { code: "ct420", name: "No dai han", level: 1, ms: 420 },
  {
    code: "ct421",
    name: "Phai tra nguoi ban dai han",
    level: 2,
    ms: 421,
  },
  { code: "ct500", name: "VON CHU SO HUU", level: 0, ms: 500 },
  {
    code: "ct511",
    name: "Von gop cua chu so huu",
    level: 1,
    ms: 511,
  },
  {
    code: "ct512",
    name: "Thang du von co phan",
    level: 1,
    ms: 512,
  },
  {
    code: "ct513",
    name: "Von khac cua chu so huu",
    level: 1,
    ms: 513,
  },
  { code: "ct514", name: "Co phieu quy", level: 1, ms: 514 },
  {
    code: "ct515",
    name: "Chenh lech ty gia hoi doai",
    level: 1,
    ms: 515,
  },
  { code: "ct516", name: "Cac quy", level: 1, ms: 516 },
  {
    code: "ct517",
    name: "Loi nhuan sau thue chua phan phoi",
    level: 1,
    ms: 517,
  },
  {
    code: "ct600",
    name: "TONG CONG NGUON VON",
    level: 0,
    ms: 600,
    bold: true,
  },
];

export default function BalanceSheet({ cdktData }) {
  if (!cdktData) return null;

  const { so_cuoi_nam = {}, so_dau_nam = {} } = cdktData;

  // Filter to only show rows that have data
  const visibleItems = CDKT_ITEMS.filter((item) => {
    if (item.level === 0) return true; // Always show headers
    const cuoiNam = so_cuoi_nam[item.code];
    const dauNam = so_dau_nam[item.code];
    return cuoiNam || dauNam;
  });

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-200 bg-gray-50">
        <h3 className="text-base font-semibold text-gray-800">
          Bang Can doi Ke toan
        </h3>
        <p className="text-xs text-gray-400 mt-0.5">
          Bieu mau B01b-DNN (Thong tu 133/2016)
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
                Ten chi tieu
              </th>
              <th className="px-4 py-2.5 text-right font-semibold w-40">
                So cuoi nam
              </th>
              <th className="px-4 py-2.5 text-right font-semibold w-40">
                So dau nam
              </th>
            </tr>
          </thead>
          <tbody>
            {visibleItems.map((item) => {
              const cuoiNam = so_cuoi_nam[item.code];
              const dauNam = so_dau_nam[item.code];
              const isHeader = item.level === 0;
              const isTotal = item.bold;

              return (
                <tr
                  key={item.code}
                  className={`border-b border-gray-100 ${
                    isTotal
                      ? "bg-indigo-50/50 font-bold"
                      : isHeader
                        ? "bg-gray-50 font-semibold"
                        : "hover:bg-gray-50"
                  }`}
                >
                  <td className="px-4 py-2 text-gray-500 font-mono text-xs">
                    {item.ms}
                  </td>
                  <td
                    className={`px-4 py-2 ${isHeader ? "text-gray-800" : "text-gray-600"}`}
                    style={{
                      paddingLeft: `${item.level * 20 + 16}px`,
                    }}
                  >
                    {item.name}
                  </td>
                  <td
                    className={`px-4 py-2 text-right tabular-nums ${
                      cuoiNam < 0 ? "text-red-600" : "text-gray-800"
                    }`}
                  >
                    {formatVND(cuoiNam)}
                  </td>
                  <td
                    className={`px-4 py-2 text-right tabular-nums ${
                      dauNam < 0 ? "text-red-600" : "text-gray-800"
                    }`}
                  >
                    {formatVND(dauNam)}
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
