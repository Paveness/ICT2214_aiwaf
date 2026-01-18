from app.waf.decisions import Decision, Action


def traversal_checks(req) -> Decision | None:
    path = (req.decoded_path or "").lower()
    body = (req.body_text or "").lower()

    # ===== Path checks (existing) =====
    # Unix-style traversal in path
    if "/../" in path or path.endswith("/.."):
        return Decision(
            Action.BLOCK,
            ["path_traversal:path:dotdot"],
            status_code=403,
        )

    # Windows-style traversal in path
    if "\\..\\" in path or path.endswith("\\.."):
        return Decision(
            Action.BLOCK,
            ["path_traversal:path:backslash"],
            status_code=403,
        )

    # ===== Body checks (new) =====
    if body:
        # Unix-style traversal in body
        if "/../" in body or body.endswith("/..") or "../" in body:
            return Decision(
                Action.BLOCK,
                ["path_traversal:body:dotdot"],
                status_code=403,
            )

        # Windows-style traversal in body
        if "\\..\\" in body or body.endswith("\\..") or "..\\" in body:
            return Decision(
                Action.BLOCK,
                ["path_traversal:body:backslash"],
                status_code=403,
            )

    return None

