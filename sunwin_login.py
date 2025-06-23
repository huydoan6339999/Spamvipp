import requests

def login_to_sunwin(username, password):
    url = "https://web.sun.win/"  # Cần chính xác lại URL
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    data = {
        "username": username,
        "password": password
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200 and "token" in res.text:
            return {"success": True, "token": res.json()["token"]}
        else:
            return {"success": False, "message": res.text}
    except Exception as e:
        return {"success": False, "message": str(e)}
