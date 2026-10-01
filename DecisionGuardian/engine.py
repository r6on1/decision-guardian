import re
import uuid
from datetime import datetime


LANGUAGES = {
    "en": "English",
    "ar": "العربية",
    "fr": "Français",
    "nl": "Nederlands",
    "hi": "हिन्दी",
    "zh": "中文",
}


PATTERNS = {
    "urgency": {
        "en": [
            r"\burgent\b",
            r"\bimmediately\b",
            r"\bas soon as possible\b",
            r"\bwithin \d+ (minutes?|hours?)\b",
            r"\byour account (will be|has been|is) suspended\b",
            r"\baccount (will be|has been|is) suspended\b",
            r"\baction required\b",
            r"\bfinal warning\b",
        ],
        "ar": [
            r"عاجل",
            r"فوراً",
            r"على الفور",
            r"خلال\s+\d+\s*(دقيقة|دقائق|ساعة|ساعات)",
            r"سيتم تعليق حسابك",
            r"تم تعليق حسابك",
            r"حسابك.*معلق",
            r"إجراء مطلوب",
            r"تحذير أخير",
        ],
        "fr": [
            r"\burgent\b",
            r"\bimmédiatement\b",
            r"\baction requise\b",
            r"\bdernier avertissement\b",
            r"compte.*suspendu",
        ],
        "nl": [
            r"\bdringend\b",
            r"\bonmiddellijk\b",
            r"\bactie vereist\b",
            r"\blaatste waarschuwing\b",
            r"account.*opgeschort",
        ],
        "hi": [
            r"तुरंत",
            r"अत्यावश्यक",
            r"कार्रवाई आवश्यक",
            r"अंतिम चेतावनी",
            r"खाता.*निलंबित",
        ],
        "zh": [
            r"紧急",
            r"立即",
            r"马上",
            r"需要立即操作",
            r"最后警告",
            r"账户.*暂停",
        ],
    },

    "credential": {
        "en": [
            r"\benter your password\b",
            r"\bprovide your password\b",
            r"\bverify your password\b",
            r"\benter credentials\b",
            r"\benter your login\b",
            r"\blog in\b",
            r"\bsign in\b",
            r"\busername and password\b",
        ],
        "ar": [
            r"أدخل كلمة المرور",
            r"أدخل بيانات الدخول",
            r"تحقق من كلمة المرور",
            r"سجل الدخول",
            r"تسجيل الدخول",
            r"اسم المستخدم.*كلمة المرور",
        ],
        "fr": [
            r"entrez votre mot de passe",
            r"identifiants",
            r"connectez-vous",
            r"nom d'utilisateur.*mot de passe",
        ],
        "nl": [
            r"voer.*wachtwoord.*in",
            r"inloggegevens",
            r"log.*in",
            r"gebruikersnaam.*wachtwoord",
        ],
        "hi": [
            r"पासवर्ड दर्ज करें",
            r"लॉगिन करें",
            r"लॉग इन",
            r"उपयोगकर्ता नाम.*पासवर्ड",
        ],
        "zh": [
            r"输入密码",
            r"登录",
            r"登入",
            r"用户名.*密码",
        ],
    },

    "otp": {
        "en": [
            r"\bOTP\b",
            r"\bone[- ]time password\b",
            r"\bverification code\b",
            r"\bsecurity code\b",
            r"\b6[- ]digit code\b",
        ],
        "ar": [
            r"\bOTP\b",
            r"رمز التحقق",
            r"رمز أمان",
            r"رمز لمرة واحدة",
            r"رمز مكون من 6 أرقام",
        ],
        "fr": [
            r"\bOTP\b",
            r"code de vérification",
            r"code de sécurité",
        ],
        "nl": [
            r"\bOTP\b",
            r"verificatiecode",
            r"beveiligingscode",
        ],
        "hi": [
            r"\bOTP\b",
            r"सत्यापन कोड",
            r"सुरक्षा कोड",
        ],
        "zh": [
            r"\bOTP\b",
            r"验证码",
            r"安全码",
            r"一次性密码",
        ],
    },

    "financial": {
        "en": [
            r"\btransfer money\b",
            r"\bmake a transfer\b",
            r"\bnew beneficiary\b",
            r"\badd beneficiary\b",
            r"\bsend payment\b",
            r"\bpay now\b",
            r"\bbank transfer\b",
        ],
        "ar": [
            r"تحويل أموال",
            r"حوّل المبلغ",
            r"إجراء تحويل",
            r"مستفيد جديد",
            r"إضافة مستفيد",
            r"إرسال دفعة",
            r"تحويل بنكي",
            r"ادفع الآن",
        ],
        "fr": [
            r"transférer de l'argent",
            r"nouveau bénéficiaire",
            r"virement bancaire",
            r"effectuer un paiement",
        ],
        "nl": [
            r"geld overmaken",
            r"nieuwe begunstigde",
            r"bankoverschrijving",
            r"betaling uitvoeren",
        ],
        "hi": [
            r"पैसे ट्रांसफर",
            r"नया लाभार्थी",
            r"बैंक ट्रांसफर",
            r"भुगतान करें",
        ],
        "zh": [
            r"转账",
            r"新收款人",
            r"银行转账",
            r"付款",
        ],
    },
}


TRANSLATIONS = {
    "en": {
        "normal": "Normal",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical",
        "stop": "STOP BEFORE CONTINUING",
        "safe": "No significant decision risk detected.",
        "external": "External destination detected",
        "credential": "Credential request detected",
        "otp": "OTP / verification code request detected",
        "financial": "Financial action detected",
        "urgency": "Urgency or pressure detected",
        "analyze": "Analyze Decision Risk",
    },
    "ar": {
        "normal": "طبيعي",
        "low": "منخفض",
        "medium": "متوسط",
        "high": "مرتفع",
        "critical": "حرج",
        "stop": "توقف قبل المتابعة",
        "safe": "لم يتم اكتشاف خطر مهم على القرار.",
        "external": "تم اكتشاف وجهة خارجية",
        "credential": "تم اكتشاف طلب بيانات دخول",
        "otp": "تم اكتشاف طلب رمز تحقق / OTP",
        "financial": "تم اكتشاف إجراء مالي",
        "urgency": "تم اكتشاف ضغط أو استعجال",
        "analyze": "تحليل مخاطر القرار",
    },
    "fr": {
        "normal": "Normal",
        "low": "Faible",
        "medium": "Moyen",
        "high": "Élevé",
        "critical": "Critique",
        "stop": "ARRÊTEZ-VOUS AVANT DE CONTINUER",
        "safe": "Aucun risque décisionnel important détecté.",
        "external": "Destination externe détectée",
        "credential": "Demande d'identifiants détectée",
        "otp": "Demande de code OTP détectée",
        "financial": "Action financière détectée",
        "urgency": "Pression ou urgence détectée",
        "analyze": "Analyser le risque",
    },
    "nl": {
        "normal": "Normaal",
        "low": "Laag",
        "medium": "Gemiddeld",
        "high": "Hoog",
        "critical": "Kritiek",
        "stop": "STOP VOORDAT U DOORGAAT",
        "safe": "Geen significant beslisrisico gedetecteerd.",
        "external": "Externe bestemming gedetecteerd",
        "credential": "Verzoek om inloggegevens gedetecteerd",
        "otp": "OTP-verzoek gedetecteerd",
        "financial": "Financiële actie gedetecteerd",
        "urgency": "Druk of urgentie gedetecteerd",
        "analyze": "Beslisrisico analyseren",
    },
    "hi": {
        "normal": "सामान्य",
        "low": "कम",
        "medium": "मध्यम",
        "high": "उच्च",
        "critical": "गंभीर",
        "stop": "जारी रखने से पहले रुकें",
        "safe": "कोई महत्वपूर्ण निर्णय जोखिम नहीं मिला।",
        "external": "बाहरी गंतव्य मिला",
        "credential": "लॉगिन जानकारी का अनुरोध मिला",
        "otp": "OTP अनुरोध मिला",
        "financial": "वित्तीय कार्रवाई मिली",
        "urgency": "तत्कालता या दबाव मिला",
        "analyze": "निर्णय जोखिम का विश्लेषण करें",
    },
    "zh": {
        "normal": "正常",
        "low": "低",
        "medium": "中",
        "high": "高",
        "critical": "严重",
        "stop": "继续之前请停止",
        "safe": "未发现明显的决策风险。",
        "external": "检测到外部目的地",
        "credential": "检测到凭据请求",
        "otp": "检测到 OTP / 验证码请求",
        "financial": "检测到金融操作",
        "urgency": "检测到紧迫性或压力",
        "analyze": "分析决策风险",
    },
}


def normalize(text):
    return re.sub(r"\s+", " ", text.strip())


def detect_language(text):
    if re.search(r"[\u0600-\u06FF]", text):
        return "ar"

    if re.search(r"[\u4E00-\u9FFF]", text):
        return "zh"

    if re.search(r"[\u0900-\u097F]", text):
        return "hi"

    lower = text.lower()

    french_words = [
        "bonjour", "urgent", "mot de passe",
        "vérification", "compte", "paiement"
    ]

    dutch_words = [
        "wachtwoord", "account", "betaling",
        "dringend", "verificatie"
    ]

    if any(word in lower for word in french_words):
        return "fr"

    if any(word in lower for word in dutch_words):
        return "nl"

    return "en"


def detect_events(text, language):
    events = []

    # External URL
    urls = re.findall(
        r"https?://[^\s<>\"]+",
        text,
        flags=re.IGNORECASE
    )

    if urls:
        events.append({
            "type": "EXTERNAL_DESTINATION",
            "label": "External destination",
            "evidence": urls[0],
            "severity": 15
        })

    # Urgency
    for pattern in PATTERNS["urgency"].get(language, []):
        if re.search(pattern, text, re.IGNORECASE):
            events.append({
                "type": "URGENCY",
                "label": "Urgency / pressure",
                "evidence": pattern,
                "severity": 10
            })
            break

    # Credentials
    for pattern in PATTERNS["credential"].get(language, []):
        if re.search(pattern, text, re.IGNORECASE):
            events.append({
                "type": "CREDENTIAL_REQUEST",
                "label": "Credential request",
                "evidence": pattern,
                "severity": 30
            })
            break

    # OTP
    for pattern in PATTERNS["otp"].get(language, []):
        if re.search(pattern, text, re.IGNORECASE):
            events.append({
                "type": "OTP_REQUEST",
                "label": "OTP / verification request",
                "evidence": pattern,
                "severity": 25
            })
            break

    # Financial
    for pattern in PATTERNS["financial"].get(language, []):
        if re.search(pattern, text, re.IGNORECASE):
            events.append({
                "type": "FINANCIAL_ACTION",
                "label": "Financial action",
                "evidence": pattern,
                "severity": 35
            })
            break

    return events


def extract_iocs(text):
    urls = re.findall(
        r"https?://[^\s<>\"]+",
        text,
        flags=re.IGNORECASE
    )

    emails = re.findall(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text
    )

    ips = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        text
    )

    domains = []

    for url in urls:
        match = re.search(
            r"https?://([^/:]+)",
            url,
            re.IGNORECASE
        )
        if match:
            domains.append(match.group(1))

    return {
        "urls": list(dict.fromkeys(urls)),
        "domains": list(dict.fromkeys(domains)),
        "ips": list(dict.fromkeys(ips)),
        "emails": list(dict.fromkeys(emails)),
    }


def build_timeline(events):
    timeline = []

    for index, event in enumerate(events, start=1):
        timeline.append({
            "step": index,
            "event": event["type"],
            "label": event["label"],
            "evidence": event["evidence"]
        })

    return timeline


def dangerous_transitions(events):
    types = [event["type"] for event in events]
    dangerous = []

    dangerous_pairs = [
        ("EXTERNAL_DESTINATION", "CREDENTIAL_REQUEST"),
        ("EXTERNAL_DESTINATION", "OTP_REQUEST"),
        ("EXTERNAL_DESTINATION", "FINANCIAL_ACTION"),
        ("CREDENTIAL_REQUEST", "OTP_REQUEST"),
        ("OTP_REQUEST", "FINANCIAL_ACTION"),
        ("URGENCY", "CREDENTIAL_REQUEST"),
        ("URGENCY", "OTP_REQUEST"),
        ("URGENCY", "FINANCIAL_ACTION"),
    ]

    for first, second in dangerous_pairs:
        if first in types and second in types:
            dangerous.append(f"{first} → {second}")

    return dangerous


def calculate_score(events, dangerous):
    score = sum(event["severity"] for event in events)

    score += len(dangerous) * 15

    types = {event["type"] for event in events}

    # Compound decision-risk pattern
    if (
        "EXTERNAL_DESTINATION" in types
        and "CREDENTIAL_REQUEST" in types
        and "OTP_REQUEST" in types
    ):
        score += 20

    if (
        "EXTERNAL_DESTINATION" in types
        and "FINANCIAL_ACTION" in types
    ):
        score += 20

    return min(score, 100)


def risk_level(score):
    if score >= 80:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 30:
        return "medium"
    if score >= 15:
        return "low"

    return "normal"


def mitre_mapping(events):
    mappings = []

    types = {event["type"] for event in events}

    if "EXTERNAL_DESTINATION" in types:
        mappings.append({
            "technique": "T1566",
            "name": "Phishing",
            "note": "Potential mapping based on external delivery/link behavior."
        })

    if "CREDENTIAL_REQUEST" in types:
        mappings.append({
            "technique": "T1056",
            "name": "Input Capture",
            "note": "Potential mapping where credentials are requested."
        })

    if "FINANCIAL_ACTION" in types:
        mappings.append({
            "technique": "T1204",
            "name": "User Execution",
            "note": "Potential mapping where the user is directed to perform an action."
        })

    return mappings


def recommendations(score, events, dangerous):
    recommendations = []

    types = {event["type"] for event in events}

    if score >= 50:
        recommendations.append(
            "Stop before entering credentials, OTP codes, or financial information."
        )

    if "EXTERNAL_DESTINATION" in types:
        recommendations.append(
            "Verify the destination through an independently trusted channel."
        )

    if "CREDENTIAL_REQUEST" in types:
        recommendations.append(
            "Do not submit passwords through an unexpected external link."
        )

    if "OTP_REQUEST" in types:
        recommendations.append(
            "Never share an OTP unless you initiated and understand the transaction."
        )

    if "FINANCIAL_ACTION" in types:
        recommendations.append(
            "Verify the beneficiary and transaction independently before approval."
        )

    if dangerous:
        recommendations.append(
            "Review the event sequence before continuing with the requested action."
        )

    if not recommendations:
        recommendations.append(
            "Continue using normal security awareness practices."
        )

    return recommendations


def intervention(score, language):
    if score >= 80:
        messages = {
            "en": "STOP. A high-risk decision sequence was detected.",
            "ar": "توقف. تم اكتشاف تسلسل قرار عالي الخطورة.",
            "fr": "ARRÊTEZ-VOUS. Une séquence à haut risque a été détectée.",
            "nl": "STOP. Een risicovolle beslisketen is gedetecteerd.",
            "hi": "रुकें। उच्च जोखिम वाला निर्णय क्रम पाया गया।",
            "zh": "请停止。检测到高风险决策链。",
        }
        return messages.get(language, messages["en"])

    if score >= 50:
        messages = {
            "en": "STOP BEFORE CONTINUING.",
            "ar": "توقف قبل المتابعة.",
            "fr": "ARRÊTEZ-VOUS AVANT DE CONTINUER.",
            "nl": "STOP VOORDAT U DOORGAAT.",
            "hi": "जारी रखने से पहले रुकें।",
            "zh": "继续之前请停止。",
        }
        return messages.get(language, messages["en"])

    return None


def analyze(text, selected_language=None):
    text = normalize(text)

    language = selected_language or detect_language(text)

    if language not in LANGUAGES:
        language = "en"

    events = detect_events(text, language)
    iocs = extract_iocs(text)
    timeline = build_timeline(events)
    dangerous = dangerous_transitions(events)
    score = calculate_score(events, dangerous)
    level = risk_level(score)

    transition = " → ".join(
        event["type"] for event in events
    )

    incident_id = "DG-" + uuid.uuid4().hex[:8].upper()

    return {
        "incident_id": incident_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "language": language,
        "language_name": LANGUAGES[language],
        "risk_score": score,
        "risk_level": level,
        "decision_transition": transition or "NORMAL_ACTIVITY",
        "events": events,
        "timeline": timeline,
        "dangerous_transitions": dangerous,
        "iocs": iocs,
        "mitre": mitre_mapping(events),
        "recommendations": recommendations(
            score,
            events,
            dangerous
        ),
        "intervention": intervention(
            score,
            language
        ),
    }