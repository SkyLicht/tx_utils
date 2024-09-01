def translate_andon_data(data: list[dict]) -> list[dict]:
    _clean_data = []
    for _record in data:
        _clean_data.append({
            "alerts_id": int(_record.get("alerts_id")),
            "id": _record.get("id"),
            "date": _record.get("alerts__start__date"),
            "shift": int(_record.get("alerts__start__shift")),
            "start": _record.get("start"),
            "first": _record.get("first"),
            "finish": _record.get("finish"),
            "alert_min": _record.get("alert_mins"),
            "total_min": _record.get("total_mins"),
            "downtime": _record.get("real_downtime"),
            "real_downtime": _record.get("real_downtime"),
            "area_name": translate_area_name(_record.get("alerts__areas__name")),
            "category_name": _record.get("alerts__categories__name"),
            "location": _record.get("alerts__location"),
            "status_name": _record.get("alerts__status__name"),
            "owners_name": str(_record.get("alerts_owners__name"))[3:],
            "message": _record.get("message"),
            "reason": _record.get("alerts__reason"),
            "station": _record.get("station"),
            "level_1": _record.get("level_1"),
            "level_2": _record.get("level_2"),
            "employee_id": int(_record.get("employees_id")),
            "total_alerts": 1,
        })
    return _clean_data

def translate_area_name(area_name: str) -> str:
    if area_name is None:
        return ""
    if "Backend" in area_name :
        return "Packing"
    if "Frontend" in area_name:
        return "Smt"
    return area_name
