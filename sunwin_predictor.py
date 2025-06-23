def predict_outcome(session_numbers):
    last = session_numbers[-1]
    seq = "".join(str(x) for x in session_numbers[-3:]) if len(session_numbers) >= 3 else ""

    if last == 3:
        return "100% Xỉu ✅"
    elif last == 4:
        return "68% Xỉu / 32% Tài"
    elif last == 5:
        return "100% Xỉu ✅"
    elif last == 6:
        return "Đến con 6 nên nghỉ tay vì hay bịp"
    elif last == 7:
        if seq in ["124", "223", "133"]:
            return "89% Xỉu ✅"
        else:
            return "Tài (khác 124, 223, 133)"
    elif last == 8:
        if seq == "134":
            return "Auto ra Xỉu ✅"
        else:
            return "Còn lại: Tài hết"
    elif last == 9:
        if seq == "234":
            return "Ra con 234: Xỉu ✅"
        else:
            return "Còn lại: Tài 50/50"
    elif last == 10:
        return "Auto ra Xỉu ✅ (trừ khi trước đó là cầu đen → ra 12-13-11)"
    elif last == 11:
        return "Nghỉ tay, cầu nát"
    elif last == 12:
        if seq in ["246", "156", "336", "255"]:
            return "Auto ra Xỉu ✅"
        else:
            return "Tài"
    elif last == 13:
        if seq in ["553", "661", "531", "631"]:
            return "Auto ra Xỉu ✅"
        else:
            return "Tài"
    elif last == 14:
        return "Tuỳ phiên, 50/50"
    elif last == 15:
        return "Auto ra Tài ✅"
    elif last == 16:
        return "Xỉu"
    elif last == 17:
        return "Có thể bay xuống 10, cẩn thận"
    elif last == 18:
        return "Tài"
    else:
        return "Không có dữ liệu cho phiên này"
