import re
from urllib.parse import unquote_plus
import string
_SUSPICIOUS_CHARS = set(string.punctuation)
# _SUSPICIOUS_CHARS = set(";|&`$<>(){}")
_HEX_RE = re.compile(r"%[0-9a-fA-F]{2}")

def extract_features(
    *,
    method: str,
    raw_path: str,
    decoded_path: str,
    normalized_path: str,
    raw_query: str,
    headers: dict,
    body_len: int,
    body_text: str,
) -> dict:
    # NOTE: avoid logging raw secrets; features only.
    q = raw_query or ""
    qp = unquote_plus(q)  # basic decode for signal; you can also use your safe_unquote

    ua = headers.get("user-agent", "")
    ct = headers.get("content-type", "")

    # simple “character class” counts
    def count_set(s: str, charset: set) -> int:
        return sum(1 for c in s if c in charset)
    
    def count_regex(s: str, rx: re.Pattern) -> int:
        return len(rx.findall(s or ""))

    def count_pred(s: str, pred) -> int:
        return sum(1 for c in (s or "") if pred(c))

    body = body_text or ""

    feat = {
        # method/categoricals (we’ll encode later)
        "method": (method or "").upper(),

        # path / query shape
        "raw_path_len": len(raw_path or ""),
        "decoded_path_len": len(decoded_path or ""),
        "normalized_path_len": len(normalized_path or ""),
        "path_slash_count": (normalized_path or "").count("/"),
        "path_dot_count": (normalized_path or "").count("."),
        "path_pct_count": (raw_path or "").count("%"),
        "path_hex_pct_count": len(_HEX_RE.findall(raw_path or "")),

        "query_len": len(q),
        "query_pct_count": q.count("%"),
        "query_hex_pct_count": len(_HEX_RE.findall(q)),
        "query_amp_count": q.count("&"),
        "query_eq_count": q.count("="),

        # suspicious operators (helps the model)
        "query_suspicious_char_count": count_set(qp, _SUSPICIOUS_CHARS),
        "path_suspicious_char_count": count_set((decoded_path or ""), _SUSPICIOUS_CHARS),

        # headers/body shape
        "header_count": len(headers),
        "has_cookie": 1 if "cookie" in {k.lower() for k in headers.keys()} else 0,
        "ua_len": len(ua),
        "ct_len": len(ct),
        "body_len": int(body_len or 0),
    }

    feat.update({
        "body_pct_count": body.count("%"),
        "body_hex_pct_count": count_regex(body, _HEX_RE),
        "body_suspicious_char_count": count_set(body, _SUSPICIOUS_CHARS),
        "body_alpha_count": count_pred(body, str.isalpha),
        "body_digit_count": count_pred(body, str.isdigit),
        "ct_is_json": 1 if "application/json" in (ct or "").lower() else 0,
        "ct_is_form": 1 if "application/x-www-form-urlencoded" in (ct or "").lower() else 0,
    })

    return feat
