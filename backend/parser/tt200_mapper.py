"""
Mapping ma chi tieu XML -> ten chi tieu BCTC theo Thong tu 200/2014/TT-BTC.
Dung cho doanh nghiep lon (DN lon).
Ma to khai HTKK: 405.

Khac biet chinh voi TT133:
- CDKT chi tiet hon (tach TK 641/642, them nhieu chi tieu TSCD, VCSH)
- KQHDKD tach rieng CP ban hang (ct25) va CP QLDN (ct26)
- He thong TK ke toan day du hon (TK 241 tach 2411/2412/2413, etc.)
"""

# =====================================================
#  BANG CAN DOI KE TOAN (B01-DN) - TT200
# =====================================================

CDKT_MAP = {
    # --- TAI SAN NGAN HAN ---
    "ct100": {"name": "A. TAI SAN NGAN HAN", "level": 0, "ms": 100},
    "ct110": {"name": "I. Tien va cac khoan tuong duong tien", "level": 1, "ms": 110},
    "ct111": {"name": "1. Tien", "level": 2, "ms": 111},
    "ct112": {"name": "2. Cac khoan tuong duong tien", "level": 2, "ms": 112},
    "ct120": {"name": "II. Dau tu tai chinh ngan han", "level": 1, "ms": 120},
    "ct121": {"name": "1. Chung khoan kinh doanh", "level": 2, "ms": 121},
    "ct122": {"name": "2. Du phong giam gia CKKD", "level": 2, "ms": 122},
    "ct123": {"name": "3. Dau tu nam giu den ngay dao han", "level": 2, "ms": 123},
    "ct130": {"name": "III. Cac khoan phai thu ngan han", "level": 1, "ms": 130},
    "ct131": {"name": "1. Phai thu ngan han cua khach hang", "level": 2, "ms": 131},
    "ct132": {"name": "2. Tra truoc cho nguoi ban ngan han", "level": 2, "ms": 132},
    "ct133": {"name": "3. Phai thu noi bo ngan han", "level": 2, "ms": 133},
    "ct134": {"name": "4. Phai thu theo tien do ke hoach hop dong XD", "level": 2, "ms": 134},
    "ct135": {"name": "5. Phai thu ve cho vay ngan han", "level": 2, "ms": 135},
    "ct136": {"name": "6. Cac khoan phai thu ngan han khac", "level": 2, "ms": 136},
    "ct137": {"name": "7. Du phong phai thu ngan han kho doi", "level": 2, "ms": 137},
    "ct139": {"name": "8. Tai san thieu cho xu ly", "level": 2, "ms": 139},
    "ct140": {"name": "IV. Hang ton kho", "level": 1, "ms": 140},
    "ct141": {"name": "1. Hang ton kho", "level": 2, "ms": 141},
    "ct149": {"name": "2. Du phong giam gia HTK", "level": 2, "ms": 149},
    "ct150": {"name": "V. Tai san ngan han khac", "level": 1, "ms": 150},
    "ct151": {"name": "1. Chi phi tra truoc ngan han", "level": 2, "ms": 151},
    "ct152": {"name": "2. Thue GTGT duoc khau tru", "level": 2, "ms": 152},
    "ct153": {"name": "3. Thue va cac khoan khac phai thu Nha nuoc", "level": 2, "ms": 153},
    "ct154": {"name": "4. Giao dich mua ban lai trai phieu CP", "level": 2, "ms": 154},
    "ct155": {"name": "5. Tai san ngan han khac", "level": 2, "ms": 155},

    # --- TAI SAN DAI HAN ---
    "ct200": {"name": "B. TAI SAN DAI HAN", "level": 0, "ms": 200},
    "ct210": {"name": "I. Cac khoan phai thu dai han", "level": 1, "ms": 210},
    "ct211": {"name": "1. Phai thu dai han cua khach hang", "level": 2, "ms": 211},
    "ct212": {"name": "2. Tra truoc cho nguoi ban dai han", "level": 2, "ms": 212},
    "ct213": {"name": "3. Von kinh doanh o don vi truc thuoc", "level": 2, "ms": 213},
    "ct214": {"name": "4. Phai thu noi bo dai han", "level": 2, "ms": 214},
    "ct215": {"name": "5. Phai thu ve cho vay dai han", "level": 2, "ms": 215},
    "ct216": {"name": "6. Phai thu dai han khac", "level": 2, "ms": 216},
    "ct219": {"name": "7. Du phong phai thu dai han kho doi", "level": 2, "ms": 219},
    "ct220": {"name": "II. Tai san co dinh", "level": 1, "ms": 220},
    "ct221": {"name": "1. TSCD huu hinh", "level": 2, "ms": 221},
    "ct222": {"name": "- Nguyen gia", "level": 3, "ms": 222},
    "ct223": {"name": "- Gia tri hao mon luy ke", "level": 3, "ms": 223},
    "ct224": {"name": "2. TSCD thue tai chinh", "level": 2, "ms": 224},
    "ct225": {"name": "- Nguyen gia", "level": 3, "ms": 225},
    "ct226": {"name": "- Gia tri hao mon luy ke", "level": 3, "ms": 226},
    "ct227": {"name": "3. TSCD vo hinh", "level": 2, "ms": 227},
    "ct228": {"name": "- Nguyen gia", "level": 3, "ms": 228},
    "ct229": {"name": "- Gia tri hao mon luy ke", "level": 3, "ms": 229},
    "ct230": {"name": "III. Bat dong san dau tu", "level": 1, "ms": 230},
    "ct231": {"name": "- Nguyen gia", "level": 2, "ms": 231},
    "ct232": {"name": "- Gia tri hao mon luy ke", "level": 2, "ms": 232},
    "ct240": {"name": "IV. Tai san do dang dai han", "level": 1, "ms": 240},
    "ct241": {"name": "1. Chi phi SXKD do dang dai han", "level": 2, "ms": 241},
    "ct242": {"name": "2. Chi phi xay dung co ban do dang", "level": 2, "ms": 242},
    "ct250": {"name": "V. Dau tu tai chinh dai han", "level": 1, "ms": 250},
    "ct251": {"name": "1. Dau tu vao cong ty con", "level": 2, "ms": 251},
    "ct252": {"name": "2. Dau tu vao cong ty lien doanh, lien ket", "level": 2, "ms": 252},
    "ct253": {"name": "3. Dau tu gop von vao don vi khac", "level": 2, "ms": 253},
    "ct254": {"name": "4. Du phong dau tu TC dai han", "level": 2, "ms": 254},
    "ct255": {"name": "5. Dau tu nam giu den ngay dao han", "level": 2, "ms": 255},
    "ct260": {"name": "VI. Tai san dai han khac", "level": 1, "ms": 260},
    "ct261": {"name": "1. Chi phi tra truoc dai han", "level": 2, "ms": 261},
    "ct262": {"name": "2. Tai san thue thu nhap hoan lai", "level": 2, "ms": 262},
    "ct263": {"name": "3. Thiet bi, vat tu, phu tung thay the dai han", "level": 2, "ms": 263},
    "ct268": {"name": "4. Tai san dai han khac", "level": 2, "ms": 268},
    "ct269": {"name": "5. Loi the thuong mai", "level": 2, "ms": 269},
    "ct270": {"name": "TONG CONG TAI SAN (270=100+200)", "level": 0, "ms": 270, "bold": True},

    # --- NGUON VON ---
    "ct300": {"name": "C. NO PHAI TRA (300=310+330)", "level": 0, "ms": 300},
    "ct310": {"name": "I. No ngan han", "level": 1, "ms": 310},
    "ct311": {"name": "1. Phai tra nguoi ban ngan han", "level": 2, "ms": 311},
    "ct312": {"name": "2. Nguoi mua tra tien truoc ngan han", "level": 2, "ms": 312},
    "ct313": {"name": "3. Thue va cac khoan phai nop NN", "level": 2, "ms": 313},
    "ct314": {"name": "4. Phai tra nguoi lao dong", "level": 2, "ms": 314},
    "ct315": {"name": "5. Chi phi phai tra ngan han", "level": 2, "ms": 315},
    "ct316": {"name": "6. Phai tra noi bo ngan han", "level": 2, "ms": 316},
    "ct317": {"name": "7. Phai tra theo tien do ke hoach hop dong XD", "level": 2, "ms": 317},
    "ct318": {"name": "8. Doanh thu chua thuc hien ngan han", "level": 2, "ms": 318},
    "ct319": {"name": "9. Cac khoan phai tra, phai nop NH khac", "level": 2, "ms": 319},
    "ct320": {"name": "10. Vay va no thue TC ngan han", "level": 2, "ms": 320},
    "ct321": {"name": "11. Du phong phai tra ngan han", "level": 2, "ms": 321},
    "ct322": {"name": "12. Quy khen thuong, phuc loi", "level": 2, "ms": 322},
    "ct323": {"name": "13. Giao dich mua ban lai trai phieu CP", "level": 2, "ms": 323},
    "ct330": {"name": "II. No dai han", "level": 1, "ms": 330},
    "ct331": {"name": "1. Phai tra nguoi ban dai han", "level": 2, "ms": 331},
    "ct332": {"name": "2. Nguoi mua tra tien truoc dai han", "level": 2, "ms": 332},
    "ct333": {"name": "3. Chi phi phai tra dai han", "level": 2, "ms": 333},
    "ct334": {"name": "4. Phai tra noi bo ve von kinh doanh", "level": 2, "ms": 334},
    "ct335": {"name": "5. Phai tra noi bo dai han", "level": 2, "ms": 335},
    "ct336": {"name": "6. Doanh thu chua thuc hien dai han", "level": 2, "ms": 336},
    "ct337": {"name": "7. Phai tra dai han khac", "level": 2, "ms": 337},
    "ct338": {"name": "8. Vay va no thue TC dai han", "level": 2, "ms": 338},
    "ct339": {"name": "9. Trai phieu chuyen doi", "level": 2, "ms": 339},
    "ct340": {"name": "10. Co phieu uu dai", "level": 2, "ms": 340},
    "ct341": {"name": "11. Thue thu nhap hoan lai phai tra", "level": 2, "ms": 341},
    "ct342": {"name": "12. Du phong phai tra dai han", "level": 2, "ms": 342},
    "ct343": {"name": "13. Quy phat trien KH&CN", "level": 2, "ms": 343},

    "ct400": {"name": "D. VON CHU SO HUU (400=410+430)", "level": 0, "ms": 400},
    "ct410": {"name": "I. Von chu so huu", "level": 1, "ms": 410},
    "ct411": {"name": "1. Von gop cua chu so huu", "level": 2, "ms": 411},
    "ct411a": {"name": "- Co phieu pho thong co quyen bieu quyet", "level": 3, "ms": "411a"},
    "ct411b": {"name": "- Co phieu uu dai", "level": 3, "ms": "411b"},
    "ct412": {"name": "2. Thang du von co phan", "level": 2, "ms": 412},
    "ct413": {"name": "3. Quyen chon chuyen doi trai phieu", "level": 2, "ms": 413},
    "ct414": {"name": "4. Von khac cua chu so huu", "level": 2, "ms": 414},
    "ct415": {"name": "5. Co phieu quy", "level": 2, "ms": 415},
    "ct416": {"name": "6. Chenh lech danh gia lai tai san", "level": 2, "ms": 416},
    "ct417": {"name": "7. Chenh lech ty gia hoi doai", "level": 2, "ms": 417},
    "ct418": {"name": "8. Quy dau tu phat trien", "level": 2, "ms": 418},
    "ct419": {"name": "9. Quy du phong tai chinh", "level": 2, "ms": 419},
    "ct420": {"name": "10. Quy khac thuoc VCSH", "level": 2, "ms": 420},
    "ct421": {"name": "11. Loi nhuan sau thue chua phan phoi", "level": 2, "ms": 421},
    "ct421a": {"name": "- LNST chua PP luy ke den cuoi ky truoc", "level": 3, "ms": "421a"},
    "ct421b": {"name": "- LNST chua PP ky nay", "level": 3, "ms": "421b"},
    "ct422": {"name": "12. Nguon von dau tu XDCB", "level": 2, "ms": 422},
    "ct430": {"name": "II. Nguon kinh phi va quy khac", "level": 1, "ms": 430},
    "ct431": {"name": "1. Nguon kinh phi", "level": 2, "ms": 431},
    "ct432": {"name": "2. Nguon kinh phi da hinh thanh TSCD", "level": 2, "ms": 432},
    "ct440": {"name": "TONG CONG NGUON VON (440=300+400)", "level": 0, "ms": 440, "bold": True},
}


# =====================================================
#  KET QUA HOAT DONG KINH DOANH (B02-DN) - TT200
# =====================================================
# Khac TT133: tach rieng CP ban hang (ct25) va CP QLDN (ct26)

KQHDKD_MAP = {
    "ct01": {"name": "Doanh thu ban hang va cung cap dich vu", "ms": "01"},
    "ct02": {"name": "Cac khoan giam tru doanh thu", "ms": "02"},
    "ct10": {"name": "Doanh thu thuan ve ban hang va CCDV", "ms": "10"},
    "ct11": {"name": "Gia von hang ban", "ms": "11"},
    "ct20": {"name": "Loi nhuan gop ve ban hang va CCDV", "ms": "20"},
    "ct21": {"name": "Doanh thu hoat dong tai chinh", "ms": "21"},
    "ct22": {"name": "Chi phi tai chinh", "ms": "22"},
    "ct23": {"name": "Trong do: Chi phi lai vay", "ms": "23"},
    "ct25": {"name": "Chi phi ban hang", "ms": "25"},
    "ct26": {"name": "Chi phi quan ly doanh nghiep", "ms": "26"},
    "ct30": {"name": "Loi nhuan thuan tu hoat dong kinh doanh", "ms": "30"},
    "ct31": {"name": "Thu nhap khac", "ms": "31"},
    "ct32": {"name": "Chi phi khac", "ms": "32"},
    "ct40": {"name": "Loi nhuan khac", "ms": "40"},
    "ct50": {"name": "Tong loi nhuan ke toan truoc thue", "ms": "50"},
    "ct51": {"name": "Chi phi thue TNDN hien hanh", "ms": "51"},
    "ct52": {"name": "Chi phi thue TNDN hoan lai", "ms": "52"},
    "ct60": {"name": "Loi nhuan sau thue thu nhap doanh nghiep", "ms": "60"},
    "ct70": {"name": "Lai co ban tren co phieu", "ms": "70"},
    "ct71": {"name": "Lai suy giam tren co phieu", "ms": "71"},
}


# =====================================================
#  LUU CHUYEN TIEN TE - TRUC TIEP (B03-DN) - TT200
# =====================================================

LCTT_TT_MAP = {
    # --- HDKD ---
    "ct01": {"name": "Tien thu tu ban hang, cung cap DV va DT khac", "ms": "01", "flow": "operating"},
    "ct02": {"name": "Tien chi tra cho nguoi cung cap HH va DV", "ms": "02", "flow": "operating"},
    "ct03": {"name": "Tien chi tra cho nguoi lao dong", "ms": "03", "flow": "operating"},
    "ct04": {"name": "Tien lai vay da tra", "ms": "04", "flow": "operating"},
    "ct05": {"name": "Thue TNDN da nop", "ms": "05", "flow": "operating"},
    "ct06": {"name": "Tien thu khac tu hoat dong kinh doanh", "ms": "06", "flow": "operating"},
    "ct07": {"name": "Tien chi khac cho hoat dong kinh doanh", "ms": "07", "flow": "operating"},
    "ct20": {"name": "Luu chuyen tien thuan tu HDKD", "ms": "20", "flow": "operating", "subtotal": True},

    # --- HD Dau tu ---
    "ct21": {"name": "Tien chi de mua sam, xay dung TSCD va TS dai han khac", "ms": "21", "flow": "investing"},
    "ct22": {"name": "Tien thu tu thanh ly, nhuong ban TSCD va TS dai han khac", "ms": "22", "flow": "investing"},
    "ct23": {"name": "Tien chi cho vay, mua cac cong cu no cua DV khac", "ms": "23", "flow": "investing"},
    "ct24": {"name": "Tien thu hoi cho vay, ban lai cac cong cu no cua DV khac", "ms": "24", "flow": "investing"},
    "ct25": {"name": "Tien chi dau tu gop von vao don vi khac", "ms": "25", "flow": "investing"},
    "ct26": {"name": "Tien thu hoi dau tu gop von vao don vi khac", "ms": "26", "flow": "investing"},
    "ct27": {"name": "Tien thu lai cho vay, co tuc va loi nhuan duoc chia", "ms": "27", "flow": "investing"},
    "ct30": {"name": "Luu chuyen tien thuan tu hoat dong dau tu", "ms": "30", "flow": "investing", "subtotal": True},

    # --- HD Tai chinh ---
    "ct31": {"name": "Tien thu tu phat hanh co phieu, nhan von gop cua CSH", "ms": "31", "flow": "financing"},
    "ct32": {"name": "Tien tra lai von gop cho CSH, mua lai co phieu da phat hanh", "ms": "32", "flow": "financing"},
    "ct33": {"name": "Tien thu tu di vay", "ms": "33", "flow": "financing"},
    "ct34": {"name": "Tien tra no goc vay", "ms": "34", "flow": "financing"},
    "ct35": {"name": "Tien tra no goc thue tai chinh", "ms": "35", "flow": "financing"},
    "ct36": {"name": "Co tuc, loi nhuan da tra cho CSH", "ms": "36", "flow": "financing"},
    "ct40": {"name": "Luu chuyen tien thuan tu hoat dong tai chinh", "ms": "40", "flow": "financing", "subtotal": True},

    # --- Tong hop ---
    "ct50": {"name": "Luu chuyen tien thuan trong ky", "ms": "50", "total": True},
    "ct60": {"name": "Tien va tuong duong tien dau ky", "ms": "60"},
    "ct61": {"name": "Anh huong cua thay doi ty gia hoi doai quy doi ngoai te", "ms": "61"},
    "ct70": {"name": "Tien va tuong duong tien cuoi ky", "ms": "70", "total": True},
}


# =====================================================
#  CAN DOI TAI KHOAN - Mapping TK ke toan (TT200)
# =====================================================
# TT200 co he thong TK day du hon TT133:
# - TK 641 (CP ban hang) tach rieng, khong gop vao 642
# - TK 242 tach thanh CP tra truoc NH va DH
# - TK 241 tach 2411/2412/2413
# - Them TK 243, 244, 347, etc.

CDTK_ACCOUNT_MAP = {
    # TK Loai 1 - Tai san
    "ct111":  {"name": "Tien mat", "tk": "111", "loai": "TS"},
    "ct1111": {"name": "Tien Viet Nam", "tk": "1111", "parent": "111"},
    "ct1112": {"name": "Ngoai te", "tk": "1112", "parent": "111"},
    "ct1113": {"name": "Vang tien te", "tk": "1113", "parent": "111"},
    "ct112":  {"name": "Tien gui ngan hang", "tk": "112", "loai": "TS"},
    "ct1121": {"name": "Tien Viet Nam", "tk": "1121", "parent": "112"},
    "ct1122": {"name": "Ngoai te", "tk": "1122", "parent": "112"},
    "ct1123": {"name": "Vang tien te", "tk": "1123", "parent": "112"},
    "ct113":  {"name": "Tien dang chuyen", "tk": "113", "loai": "TS"},
    "ct121":  {"name": "Chung khoan kinh doanh", "tk": "121", "loai": "TS"},
    "ct128":  {"name": "Dau tu nam giu den ngay dao han", "tk": "128", "loai": "TS"},
    "ct131":  {"name": "Phai thu cua khach hang", "tk": "131", "loai": "LK"},
    "ct133":  {"name": "Thue GTGT duoc khau tru", "tk": "133", "loai": "TS"},
    "ct1331": {"name": "Thue GTGT dau vao hang hoa, DV", "tk": "1331", "parent": "133"},
    "ct1332": {"name": "Thue GTGT dau vao TSCD", "tk": "1332", "parent": "133"},
    "ct136":  {"name": "Phai thu noi bo", "tk": "136", "loai": "TS"},
    "ct1361": {"name": "Von kinh doanh o cac don vi truc thuoc", "tk": "1361", "parent": "136"},
    "ct1368": {"name": "Phai thu noi bo khac", "tk": "1368", "parent": "136"},
    "ct138":  {"name": "Phai thu khac", "tk": "138", "loai": "TS"},
    "ct1381": {"name": "Tai san thieu cho xu ly", "tk": "1381", "parent": "138"},
    "ct1385": {"name": "Phai thu ve co phan hoa", "tk": "1385", "parent": "138"},
    "ct1388": {"name": "Phai thu khac", "tk": "1388", "parent": "138"},
    "ct141":  {"name": "Tam ung", "tk": "141", "loai": "TS"},
    "ct151":  {"name": "Hang mua dang di duong", "tk": "151", "loai": "TS"},
    "ct152":  {"name": "Nguyen lieu, vat lieu", "tk": "152", "loai": "TS"},
    "ct153":  {"name": "Cong cu, dung cu", "tk": "153", "loai": "TS"},
    "ct154":  {"name": "Chi phi SXKD do dang", "tk": "154", "loai": "TS"},
    "ct155":  {"name": "Thanh pham", "tk": "155", "loai": "TS"},
    "ct156":  {"name": "Hang hoa", "tk": "156", "loai": "TS"},
    "ct157":  {"name": "Hang gui di ban", "tk": "157", "loai": "TS"},
    "ct158":  {"name": "Hang hoa kho bao thue", "tk": "158", "loai": "TS"},

    # TK Loai 2 - Tai san dai han
    "ct211":  {"name": "TSCD huu hinh", "tk": "211", "loai": "TS"},
    "ct2111": {"name": "Nha cua, vat kien truc", "tk": "2111", "parent": "211"},
    "ct2112": {"name": "May moc, thiet bi", "tk": "2112", "parent": "211"},
    "ct2113": {"name": "Phuong tien van tai, truyen dan", "tk": "2113", "parent": "211"},
    "ct2114": {"name": "Thiet bi, dung cu quan ly", "tk": "2114", "parent": "211"},
    "ct2115": {"name": "Cay lau nam, suc vat lam viec", "tk": "2115", "parent": "211"},
    "ct2118": {"name": "TSCD khac", "tk": "2118", "parent": "211"},
    "ct212":  {"name": "TSCD thue tai chinh", "tk": "212", "loai": "TS"},
    "ct213":  {"name": "TSCD vo hinh", "tk": "213", "loai": "TS"},
    "ct2131": {"name": "Quyen su dung dat", "tk": "2131", "parent": "213"},
    "ct2135": {"name": "Chuong trinh phan mem", "tk": "2135", "parent": "213"},
    "ct2138": {"name": "TSCD vo hinh khac", "tk": "2138", "parent": "213"},
    "ct214":  {"name": "Hao mon TSCD", "tk": "214", "loai": "TS_AM"},
    "ct2141": {"name": "Hao mon TSCD huu hinh", "tk": "2141", "parent": "214"},
    "ct2142": {"name": "Hao mon TSCD thue TC", "tk": "2142", "parent": "214"},
    "ct2143": {"name": "Hao mon TSCD vo hinh", "tk": "2143", "parent": "214"},
    "ct2147": {"name": "Hao mon BDS dau tu", "tk": "2147", "parent": "214"},
    "ct217":  {"name": "Bat dong san dau tu", "tk": "217", "loai": "TS"},
    "ct221":  {"name": "Dau tu vao cong ty con", "tk": "221", "loai": "TS"},
    "ct222":  {"name": "Dau tu vao cong ty lien doanh, lien ket", "tk": "222", "loai": "TS"},
    "ct228":  {"name": "Dau tu khac", "tk": "228", "loai": "TS"},
    "ct229":  {"name": "Du phong ton that tai san", "tk": "229", "loai": "TS_DP"},
    "ct241":  {"name": "XDCB do dang", "tk": "241", "loai": "TS"},
    "ct2411": {"name": "Mua sam TSCD", "tk": "2411", "parent": "241"},
    "ct2412": {"name": "Xay dung co ban", "tk": "2412", "parent": "241"},
    "ct2413": {"name": "Sua chua lon TSCD", "tk": "2413", "parent": "241"},
    "ct242":  {"name": "Chi phi tra truoc", "tk": "242", "loai": "TS"},
    "ct243":  {"name": "Tai san thue thu nhap hoan lai", "tk": "243", "loai": "TS"},
    "ct244":  {"name": "Cau cam co, ky cuoc, ky quy", "tk": "244", "loai": "TS"},

    # TK Loai 3 - No phai tra
    "ct331":  {"name": "Phai tra cho nguoi ban", "tk": "331", "loai": "LK"},
    "ct333":  {"name": "Thue va cac khoan phai nop NN", "tk": "333", "loai": "NV"},
    "ct3331": {"name": "Thue GTGT phai nop", "tk": "3331", "parent": "333"},
    "ct33311": {"name": "Thue GTGT dau ra", "tk": "33311", "parent": "3331"},
    "ct3332": {"name": "Thue tieu thu dac biet", "tk": "3332", "parent": "333"},
    "ct3333": {"name": "Thue xuat, nhap khau", "tk": "3333", "parent": "333"},
    "ct3334": {"name": "Thue TNDN", "tk": "3334", "parent": "333"},
    "ct3335": {"name": "Thue TNCN", "tk": "3335", "parent": "333"},
    "ct3336": {"name": "Thue tai nguyen", "tk": "3336", "parent": "333"},
    "ct3337": {"name": "Thue nha dat, tien thue dat", "tk": "3337", "parent": "333"},
    "ct3338": {"name": "Thue bao ve moi truong va cac loai thue khac", "tk": "3338", "parent": "333"},
    "ct3339": {"name": "Phi, le phi va cac khoan phai nop khac", "tk": "3339", "parent": "333"},
    "ct334":  {"name": "Phai tra nguoi lao dong", "tk": "334", "loai": "NV"},
    "ct335":  {"name": "Chi phi phai tra", "tk": "335", "loai": "NV"},
    "ct336":  {"name": "Phai tra noi bo", "tk": "336", "loai": "NV"},
    "ct337":  {"name": "Thanh toan theo tien do ke hoach hop dong XD", "tk": "337", "loai": "NV"},
    "ct338":  {"name": "Phai tra, phai nop khac", "tk": "338", "loai": "NV"},
    "ct3381": {"name": "Tai san thua cho xu ly", "tk": "3381", "parent": "338"},
    "ct3382": {"name": "Kinh phi cong doan", "tk": "3382", "parent": "338"},
    "ct3383": {"name": "Bao hiem xa hoi", "tk": "3383", "parent": "338"},
    "ct3384": {"name": "Bao hiem y te", "tk": "3384", "parent": "338"},
    "ct3385": {"name": "Phai tra ve co phan hoa", "tk": "3385", "parent": "338"},
    "ct3386": {"name": "Bao hiem that nghiep", "tk": "3386", "parent": "338"},
    "ct3387": {"name": "Doanh thu chua thuc hien", "tk": "3387", "parent": "338"},
    "ct3388": {"name": "Phai tra, phai nop khac", "tk": "3388", "parent": "338"},
    "ct341":  {"name": "Vay va no thue tai chinh", "tk": "341", "loai": "NV"},
    "ct3411": {"name": "Cac khoan di vay", "tk": "3411", "parent": "341"},
    "ct3412": {"name": "No thue tai chinh", "tk": "3412", "parent": "341"},
    "ct343":  {"name": "Trai phieu phat hanh", "tk": "343", "loai": "NV"},
    "ct344":  {"name": "Nhan ky quy, ky cuoc", "tk": "344", "loai": "NV"},
    "ct347":  {"name": "Thue thu nhap hoan lai phai tra", "tk": "347", "loai": "NV"},
    "ct352":  {"name": "Du phong phai tra", "tk": "352", "loai": "NV"},
    "ct353":  {"name": "Quy khen thuong, phuc loi", "tk": "353", "loai": "NV"},
    "ct356":  {"name": "Quy phat trien KH&CN", "tk": "356", "loai": "NV"},

    # TK Loai 4 - Von chu so huu
    "ct411":  {"name": "Von dau tu cua CSH", "tk": "411", "loai": "NV"},
    "ct4111": {"name": "Von gop cua CSH", "tk": "4111", "parent": "411"},
    "ct4112": {"name": "Thang du von co phan", "tk": "4112", "parent": "411"},
    "ct4113": {"name": "Quyen chon chuyen doi trai phieu", "tk": "4113", "parent": "411"},
    "ct4118": {"name": "Von khac", "tk": "4118", "parent": "411"},
    "ct412":  {"name": "Chenh lech danh gia lai tai san", "tk": "412", "loai": "NV"},
    "ct413":  {"name": "Chenh lech ty gia hoi doai", "tk": "413", "loai": "NV"},
    "ct414":  {"name": "Quy dau tu phat trien", "tk": "414", "loai": "NV"},
    "ct417":  {"name": "Quy du phong tai chinh", "tk": "417", "loai": "NV"},
    "ct418":  {"name": "Cac quy khac thuoc VCSH", "tk": "418", "loai": "NV"},
    "ct419":  {"name": "Co phieu quy", "tk": "419", "loai": "NV_AM"},
    "ct421":  {"name": "Loi nhuan sau thue chua phan phoi", "tk": "421", "loai": "LK"},
    "ct4211": {"name": "LNST chua PP nam truoc", "tk": "4211", "parent": "421"},
    "ct4212": {"name": "LNST chua PP nam nay", "tk": "4212", "parent": "421"},
    "ct441":  {"name": "Nguon von dau tu XDCB", "tk": "441", "loai": "NV"},
    "ct461":  {"name": "Nguon kinh phi su nghiep", "tk": "461", "loai": "NV"},
    "ct466":  {"name": "Nguon kinh phi da hinh thanh TSCD", "tk": "466", "loai": "NV"},

    # TK Loai 5 - Doanh thu
    "ct511":  {"name": "Doanh thu ban hang va CCDV", "tk": "511", "loai": "DT"},
    "ct515":  {"name": "Doanh thu hoat dong tai chinh", "tk": "515", "loai": "DT"},
    "ct521":  {"name": "Cac khoan giam tru doanh thu", "tk": "521", "loai": "DT_AM"},

    # TK Loai 6 - Chi phi (TT200 tach rieng 641 va 642)
    "ct621":  {"name": "Chi phi nguyen vat lieu truc tiep", "tk": "621", "loai": "CP"},
    "ct622":  {"name": "Chi phi nhan cong truc tiep", "tk": "622", "loai": "CP"},
    "ct623":  {"name": "Chi phi su dung may thi cong", "tk": "623", "loai": "CP"},
    "ct627":  {"name": "Chi phi san xuat chung", "tk": "627", "loai": "CP"},
    "ct632":  {"name": "Gia von hang ban", "tk": "632", "loai": "CP"},
    "ct635":  {"name": "Chi phi tai chinh", "tk": "635", "loai": "CP"},
    "ct641":  {"name": "Chi phi ban hang", "tk": "641", "loai": "CP"},
    "ct642":  {"name": "Chi phi quan ly doanh nghiep", "tk": "642", "loai": "CP"},

    # TK Loai 7 - Thu nhap khac
    "ct711":  {"name": "Thu nhap khac", "tk": "711", "loai": "DT"},

    # TK Loai 8 - Chi phi khac
    "ct811":  {"name": "Chi phi khac", "tk": "811", "loai": "CP"},
    "ct821":  {"name": "Chi phi thue TNDN", "tk": "821", "loai": "CP"},
    "ct8211": {"name": "Chi phi thue TNDN hien hanh", "tk": "8211", "parent": "821"},
    "ct8212": {"name": "Chi phi thue TNDN hoan lai", "tk": "8212", "parent": "821"},

    # TK Loai 9 - Xac dinh KQKD
    "ct911":  {"name": "Xac dinh ket qua kinh doanh", "tk": "911", "loai": "XDKQ"},
}
