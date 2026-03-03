"""
Mapping ma chi tieu XML -> ten chi tieu BCTC theo Thong tu 133/2016/TT-BTC.
Dung cho hien thi UI va bao cao.

Ap dung cho doanh nghiep nho va vua (DN nho).
Ma to khai HTKK: 684.
"""

# =====================================================
#  BANG CAN DOI KE TOAN (B01b-DNN)
# =====================================================

CDKT_MAP = {
    # --- TAI SAN ---
    "ct100": {"name": "TAI SAN NGAN HAN", "level": 0, "ms": 100},
    "ct110": {"name": "Tien va cac khoan tuong duong tien", "level": 1, "ms": 110},
    "ct120": {"name": "Dau tu tai chinh ngan han", "level": 1, "ms": 120},
    "ct121": {"name": "Chung khoan kinh doanh", "level": 2, "ms": 121},
    "ct122": {"name": "Du phong giam gia CKKD", "level": 2, "ms": 122},
    "ct123": {"name": "Dau tu nam giu den ngay dao han", "level": 2, "ms": 123},
    "ct130": {"name": "Cac khoan phai thu ngan han", "level": 1, "ms": 130},
    "ct131": {"name": "Phai thu khach hang", "level": 2, "ms": 131},
    "ct132": {"name": "Tra truoc cho nguoi ban", "level": 2, "ms": 132},
    "ct133": {"name": "Cac khoan phai thu khac", "level": 2, "ms": 133},
    "ct134": {"name": "Thue GTGT duoc khau tru", "level": 2, "ms": 134},
    "ct135": {"name": "Du phong phai thu ngan han kho doi", "level": 2, "ms": 135},
    "ct140": {"name": "Hang ton kho", "level": 1, "ms": 140},
    "ct141": {"name": "Hang ton kho", "level": 2, "ms": 141},
    "ct142": {"name": "Du phong giam gia HTK", "level": 2, "ms": 142},
    "ct150": {"name": "Tai san ngan han khac", "level": 1, "ms": 150},
    "ct151": {"name": "Thue GTGT duoc khau tru", "level": 2, "ms": 151},
    "ct152": {"name": "Thue va cac khoan phai thu Nha nuoc", "level": 2, "ms": 152},

    # --- TAI SAN DAI HAN ---
    "ct200": {"name": "TAI SAN DAI HAN", "level": 0, "ms": 200},
    "ct210": {"name": "Tai san co dinh", "level": 1, "ms": 210},
    "ct211": {"name": "Nguyen gia TSCD huu hinh", "level": 2, "ms": 211},
    "ct212": {"name": "Gia tri hao mon luy ke", "level": 2, "ms": 212},
    "ct213": {"name": "Nguyen gia TSCD thue TC", "level": 2, "ms": 213},
    "ct214": {"name": "Gia tri hao mon luy ke TSCD thue TC", "level": 2, "ms": 214},
    "ct215": {"name": "Nguyen gia TSCD vo hinh", "level": 2, "ms": 215},
    "ct220": {"name": "Bat dong san dau tu", "level": 1, "ms": 220},
    "ct221": {"name": "Nguyen gia BDSDT", "level": 2, "ms": 221},
    "ct222": {"name": "Gia tri hao mon luy ke BDSDT", "level": 2, "ms": 222},
    "ct230": {"name": "Xay dung co ban do dang", "level": 1, "ms": 230},
    "ct240": {"name": "Dau tu tai chinh dai han", "level": 1, "ms": 240},
    "ct250": {"name": "Tai san dai han khac", "level": 1, "ms": 250},
    "ct260": {"name": "Loi the thuong mai", "level": 1, "ms": 260},
    "ct300": {"name": "TONG CONG TAI SAN", "level": 0, "ms": 300, "bold": True},

    # --- NGUON VON ---
    "ct400": {"name": "NO PHAI TRA", "level": 0, "ms": 400},
    "ct410": {"name": "No ngan han", "level": 1, "ms": 410},
    "ct411": {"name": "Phai tra nguoi ban ngan han", "level": 2, "ms": 411},
    "ct412": {"name": "Nguoi mua tra tien truoc ngan han", "level": 2, "ms": 412},
    "ct413": {"name": "Thue va cac khoan phai nop Nha nuoc", "level": 2, "ms": 413},
    "ct414": {"name": "Phai tra nguoi lao dong", "level": 2, "ms": 414},
    "ct415": {"name": "Chi phi phai tra ngan han", "level": 2, "ms": 415},
    "ct416": {"name": "Cac khoan phai tra, phai nop NH khac", "level": 2, "ms": 416},
    "ct417": {"name": "Vay va no thue tai chinh ngan han", "level": 2, "ms": 417},
    "ct418": {"name": "Quy khen thuong, phuc loi", "level": 2, "ms": 418},
    "ct420": {"name": "No dai han", "level": 1, "ms": 420},
    "ct421": {"name": "Phai tra nguoi ban dai han", "level": 2, "ms": 421},
    "ct500": {"name": "VON CHU SO HUU", "level": 0, "ms": 500},
    "ct511": {"name": "Von gop cua chu so huu", "level": 1, "ms": 511},
    "ct512": {"name": "Thang du von co phan", "level": 1, "ms": 512},
    "ct513": {"name": "Von khac cua chu so huu", "level": 1, "ms": 513},
    "ct514": {"name": "Co phieu quy", "level": 1, "ms": 514},
    "ct515": {"name": "Chenh lech ty gia hoi doai", "level": 1, "ms": 515},
    "ct516": {"name": "Cac quy", "level": 1, "ms": 516},
    "ct517": {"name": "Loi nhuan sau thue chua phan phoi", "level": 1, "ms": 517},
    "ct600": {"name": "TONG CONG NGUON VON", "level": 0, "ms": 600, "bold": True},
}


# =====================================================
#  KET QUA HOAT DONG KINH DOANH (B02-DNN)
# =====================================================

KQHDKD_MAP = {
    "ct01": {"name": "Doanh thu ban hang va cung cap dich vu", "ms": "01"},
    "ct02": {"name": "Cac khoan giam tru doanh thu", "ms": "02"},
    "ct10": {"name": "Doanh thu thuan", "ms": "10"},
    "ct11": {"name": "Gia von hang ban", "ms": "11"},
    "ct20": {"name": "Loi nhuan gop", "ms": "20"},
    "ct21": {"name": "Doanh thu hoat dong tai chinh", "ms": "21"},
    "ct22": {"name": "Chi phi tai chinh", "ms": "22"},
    "ct23": {"name": "Chi phi ban hang", "ms": "23"},
    "ct24": {"name": "Chi phi quan ly doanh nghiep", "ms": "24"},
    "ct30": {"name": "Loi nhuan thuan tu HDKD", "ms": "30"},
    "ct31": {"name": "Thu nhap khac", "ms": "31"},
    "ct32": {"name": "Chi phi khac", "ms": "32"},
    "ct40": {"name": "Loi nhuan khac", "ms": "40"},
    "ct50": {"name": "Tong loi nhuan ke toan truoc thue", "ms": "50"},
    "ct51": {"name": "Chi phi thue TNDN", "ms": "51"},
    "ct60": {"name": "Loi nhuan sau thue TNDN", "ms": "60"},
}


# =====================================================
#  LUU CHUYEN TIEN TE - TRUC TIEP (B03-DNN)
# =====================================================

LCTT_TT_MAP = {
    # --- HDKD ---
    "ct01": {"name": "Tien thu tu ban hang, cung cap DV", "ms": "01", "flow": "operating"},
    "ct02": {"name": "Tien chi tra cho nguoi cung cap hang hoa, DV", "ms": "02", "flow": "operating"},
    "ct03": {"name": "Tien chi tra cho nguoi lao dong", "ms": "03", "flow": "operating"},
    "ct04": {"name": "Tien chi tra lai vay", "ms": "04", "flow": "operating"},
    "ct05": {"name": "Tien chi nop thue TNDN", "ms": "05", "flow": "operating"},
    "ct06": {"name": "Tien thu khac tu HDKD", "ms": "06", "flow": "operating"},
    "ct07": {"name": "Tien chi khac cho HDKD", "ms": "07", "flow": "operating"},
    "ct20": {"name": "Luu chuyen tien thuan tu HDKD", "ms": "20", "flow": "operating", "subtotal": True},

    # --- HD Dau tu ---
    "ct21": {"name": "Tien chi mua sam, xay dung TSCD", "ms": "21", "flow": "investing"},
    "ct22": {"name": "Tien thu tu thanh ly TSCD", "ms": "22", "flow": "investing"},
    "ct23": {"name": "Tien chi cho vay, mua cong cu no", "ms": "23", "flow": "investing"},
    "ct24": {"name": "Tien thu hoi cho vay, ban cong cu no", "ms": "24", "flow": "investing"},
    "ct25": {"name": "Tien thu lai cho vay, co tuc, LN duoc chia", "ms": "25", "flow": "investing"},
    "ct30": {"name": "Luu chuyen tien thuan tu HD dau tu", "ms": "30", "flow": "investing", "subtotal": True},

    # --- HD Tai chinh ---
    "ct31": {"name": "Tien thu tu phat hanh CP, nhan von gop", "ms": "31", "flow": "financing"},
    "ct32": {"name": "Tien chi tra von gop cho CSH, mua lai CP", "ms": "32", "flow": "financing"},
    "ct33": {"name": "Tien thu tu di vay", "ms": "33", "flow": "financing"},
    "ct34": {"name": "Tien chi tra no goc vay", "ms": "34", "flow": "financing"},
    "ct35": {"name": "Tien chi tra no goc thue TC", "ms": "35", "flow": "financing"},
    "ct40": {"name": "Luu chuyen tien thuan tu HD tai chinh", "ms": "40", "flow": "financing", "subtotal": True},

    # --- Tong hop ---
    "ct50": {"name": "Tang/giam tien thuan trong ky", "ms": "50", "total": True},
    "ct60": {"name": "Tien va tuong duong tien dau ky", "ms": "60"},
    "ct61": {"name": "Anh huong thay doi ty gia", "ms": "61"},
    "ct70": {"name": "Tien va tuong duong tien cuoi ky", "ms": "70", "total": True},
}


# =====================================================
#  CAN DOI TAI KHOAN - Mapping TK ke toan (TT133)
# =====================================================

CDTK_ACCOUNT_MAP = {
    # TK Loai 1 - Tai san
    "ct111":  {"name": "Tien mat", "tk": "111", "loai": "TS"},
    "ct1111": {"name": "Tien Viet Nam", "tk": "1111", "parent": "111"},
    "ct1112": {"name": "Ngoai te", "tk": "1112", "parent": "111"},
    "ct112":  {"name": "Tien gui ngan hang", "tk": "112", "loai": "TS"},
    "ct1121": {"name": "Tien Viet Nam", "tk": "1121", "parent": "112"},
    "ct1122": {"name": "Ngoai te", "tk": "1122", "parent": "112"},
    "ct121":  {"name": "Chung khoan kinh doanh", "tk": "121", "loai": "TS"},
    "ct128":  {"name": "Dau tu nam giu den ngay dao han", "tk": "128", "loai": "TS"},
    "ct131":  {"name": "Phai thu khach hang", "tk": "131", "loai": "LK"},
    "ct133":  {"name": "Thue GTGT duoc khau tru", "tk": "133", "loai": "TS"},
    "ct1331": {"name": "Thue GTGT dau vao hang hoa, DV", "tk": "1331", "parent": "133"},
    "ct1332": {"name": "Thue GTGT dau vao TSCD", "tk": "1332", "parent": "133"},
    "ct136":  {"name": "Phai thu noi bo", "tk": "136", "loai": "TS"},
    "ct138":  {"name": "Phai thu khac", "tk": "138", "loai": "TS"},
    "ct141":  {"name": "Tam ung", "tk": "141", "loai": "TS"},
    "ct151":  {"name": "Hang mua dang di duong", "tk": "151", "loai": "TS"},
    "ct152":  {"name": "Nguyen lieu, vat lieu", "tk": "152", "loai": "TS"},
    "ct153":  {"name": "Cong cu, dung cu", "tk": "153", "loai": "TS"},
    "ct154":  {"name": "CP SXKD do dang", "tk": "154", "loai": "TS"},
    "ct155":  {"name": "Thanh pham", "tk": "155", "loai": "TS"},
    "ct156":  {"name": "Hang hoa", "tk": "156", "loai": "TS"},
    "ct157":  {"name": "Hang gui di ban", "tk": "157", "loai": "TS"},

    # TK Loai 2 - Tai san dai han
    "ct211":  {"name": "TSCD huu hinh", "tk": "211", "loai": "TS"},
    "ct214":  {"name": "Hao mon TSCD", "tk": "214", "loai": "TS_AM"},  # Du Co
    "ct217":  {"name": "BDS dau tu", "tk": "217", "loai": "TS"},
    "ct228":  {"name": "Dau tu gop von vao don vi khac", "tk": "228", "loai": "TS"},
    "ct229":  {"name": "Du phong ton that tai san", "tk": "229", "loai": "TS_DP"},
    "ct241":  {"name": "XDCB do dang", "tk": "241", "loai": "TS"},
    "ct242":  {"name": "Chi phi tra truoc", "tk": "242", "loai": "TS"},

    # TK Loai 3 - No phai tra
    "ct331":  {"name": "Phai tra cho nguoi ban", "tk": "331", "loai": "LK"},
    "ct333":  {"name": "Thue va cac khoan phai nop NN", "tk": "333", "loai": "NV"},
    "ct3331": {"name": "Thue GTGT phai nop", "tk": "3331", "parent": "333"},
    "ct3334": {"name": "Thue TNDN", "tk": "3334", "parent": "333"},
    "ct3335": {"name": "Thue TNCN", "tk": "3335", "parent": "333"},
    "ct334":  {"name": "Phai tra nguoi lao dong", "tk": "334", "loai": "NV"},
    "ct335":  {"name": "Chi phi phai tra", "tk": "335", "loai": "NV"},
    "ct336":  {"name": "Phai tra noi bo", "tk": "336", "loai": "NV"},
    "ct338":  {"name": "Phai tra, phai nop khac", "tk": "338", "loai": "NV"},
    "ct341":  {"name": "Vay va no thue TC", "tk": "341", "loai": "NV"},
    "ct352":  {"name": "Du phong phai tra", "tk": "352", "loai": "NV"},
    "ct353":  {"name": "Quy khen thuong, phuc loi", "tk": "353", "loai": "NV"},
    "ct356":  {"name": "Quy phat trien KH&CN", "tk": "356", "loai": "NV"},

    # TK Loai 4 - Von chu so huu
    "ct411":  {"name": "Von dau tu cua CSH", "tk": "411", "loai": "NV"},
    "ct4111": {"name": "Von gop cua CSH", "tk": "4111", "parent": "411"},
    "ct4112": {"name": "Thang du von co phan", "tk": "4112", "parent": "411"},
    "ct4118": {"name": "Von khac", "tk": "4118", "parent": "411"},
    "ct413":  {"name": "Chenh lech ty gia hoi doai", "tk": "413", "loai": "NV"},
    "ct418":  {"name": "Cac quy thuoc VCSH", "tk": "418", "loai": "NV"},
    "ct419":  {"name": "Co phieu quy", "tk": "419", "loai": "NV_AM"},
    "ct421":  {"name": "Loi nhuan sau thue chua PP", "tk": "421", "loai": "LK"},
    "ct4211": {"name": "LNST chua PP nam truoc", "tk": "4211", "parent": "421"},
    "ct4212": {"name": "LNST chua PP nam nay", "tk": "4212", "parent": "421"},

    # TK Loai 5 - Doanh thu
    "ct511":  {"name": "Doanh thu ban hang va CCDV", "tk": "511", "loai": "DT"},
    "ct515":  {"name": "Doanh thu hoat dong tai chinh", "tk": "515", "loai": "DT"},

    # TK Loai 6 - Chi phi (TT133 gop 641+642 thanh 642)
    "ct611":  {"name": "Mua hang", "tk": "611", "loai": "CP"},
    "ct631":  {"name": "Gia thanh san xuat", "tk": "631", "loai": "CP"},
    "ct632":  {"name": "Gia von hang ban", "tk": "632", "loai": "CP"},
    "ct635":  {"name": "Chi phi tai chinh", "tk": "635", "loai": "CP"},
    "ct642":  {"name": "Chi phi quan ly kinh doanh", "tk": "642", "loai": "CP"},
    "ct6421": {"name": "CP ban hang", "tk": "6421", "parent": "642"},
    "ct6422": {"name": "CP quan ly doanh nghiep", "tk": "6422", "parent": "642"},

    # TK Loai 7 - Thu nhap khac
    "ct711":  {"name": "Thu nhap khac", "tk": "711", "loai": "DT"},

    # TK Loai 8 - Chi phi khac
    "ct811":  {"name": "Chi phi khac", "tk": "811", "loai": "CP"},
    "ct821":  {"name": "Chi phi thue TNDN", "tk": "821", "loai": "CP"},

    # TK Loai 9 - Xac dinh KQKD
    "ct911":  {"name": "Xac dinh ket qua kinh doanh", "tk": "911", "loai": "XDKQ"},
}
