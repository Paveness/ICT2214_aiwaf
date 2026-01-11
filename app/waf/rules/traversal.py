from app.waf.decisions import Decision, Action


def traversal_checks(req):
    path = req.decoded_path.lower()

    # Unix-style traversal
    if "/../" in path or path.endswith("/.."):
        return Decision(
            Action.BLOCK,
            ["path_traversal:dotdot"],
            status_code=403,
        )

    # Windows-style traversal
    if "\\..\\" in path or path.endswith("\\.."):
        return Decision(
            Action.BLOCK,
            ["path_traversal:backslash"],
            status_code=403,
        )

    return None
