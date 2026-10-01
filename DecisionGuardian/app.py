
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
import copy

from engine import analyze
from database import (
    initialize_database,
    save_incident,
    get_incidents,
    get_statistics,
)

app = FastAPI(title="Decision Guardian")

BASE_DIR = Path(__file__).resolve().parent
TRANSLATIONS_FILE = BASE_DIR / "translations" / "translations.json"


# ============================================================
# TRANSLATIONS
# ============================================================

def load_translations():
    try:
        with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {}

        return data

    except Exception:
        return {}


TRANSLATIONS = load_translations()


# ============================================================
# CLEAN UI TRANSLATIONS
# ============================================================

UI_TRANSLATIONS = {
    "ar": {
        "name": "العربية",
        "dir": "rtl",
        "brand_subtitle": "حارس الأمن الرقمي",
        "badge": "أمانك الرقمي يبدأ بالوعي.",
        "hero_title_1": "اكتشف التهديدات الرقمية قبل أن تتحول إلى مخاطر.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "يراقب حارس الأمن الرقمي تسلسل الأحداث المشبوهة، ويكشف مؤشرات الاحتيال والأنشطة الخطرة، وينبّهك قبل إتمام الإجراءات الحساسة.",
        "user_mode": "المستخدم",
        "soc_mode": "مركز العمليات",
        "placeholder": "الصق هنا رسالة أو بريدًا إلكترونيًا أو رسالة نصية أو رابطًا أو اتصالًا مشبوهًا...",
        "analyze": "تحليل",
        "risk_score": "درجة الخطورة",
        "risk_level": "مستوى الخطورة",
        "incident_id": "معرّف الحادثة",
        "language": "اللغة",
        "decision_transition": "انتقال القرار",
        "dangerous_transitions": "الانتقالات الخطرة",
        "risk_factors": "عوامل الخطورة",
        "iocs": "مؤشرات الاختراق",
        "timeline": "الخط الزمني",
        "mitre": "MITRE ATT&CK",
        "recommendations": "التوصيات",
        "incident_history": "سجل الحوادث",
        "total": "الإجمالي",
        "high_critical": "مرتفع / حرج",
        "medium": "متوسط",
        "low_normal": "منخفض / طبيعي",
        "none_detected": "لم يتم اكتشاف أي عناصر.",
        "no_intervention": "لا يلزم اتخاذ إجراء وقائي.",
        "stop": "توقف لحظة وتحقق قبل المتابعة.",
        "please_enter": "يرجى إدخال رسالة.",
        "normal": "طبيعي",
        "low": "منخفض",
        "medium_level": "متوسط",
        "high": "مرتفع",
        "critical": "حرج",
        "external_destination": "تم اكتشاف وجهة خارجية",
        "credential_request": "تم اكتشاف طلب بيانات اعتماد",
        "otp_request": "تم اكتشاف طلب رمز تحقق لمرة واحدة",
        "financial_action": "تم اكتشاف إجراء مالي",
        "urgency": "تم اكتشاف ضغط أو استعجال",
        "verify_destination": "تحقق من الوجهة والرابط قبل المتابعة.",
        "protect_credentials": "لا تدخل كلمة المرور حتى تتحقق من الجهة المستلمة.",
        "protect_otp": "لا تشارك رمز التحقق لمرة واحدة مع أي شخص.",
        "verify_financial": "تحقق من المستفيد والمبلغ وتفاصيل المعاملة قبل المتابعة.",
        "avoid_pressure": "لا تتخذ قرارًا حساسًا تحت الضغط.",
        "review_sequence": "راجع تسلسل الإجراءات كاملًا قبل المتابعة.",
        "unknown_event": "حدث أمني غير معروف",
        "mitre_phishing": "التصيد الاحتيالي",
        "mitre_input": "التقاط المدخلات",
        "mitre_execution": "تنفيذ المستخدم",
        "analysis_failed": "تعذر إكمال التحليل.",
        "date": "التاريخ",
        "time": "الوقت",
        "footer": "Decision Guardian — حارس الأمن الرقمي"
    },

    "en": {
        "name": "English",
        "dir": "ltr",
        "brand_subtitle": "Digital Security Guardian",
        "badge": "Your digital safety starts with awareness.",
        "hero_title_1": "Discover digital threats before they become risks.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian monitors suspicious event sequences, detects signs of fraud and risky activity, and alerts you before sensitive actions are completed.",
        "user_mode": "User",
        "soc_mode": "SOC",
        "placeholder": "Paste a message, email, SMS, URL, or suspicious communication here...",
        "analyze": "Analyze",
        "risk_score": "Risk Score",
        "risk_level": "Risk Level",
        "incident_id": "Incident ID",
        "language": "Language",
        "decision_transition": "Decision Transition",
        "dangerous_transitions": "Dangerous Transitions",
        "risk_factors": "Risk Factors",
        "iocs": "Indicators of Compromise",
        "timeline": "Timeline",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Recommendations",
        "incident_history": "Incident History",
        "total": "Total",
        "high_critical": "High / Critical",
        "medium": "Medium",
        "low_normal": "Low / Normal",
        "none_detected": "None detected.",
        "no_intervention": "No intervention required.",
        "stop": "Stop and verify before continuing.",
        "please_enter": "Please enter a message.",
        "normal": "Normal",
        "low": "Low",
        "medium_level": "Medium",
        "high": "High",
        "critical": "Critical",
        "external_destination": "External destination detected",
        "credential_request": "Credential request detected",
        "otp_request": "OTP request detected",
        "financial_action": "Financial action detected",
        "urgency": "Urgency or pressure detected",
        "verify_destination": "Verify the destination and link before continuing.",
        "protect_credentials": "Do not enter your password until you verify the recipient.",
        "protect_otp": "Never share a one-time verification code with anyone.",
        "verify_financial": "Verify the beneficiary, amount, and transaction details before proceeding.",
        "avoid_pressure": "Do not make a sensitive decision under pressure.",
        "review_sequence": "Review the entire sequence before proceeding.",
        "unknown_event": "Unknown security event",
        "mitre_phishing": "Phishing",
        "mitre_input": "Input Capture",
        "mitre_execution": "User Execution",
        "analysis_failed": "Analysis failed.",
        "date": "Date",
        "time": "Time",
        "footer": "Decision Guardian — Digital Security Guardian"
    },

    "fr": {
        "name": "Français",
        "dir": "ltr",
        "brand_subtitle": "Gardien de la sécurité numérique",
        "badge": "Votre sécurité numérique commence par la vigilance.",
        "hero_title_1": "Détectez les menaces numériques avant qu’elles ne deviennent des risques.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian surveille les séquences d’événements suspectes, détecte les signes de fraude et les activités à risque, et vous alerte avant toute action sensible.",
        "user_mode": "Utilisateur",
        "soc_mode": "SOC",
        "placeholder": "Collez ici un message, un e-mail, un SMS, une URL ou une communication suspecte...",
        "analyze": "Analyser",
        "risk_score": "Score de risque",
        "risk_level": "Niveau de risque",
        "incident_id": "ID de l'incident",
        "language": "Langue",
        "decision_transition": "Transition de décision",
        "dangerous_transitions": "Transitions dangereuses",
        "risk_factors": "Facteurs de risque",
        "iocs": "Indicateurs de compromission",
        "timeline": "Chronologie",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Recommandations",
        "incident_history": "Historique des incidents",
        "none_detected": "Aucun élément détecté.",
        "no_intervention": "Aucune intervention requise.",
        "stop": "Arrêtez-vous et vérifiez avant de continuer.",
        "please_enter": "Veuillez saisir un message.",
        "normal": "Normal",
        "low": "Faible",
        "medium_level": "Moyen",
        "high": "Élevé",
        "critical": "Critique",
        "external_destination": "Destination externe détectée",
        "credential_request": "Demande d'identifiants détectée",
        "otp_request": "Demande de code à usage unique détectée",
        "financial_action": "Action financière détectée",
        "urgency": "Urgence ou pression détectée",
        "verify_destination": "Vérifiez la destination et le lien avant de continuer.",
        "protect_credentials": "N'entrez pas votre mot de passe avant d'avoir vérifié le destinataire.",
        "protect_otp": "Ne partagez jamais un code de vérification à usage unique.",
        "verify_financial": "Vérifiez le bénéficiaire, le montant et les détails de la transaction.",
        "avoid_pressure": "Ne prenez pas de décision sensible sous pression.",
        "review_sequence": "Examinez toute la séquence avant de continuer.",
        "unknown_event": "Événement de sécurité inconnu",
        "mitre_phishing": "Hameçonnage",
        "mitre_input": "Capture des entrées",
        "mitre_execution": "Exécution par l'utilisateur",
        "analysis_failed": "L'analyse n'a pas pu être terminée.",
        "date": "Date",
        "time": "Heure",
        "footer": "Decision Guardian — Gardien de la sécurité numérique"
    },

    "es": {
        "name": "Español",
        "dir": "ltr",
        "brand_subtitle": "Guardián de la seguridad digital",
        "badge": "Tu seguridad digital comienza con la conciencia.",
        "hero_title_1": "Detecta las amenazas digitales antes de que se conviertan en riesgos.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian supervisa secuencias de eventos sospechosas, detecta señales de fraude y actividades riesgosas, y te alerta antes de completar acciones sensibles.",
        "user_mode": "Usuario",
        "soc_mode": "SOC",
        "placeholder": "Pega aquí un mensaje, correo electrónico, SMS, URL o comunicación sospechosa...",
        "analyze": "Analizar",
        "risk_score": "Puntuación de riesgo",
        "risk_level": "Nivel de riesgo",
        "incident_id": "ID del incidente",
        "language": "Idioma",
        "decision_transition": "Transición de decisión",
        "dangerous_transitions": "Transiciones peligrosas",
        "risk_factors": "Factores de riesgo",
        "iocs": "Indicadores de compromiso",
        "timeline": "Línea de tiempo",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Recomendaciones",
        "incident_history": "Historial de incidentes",
        "none_detected": "No se detectaron elementos.",
        "no_intervention": "No se requiere intervención.",
        "stop": "Detente y verifica antes de continuar.",
        "please_enter": "Introduce un mensaje.",
        "normal": "Normal",
        "low": "Bajo",
        "medium_level": "Medio",
        "high": "Alto",
        "critical": "Crítico",
        "external_destination": "Destino externo detectado",
        "credential_request": "Solicitud de credenciales detectada",
        "otp_request": "Solicitud de código de un solo uso detectada",
        "financial_action": "Acción financiera detectada",
        "urgency": "Urgencia o presión detectada",
        "verify_destination": "Verifica el destino y el enlace antes de continuar.",
        "protect_credentials": "No introduzcas tu contraseña hasta verificar al destinatario.",
        "protect_otp": "Nunca compartas un código de verificación de un solo uso.",
        "verify_financial": "Verifica el beneficiario, el importe y los detalles de la transacción.",
        "avoid_pressure": "No tomes una decisión sensible bajo presión.",
        "review_sequence": "Revisa toda la secuencia antes de continuar.",
        "unknown_event": "Evento de seguridad desconocido",
        "mitre_phishing": "Suplantación de identidad",
        "mitre_input": "Captura de entrada",
        "mitre_execution": "Ejecución por el usuario",
        "analysis_failed": "No se pudo completar el análisis.",
        "date": "Fecha",
        "time": "Hora",
        "footer": "Decision Guardian — Guardián de la seguridad digital"
    },

    "de": {
        "name": "Deutsch",
        "dir": "ltr",
        "brand_subtitle": "Wächter der digitalen Sicherheit",
        "badge": "Deine digitale Sicherheit beginnt mit Aufmerksamkeit.",
        "hero_title_1": "Erkenne digitale Bedrohungen, bevor sie zu Risiken werden.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian überwacht verdächtige Ereignisfolgen, erkennt Anzeichen von Betrug und riskanten Aktivitäten und warnt dich vor dem Abschluss sensibler Aktionen.",
        "user_mode": "Benutzer",
        "soc_mode": "SOC",
        "placeholder": "Füge hier eine Nachricht, E-Mail, SMS, URL oder verdächtige Kommunikation ein...",
        "analyze": "Analysieren",
        "risk_score": "Risikoscore",
        "risk_level": "Risikostufe",
        "incident_id": "Incident-ID",
        "language": "Sprache",
        "decision_transition": "Entscheidungsübergang",
        "dangerous_transitions": "Gefährliche Übergänge",
        "risk_factors": "Risikofaktoren",
        "iocs": "Kompromittierungsindikatoren",
        "timeline": "Zeitachse",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Empfehlungen",
        "incident_history": "Vorfallverlauf",
        "none_detected": "Keine Elemente erkannt.",
        "no_intervention": "Keine Intervention erforderlich.",
        "stop": "Halte an und überprüfe, bevor du fortfährst.",
        "please_enter": "Bitte gib eine Nachricht ein.",
        "normal": "Normal",
        "low": "Niedrig",
        "medium_level": "Mittel",
        "high": "Hoch",
        "critical": "Kritisch",
        "external_destination": "Externe Zieladresse erkannt",
        "credential_request": "Anforderung von Zugangsdaten erkannt",
        "otp_request": "Anforderung eines Einmalcodes erkannt",
        "financial_action": "Finanzielle Aktion erkannt",
        "urgency": "Dringlichkeit oder Druck erkannt",
        "verify_destination": "Überprüfe Ziel und Link, bevor du fortfährst.",
        "protect_credentials": "Gib dein Passwort erst ein, nachdem du den Empfänger überprüft hast.",
        "protect_otp": "Teile niemals einen Einmal-Bestätigungscode.",
        "verify_financial": "Überprüfe Empfänger, Betrag und Transaktionsdetails.",
        "avoid_pressure": "Treffe keine sensible Entscheidung unter Druck.",
        "review_sequence": "Überprüfe die gesamte Abfolge vor dem Fortfahren.",
        "unknown_event": "Unbekanntes Sicherheitsereignis",
        "mitre_phishing": "Phishing",
        "mitre_input": "Eingabeerfassung",
        "mitre_execution": "Benutzerausführung",
        "analysis_failed": "Die Analyse konnte nicht abgeschlossen werden.",
        "date": "Datum",
        "time": "Uhrzeit",
        "footer": "Decision Guardian — Wächter der digitalen Sicherheit"
    },

    "it": {
        "name": "Italiano",
        "dir": "ltr",
        "brand_subtitle": "Guardiano della sicurezza digitale",
        "badge": "La tua sicurezza digitale inizia dalla consapevolezza.",
        "hero_title_1": "Individua le minacce digitali prima che diventino rischi.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian monitora sequenze di eventi sospette, rileva segnali di frode e attività rischiose e ti avvisa prima che vengano completate azioni sensibili.",
        "user_mode": "Utente",
        "soc_mode": "SOC",
        "placeholder": "Incolla qui un messaggio, un'e-mail, un SMS, un URL o una comunicazione sospetta...",
        "analyze": "Analizza",
        "risk_score": "Punteggio di rischio",
        "risk_level": "Livello di rischio",
        "incident_id": "ID incidente",
        "language": "Lingua",
        "decision_transition": "Transizione decisionale",
        "dangerous_transitions": "Transizioni pericolose",
        "risk_factors": "Fattori di rischio",
        "iocs": "Indicatori di compromissione",
        "timeline": "Sequenza temporale",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Raccomandazioni",
        "incident_history": "Cronologia degli incidenti",
        "none_detected": "Nessun elemento rilevato.",
        "no_intervention": "Nessun intervento richiesto.",
        "stop": "Fermati e verifica prima di continuare.",
        "please_enter": "Inserisci un messaggio.",
        "normal": "Normale",
        "low": "Basso",
        "medium_level": "Medio",
        "high": "Alto",
        "critical": "Critico",
        "external_destination": "Destinazione esterna rilevata",
        "credential_request": "Richiesta di credenziali rilevata",
        "otp_request": "Richiesta di codice monouso rilevata",
        "financial_action": "Azione finanziaria rilevata",
        "urgency": "Urgenza o pressione rilevata",
        "verify_destination": "Verifica la destinazione e il collegamento prima di continuare.",
        "protect_credentials": "Non inserire la password prima di aver verificato il destinatario.",
        "protect_otp": "Non condividere mai un codice di verifica monouso.",
        "verify_financial": "Verifica beneficiario, importo e dettagli della transazione.",
        "avoid_pressure": "Non prendere decisioni sensibili sotto pressione.",
        "review_sequence": "Controlla l'intera sequenza prima di continuare.",
        "unknown_event": "Evento di sicurezza sconosciuto",
        "mitre_phishing": "Phishing",
        "mitre_input": "Acquisizione dell'input",
        "mitre_execution": "Esecuzione da parte dell'utente",
        "analysis_failed": "Impossibile completare l'analisi.",
        "date": "Data",
        "time": "Ora",
        "footer": "Decision Guardian — Guardiano della sicurezza digitale"
    },

    "pt": {
        "name": "Português",
        "dir": "ltr",
        "brand_subtitle": "Guardião da segurança digital",
        "badge": "Sua segurança digital começa com a conscientização.",
        "hero_title_1": "Detecte ameaças digitais antes que se tornem riscos.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "O Decision Guardian monitora sequências suspeitas de eventos, identifica sinais de fraude e atividades arriscadas e alerta você antes da conclusão de ações sensíveis.",
        "user_mode": "Usuário",
        "soc_mode": "SOC",
        "placeholder": "Cole aqui uma mensagem, e-mail, SMS, URL ou comunicação suspeita...",
        "analyze": "Analisar",
        "risk_score": "Pontuação de risco",
        "risk_level": "Nível de risco",
        "incident_id": "ID do incidente",
        "language": "Idioma",
        "decision_transition": "Transição de decisão",
        "dangerous_transitions": "Transições perigosas",
        "risk_factors": "Fatores de risco",
        "iocs": "Indicadores de comprometimento",
        "timeline": "Linha do tempo",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Recomendações",
        "incident_history": "Histórico de incidentes",
        "none_detected": "Nenhum item detectado.",
        "no_intervention": "Nenhuma intervenção necessária.",
        "stop": "Pare e verifique antes de continuar.",
        "please_enter": "Digite uma mensagem.",
        "normal": "Normal",
        "low": "Baixo",
        "medium_level": "Médio",
        "high": "Alto",
        "critical": "Crítico",
        "external_destination": "Destino externo detectado",
        "credential_request": "Solicitação de credenciais detectada",
        "otp_request": "Solicitação de código de uso único detectada",
        "financial_action": "Ação financeira detectada",
        "urgency": "Urgência ou pressão detectada",
        "verify_destination": "Verifique o destino e o link antes de continuar.",
        "protect_credentials": "Não digite sua senha antes de verificar o destinatário.",
        "protect_otp": "Nunca compartilhe um código de verificação de uso único.",
        "verify_financial": "Verifique o beneficiário, o valor e os detalhes da transação.",
        "avoid_pressure": "Não tome uma decisão sensível sob pressão.",
        "review_sequence": "Revise toda a sequência antes de continuar.",
        "unknown_event": "Evento de segurança desconhecido",
        "mitre_phishing": "Phishing",
        "mitre_input": "Captura de entrada",
        "mitre_execution": "Execução pelo usuário",
        "analysis_failed": "Não foi possível concluir a análise.",
        "date": "Data",
        "time": "Hora",
        "footer": "Decision Guardian — Guardião da segurança digital"
    },

    "ru": {
        "name": "Русский",
        "dir": "ltr",
        "brand_subtitle": "Защитник цифровой безопасности",
        "badge": "Цифровая безопасность начинается с осведомлённости.",
        "hero_title_1": "Выявляйте цифровые угрозы до того, как они превратятся в риски.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian отслеживает подозрительные последовательности событий, выявляет признаки мошенничества и рискованных действий и предупреждает вас до завершения важных операций.",
        "user_mode": "Пользователь",
        "soc_mode": "SOC",
        "placeholder": "Вставьте сюда сообщение, электронное письмо, SMS, URL или подозрительное сообщение...",
        "analyze": "Анализировать",
        "risk_score": "Оценка риска",
        "risk_level": "Уровень риска",
        "incident_id": "ID инцидента",
        "language": "Язык",
        "decision_transition": "Переход решения",
        "dangerous_transitions": "Опасные переходы",
        "risk_factors": "Факторы риска",
        "iocs": "Индикаторы компрометации",
        "timeline": "Хронология",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Рекомендации",
        "incident_history": "История инцидентов",
        "none_detected": "Элементы не обнаружены.",
        "no_intervention": "Вмешательство не требуется.",
        "stop": "Остановитесь и проверьте информацию перед продолжением.",
        "please_enter": "Введите сообщение.",
        "normal": "Нормальный",
        "low": "Низкий",
        "medium_level": "Средний",
        "high": "Высокий",
        "critical": "Критический",
        "external_destination": "Обнаружен внешний адрес",
        "credential_request": "Обнаружен запрос учетных данных",
        "otp_request": "Обнаружен запрос одноразового кода",
        "financial_action": "Обнаружено финансовое действие",
        "urgency": "Обнаружены срочность или давление",
        "verify_destination": "Проверьте адрес и ссылку перед продолжением.",
        "protect_credentials": "Не вводите пароль, пока не проверите получателя.",
        "protect_otp": "Никогда не сообщайте одноразовый код подтверждения.",
        "verify_financial": "Проверьте получателя, сумму и детали операции.",
        "avoid_pressure": "Не принимайте чувствительные решения под давлением.",
        "review_sequence": "Проверьте всю последовательность действий.",
        "unknown_event": "Неизвестное событие безопасности",
        "mitre_phishing": "Фишинг",
        "mitre_input": "Перехват ввода",
        "mitre_execution": "Выполнение пользователем",
        "analysis_failed": "Не удалось завершить анализ.",
        "date": "Дата",
        "time": "Время",
        "footer": "Decision Guardian — Защитник цифровой безопасности"
    },

    "ja": {
        "name": "日本語",
        "dir": "ltr",
        "brand_subtitle": "デジタルセキュリティの守護者",
        "badge": "デジタルの安全は、気づくことから始まります。",
        "hero_title_1": "デジタルの脅威がリスクになる前に検知します。",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardianは不審なイベントの連続を監視し、詐欺や危険な活動の兆候を検出して、重要な操作が完了する前に警告します。",
        "user_mode": "ユーザー",
        "soc_mode": "SOC",
        "placeholder": "メッセージ、メール、SMS、URL、または不審な通信をここに貼り付けてください...",
        "analyze": "分析",
        "risk_score": "リスクスコア",
        "risk_level": "リスクレベル",
        "incident_id": "インシデントID",
        "language": "言語",
        "decision_transition": "意思決定の遷移",
        "dangerous_transitions": "危険な遷移",
        "risk_factors": "リスク要因",
        "iocs": "侵害の指標",
        "timeline": "タイムライン",
        "mitre": "MITRE ATT&CK",
        "recommendations": "推奨事項",
        "incident_history": "インシデント履歴",
        "none_detected": "検出された項目はありません。",
        "no_intervention": "介入は必要ありません。",
        "stop": "一度停止し、確認してから続行してください。",
        "please_enter": "メッセージを入力してください。",
        "normal": "正常",
        "low": "低",
        "medium_level": "中",
        "high": "高",
        "critical": "重大",
        "external_destination": "外部宛先を検出",
        "credential_request": "認証情報の要求を検出",
        "otp_request": "ワンタイムコードの要求を検出",
        "financial_action": "金融操作を検出",
        "urgency": "緊急性または圧力を検出",
        "verify_destination": "続行する前に宛先とリンクを確認してください。",
        "protect_credentials": "受信者を確認するまでパスワードを入力しないでください。",
        "protect_otp": "ワンタイム認証コードを他人と共有しないでください。",
        "verify_financial": "続行する前に受取人、金額、取引内容を確認してください。",
        "avoid_pressure": "圧力を受けた状態で重要な判断をしないでください。",
        "review_sequence": "続行する前に操作の流れ全体を確認してください。",
        "unknown_event": "不明なセキュリティイベント",
        "mitre_phishing": "フィッシング",
        "mitre_input": "入力キャプチャ",
        "mitre_execution": "ユーザー実行",
        "analysis_failed": "分析を完了できませんでした。",
        "date": "日付",
        "time": "時刻",
        "footer": "Decision Guardian — デジタルセキュリティの守護者"
    },

    "ko": {
        "name": "한국어",
        "dir": "ltr",
        "brand_subtitle": "디지털 보안 수호자",
        "badge": "디지털 안전은 인식에서 시작됩니다.",
        "hero_title_1": "디지털 위협이 위험으로 이어지기 전에 탐지하세요.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian은 의심스러운 이벤트 흐름을 모니터링하고 사기 징후와 위험한 활동을 탐지하여 민감한 작업이 완료되기 전에 경고합니다.",
        "user_mode": "사용자",
        "soc_mode": "SOC",
        "placeholder": "메시지, 이메일, SMS, URL 또는 의심스러운 통신을 여기에 붙여넣으세요...",
        "analyze": "분석",
        "risk_score": "위험 점수",
        "risk_level": "위험 수준",
        "incident_id": "사고 ID",
        "language": "언어",
        "decision_transition": "의사결정 전환",
        "dangerous_transitions": "위험한 전환",
        "risk_factors": "위험 요소",
        "iocs": "침해 지표",
        "timeline": "타임라인",
        "mitre": "MITRE ATT&CK",
        "recommendations": "권장 사항",
        "incident_history": "사고 기록",
        "none_detected": "탐지된 항목이 없습니다.",
        "no_intervention": "개입이 필요하지 않습니다.",
        "stop": "잠시 멈추고 확인한 후 계속하세요.",
        "please_enter": "메시지를 입력하세요.",
        "normal": "정상",
        "low": "낮음",
        "medium_level": "중간",
        "high": "높음",
        "critical": "심각",
        "external_destination": "외부 목적지 탐지",
        "credential_request": "자격 증명 요청 탐지",
        "otp_request": "일회용 인증 코드 요청 탐지",
        "financial_action": "금융 작업 탐지",
        "urgency": "긴급성 또는 압박 탐지",
        "verify_destination": "계속하기 전에 목적지와 링크를 확인하세요.",
        "protect_credentials": "수신자를 확인하기 전에는 비밀번호를 입력하지 마세요.",
        "protect_otp": "일회용 인증 코드를 누구와도 공유하지 마세요.",
        "verify_financial": "계속하기 전에 수취인, 금액 및 거래 세부 정보를 확인하세요.",
        "avoid_pressure": "압박을 받는 상황에서 민감한 결정을 내리지 마세요.",
        "review_sequence": "계속하기 전에 전체 작업 순서를 검토하세요.",
        "unknown_event": "알 수 없는 보안 이벤트",
        "mitre_phishing": "피싱",
        "mitre_input": "입력 캡처",
        "mitre_execution": "사용자 실행",
        "analysis_failed": "분석을 완료할 수 없습니다.",
        "date": "날짜",
        "time": "시간",
        "footer": "Decision Guardian — 디지털 보안 수호자"
    },

    "tr": {
        "name": "Türkçe",
        "dir": "ltr",
        "brand_subtitle": "Dijital Güvenlik Koruyucusu",
        "badge": "Dijital güvenliğiniz farkındalıkla başlar.",
        "hero_title_1": "Dijital tehditleri riske dönüşmeden önce tespit edin.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian şüpheli olay dizilerini izler, dolandırıcılık belirtilerini ve riskli etkinlikleri tespit eder ve hassas işlemler tamamlanmadan önce sizi uyarır.",
        "user_mode": "Kullanıcı",
        "soc_mode": "SOC",
        "placeholder": "Mesajı, e-postayı, SMS'i, URL'yi veya şüpheli iletişimi buraya yapıştırın...",
        "analyze": "Analiz Et",
        "risk_score": "Risk Puanı",
        "risk_level": "Risk Seviyesi",
        "incident_id": "Olay Kimliği",
        "language": "Dil",
        "decision_transition": "Karar Geçişi",
        "dangerous_transitions": "Tehlikeli Geçişler",
        "risk_factors": "Risk Faktörleri",
        "iocs": "Uzlaşma Göstergeleri",
        "timeline": "Zaman Çizelgesi",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Öneriler",
        "incident_history": "Olay Geçmişi",
        "none_detected": "Öğe tespit edilmedi.",
        "no_intervention": "Müdahale gerekmiyor.",
        "stop": "Durun ve devam etmeden önce doğrulayın.",
        "please_enter": "Lütfen bir mesaj girin.",
        "normal": "Normal",
        "low": "Düşük",
        "medium_level": "Orta",
        "high": "Yüksek",
        "critical": "Kritik",
        "external_destination": "Harici hedef tespit edildi",
        "credential_request": "Kimlik bilgisi isteği tespit edildi",
        "otp_request": "Tek kullanımlık kod isteği tespit edildi",
        "financial_action": "Finansal işlem tespit edildi",
        "urgency": "Aciliyet veya baskı tespit edildi",
        "verify_destination": "Devam etmeden önce hedefi ve bağlantıyı doğrulayın.",
        "protect_credentials": "Alıcıyı doğrulamadan parolanızı girmeyin.",
        "protect_otp": "Tek kullanımlık doğrulama kodunu kimseyle paylaşmayın.",
        "verify_financial": "Devam etmeden önce alıcıyı, tutarı ve işlem ayrıntılarını doğrulayın.",
        "avoid_pressure": "Baskı altında hassas kararlar vermeyin.",
        "review_sequence": "Devam etmeden önce tüm işlem adımlarını inceleyin.",
        "unknown_event": "Bilinmeyen güvenlik olayı",
        "mitre_phishing": "Kimlik Avı",
        "mitre_input": "Girdi Yakalama",
        "mitre_execution": "Kullanıcı Yürütmesi",
        "analysis_failed": "Analiz tamamlanamadı.",
        "date": "Tarih",
        "time": "Saat",
        "footer": "Decision Guardian — Dijital Güvenlik Koruyucusu"
    },

    "id": {
        "name": "Bahasa Indonesia",
        "dir": "ltr",
        "brand_subtitle": "Pelindung Keamanan Digital",
        "badge": "Keamanan digital Anda dimulai dari kesadaran.",
        "hero_title_1": "Kenali ancaman digital sebelum berkembang menjadi risiko.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian memantau rangkaian peristiwa mencurigakan, mendeteksi tanda penipuan dan aktivitas berisiko, serta memperingatkan Anda sebelum tindakan sensitif selesai.",
        "user_mode": "Pengguna",
        "soc_mode": "SOC",
        "placeholder": "Tempel pesan, email, SMS, URL, atau komunikasi mencurigakan di sini...",
        "analyze": "Analisis",
        "risk_score": "Skor Risiko",
        "risk_level": "Tingkat Risiko",
        "incident_id": "ID Insiden",
        "language": "Bahasa",
        "decision_transition": "Transisi Keputusan",
        "dangerous_transitions": "Transisi Berbahaya",
        "risk_factors": "Faktor Risiko",
        "iocs": "Indikator Kompromi",
        "timeline": "Linimasa",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Rekomendasi",
        "incident_history": "Riwayat Insiden",
        "none_detected": "Tidak ada yang terdeteksi.",
        "no_intervention": "Tidak diperlukan intervensi.",
        "stop": "Berhenti dan verifikasi sebelum melanjutkan.",
        "please_enter": "Masukkan pesan.",
        "normal": "Normal",
        "low": "Rendah",
        "medium_level": "Sedang",
        "high": "Tinggi",
        "critical": "Kritis",
        "external_destination": "Tujuan eksternal terdeteksi",
        "credential_request": "Permintaan kredensial terdeteksi",
        "otp_request": "Permintaan kode sekali pakai terdeteksi",
        "financial_action": "Tindakan keuangan terdeteksi",
        "urgency": "Urgensi atau tekanan terdeteksi",
        "verify_destination": "Verifikasi tujuan dan tautan sebelum melanjutkan.",
        "protect_credentials": "Jangan masukkan kata sandi sebelum memverifikasi penerima.",
        "protect_otp": "Jangan pernah membagikan kode verifikasi sekali pakai.",
        "verify_financial": "Verifikasi penerima, jumlah, dan detail transaksi.",
        "avoid_pressure": "Jangan mengambil keputusan sensitif di bawah tekanan.",
        "review_sequence": "Tinjau seluruh rangkaian tindakan sebelum melanjutkan.",
        "unknown_event": "Peristiwa keamanan tidak dikenal",
        "mitre_phishing": "Phishing",
        "mitre_input": "Penangkapan Input",
        "mitre_execution": "Eksekusi Pengguna",
        "analysis_failed": "Analisis tidak dapat diselesaikan.",
        "date": "Tanggal",
        "time": "Waktu",
        "footer": "Decision Guardian — Pelindung Keamanan Digital"
    },

    "pl": {
        "name": "Polski",
        "dir": "ltr",
        "brand_subtitle": "Strażnik bezpieczeństwa cyfrowego",
        "badge": "Twoje bezpieczeństwo cyfrowe zaczyna się od świadomości.",
        "hero_title_1": "Wykrywaj zagrożenia cyfrowe, zanim przerodzą się w ryzyko.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian monitoruje podejrzane sekwencje zdarzeń, wykrywa oznaki oszustw i ryzykownych działań oraz ostrzega przed zakończeniem wrażliwych czynności.",
        "user_mode": "Użytkownik",
        "soc_mode": "SOC",
        "placeholder": "Wklej tutaj wiadomość, e-mail, SMS, adres URL lub podejrzaną komunikację...",
        "analyze": "Analizuj",
        "risk_score": "Ocena ryzyka",
        "risk_level": "Poziom ryzyka",
        "incident_id": "ID incydentu",
        "language": "Język",
        "decision_transition": "Przejście decyzji",
        "dangerous_transitions": "Niebezpieczne przejścia",
        "risk_factors": "Czynniki ryzyka",
        "iocs": "Wskaźniki naruszenia",
        "timeline": "Oś czasu",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Zalecenia",
        "incident_history": "Historia incydentów",
        "none_detected": "Nie wykryto żadnych elementów.",
        "no_intervention": "Interwencja nie jest wymagana.",
        "stop": "Zatrzymaj się i zweryfikuj informacje przed kontynuowaniem.",
        "please_enter": "Wprowadź wiadomość.",
        "normal": "Normalny",
        "low": "Niski",
        "medium_level": "Średni",
        "high": "Wysoki",
        "critical": "Krytyczny",
        "external_destination": "Wykryto zewnętrzny adres",
        "credential_request": "Wykryto żądanie danych uwierzytelniających",
        "otp_request": "Wykryto żądanie kodu jednorazowego",
        "financial_action": "Wykryto działanie finansowe",
        "urgency": "Wykryto pilność lub presję",
        "verify_destination": "Sprawdź miejsce docelowe i link przed kontynuowaniem.",
        "protect_credentials": "Nie wpisuj hasła przed zweryfikowaniem odbiorcy.",
        "protect_otp": "Nigdy nie udostępniaj jednorazowego kodu weryfikacyjnego.",
        "verify_financial": "Sprawdź odbiorcę, kwotę i szczegóły transakcji.",
        "avoid_pressure": "Nie podejmuj wrażliwych decyzji pod presją.",
        "review_sequence": "Przejrzyj całą sekwencję działań przed kontynuowaniem.",
        "unknown_event": "Nieznane zdarzenie bezpieczeństwa",
        "mitre_phishing": "Phishing",
        "mitre_input": "Przechwytywanie danych wejściowych",
        "mitre_execution": "Wykonanie przez użytkownika",
        "analysis_failed": "Nie udało się ukończyć analizy.",
        "date": "Data",
        "time": "Czas",
        "footer": "Decision Guardian — Strażnik bezpieczeństwa cyfrowego"
    },

    "uk": {
        "name": "Українська",
        "dir": "ltr",
        "brand_subtitle": "Захисник цифрової безпеки",
        "badge": "Цифрова безпека починається з обізнаності.",
        "hero_title_1": "Виявляйте цифрові загрози, перш ніж вони перетворяться на ризики.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian відстежує підозрілі послідовності подій, виявляє ознаки шахрайства та ризикованих дій і попереджає вас до завершення чутливих операцій.",
        "user_mode": "Користувач",
        "soc_mode": "SOC",
        "placeholder": "Вставте повідомлення, електронний лист, SMS, URL або підозрілу комунікацію...",
        "analyze": "Аналізувати",
        "risk_score": "Оцінка ризику",
        "risk_level": "Рівень ризику",
        "incident_id": "ID інциденту",
        "language": "Мова",
        "decision_transition": "Перехід рішення",
        "dangerous_transitions": "Небезпечні переходи",
        "risk_factors": "Фактори ризику",
        "iocs": "Індикатори компрометації",
        "timeline": "Часова шкала",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Рекомендації",
        "incident_history": "Історія інцидентів",
        "none_detected": "Елементів не виявлено.",
        "no_intervention": "Втручання не потрібне.",
        "stop": "Зупиніться та перевірте інформацію перед продовженням.",
        "please_enter": "Введіть повідомлення.",
        "normal": "Нормальний",
        "low": "Низький",
        "medium_level": "Середній",
        "high": "Високий",
        "critical": "Критичний",
        "external_destination": "Виявлено зовнішню адресу",
        "credential_request": "Виявлено запит облікових даних",
        "otp_request": "Виявлено запит одноразового коду",
        "financial_action": "Виявлено фінансову дію",
        "urgency": "Виявлено терміновість або тиск",
        "verify_destination": "Перевірте адресу та посилання перед продовженням.",
        "protect_credentials": "Не вводьте пароль, доки не перевірите одержувача.",
        "protect_otp": "Ніколи не повідомляйте одноразовий код підтвердження.",
        "verify_financial": "Перевірте одержувача, суму та деталі транзакції.",
        "avoid_pressure": "Не приймайте чутливих рішень під тиском.",
        "review_sequence": "Перегляньте всю послідовність дій.",
        "unknown_event": "Невідома подія безпеки",
        "mitre_phishing": "Фішинг",
        "mitre_input": "Перехоплення введення",
        "mitre_execution": "Виконання користувачем",
        "analysis_failed": "Не вдалося завершити аналіз.",
        "date": "Дата",
        "time": "Час",
        "footer": "Decision Guardian — Захисник цифрової безпеки"
    },

    "vi": {
        "name": "Tiếng Việt",
        "dir": "ltr",
        "brand_subtitle": "Người bảo vệ an ninh số",
        "badge": "An toàn số bắt đầu từ nhận thức.",
        "hero_title_1": "Phát hiện mối đe dọa kỹ thuật số trước khi chúng trở thành rủi ro.",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian theo dõi chuỗi sự kiện đáng ngờ, phát hiện dấu hiệu lừa đảo và hoạt động rủi ro, đồng thời cảnh báo trước khi hành động nhạy cảm hoàn tất.",
        "user_mode": "Người dùng",
        "soc_mode": "SOC",
        "placeholder": "Dán tin nhắn, email, SMS, URL hoặc thông tin liên lạc đáng ngờ vào đây...",
        "analyze": "Phân tích",
        "risk_score": "Điểm rủi ro",
        "risk_level": "Mức độ rủi ro",
        "incident_id": "ID sự cố",
        "language": "Ngôn ngữ",
        "decision_transition": "Chuyển đổi quyết định",
        "dangerous_transitions": "Chuyển đổi nguy hiểm",
        "risk_factors": "Yếu tố rủi ro",
        "iocs": "Chỉ báo xâm phạm",
        "timeline": "Dòng thời gian",
        "mitre": "MITRE ATT&CK",
        "recommendations": "Khuyến nghị",
        "incident_history": "Lịch sử sự cố",
        "none_detected": "Không phát hiện mục nào.",
        "no_intervention": "Không cần can thiệp.",
        "stop": "Dừng lại và xác minh trước khi tiếp tục.",
        "please_enter": "Vui lòng nhập tin nhắn.",
        "normal": "Bình thường",
        "low": "Thấp",
        "medium_level": "Trung bình",
        "high": "Cao",
        "critical": "Nghiêm trọng",
        "external_destination": "Phát hiện đích bên ngoài",
        "credential_request": "Phát hiện yêu cầu thông tin xác thực",
        "otp_request": "Phát hiện yêu cầu mã dùng một lần",
        "financial_action": "Phát hiện hành động tài chính",
        "urgency": "Phát hiện sự khẩn cấp hoặc áp lực",
        "verify_destination": "Xác minh đích và liên kết trước khi tiếp tục.",
        "protect_credentials": "Không nhập mật khẩu trước khi xác minh người nhận.",
        "protect_otp": "Không bao giờ chia sẻ mã xác minh dùng một lần.",
        "verify_financial": "Xác minh người nhận, số tiền và chi tiết giao dịch.",
        "avoid_pressure": "Không đưa ra quyết định nhạy cảm dưới áp lực.",
        "review_sequence": "Xem lại toàn bộ chuỗi hành động trước khi tiếp tục.",
        "unknown_event": "Sự kiện bảo mật không xác định",
        "mitre_phishing": "Lừa đảo",
        "mitre_input": "Thu thập dữ liệu đầu vào",
        "mitre_execution": "Thực thi bởi người dùng",
        "analysis_failed": "Không thể hoàn tất phân tích.",
        "date": "Ngày",
        "time": "Thời gian",
        "footer": "Decision Guardian — Người bảo vệ an ninh số"
    },

    "th": {
        "name": "ไทย",
        "dir": "ltr",
        "brand_subtitle": "ผู้พิทักษ์ความปลอดภัยดิจิทัล",
        "badge": "ความปลอดภัยดิจิทัลเริ่มต้นจากการรู้เท่าทัน",
        "hero_title_1": "ตรวจจับภัยคุกคามดิจิทัลก่อนที่จะกลายเป็นความเสี่ยง",
        "hero_title_2": "",
        "hero_title_3": "",
        "hero_description": "Decision Guardian เฝ้าติดตามลำดับเหตุการณ์ที่น่าสงสัย ตรวจจับสัญญาณการฉ้อโกงและกิจกรรมเสี่ยง พร้อมแจ้งเตือนก่อนดำเนินการสำคัญเสร็จสิ้น",
        "user_mode": "ผู้ใช้",
        "soc_mode": "SOC",
        "placeholder": "วางข้อความ อีเมล SMS URL หรือการสื่อสารที่น่าสงสัยที่นี่...",
        "analyze": "วิเคราะห์",
        "risk_score": "คะแนนความเสี่ยง",
        "risk_level": "ระดับความเสี่ยง",
        "incident_id": "รหัสเหตุการณ์",
        "language": "ภาษา",
        "decision_transition": "การเปลี่ยนผ่านของการตัดสินใจ",
        "dangerous_transitions": "การเปลี่ยนผ่านที่อันตราย",
        "risk_factors": "ปัจจัยความเสี่ยง",
        "iocs": "ตัวบ่งชี้การบุกรุก",
        "timeline": "ไทม์ไลน์",
        "mitre": "MITRE ATT&CK",
        "recommendations": "คำแนะนำ",
        "incident_history": "ประวัติเหตุการณ์",
        "none_detected": "ไม่พบรายการ",
        "no_intervention": "ไม่จำเป็นต้องดำเนินการแทรกแซง",
        "stop": "หยุดและตรวจสอบก่อนดำเนินการต่อ",
        "please_enter": "กรุณาป้อนข้อความ",
        "normal": "ปกติ",
        "low": "ต่ำ",
        "medium_level": "ปานกลาง",
        "high": "สูง",
        "critical": "วิกฤต",
        "external_destination": "ตรวจพบปลายทางภายนอก",
        "credential_request": "ตรวจพบคำขอข้อมูลรับรอง",
        "otp_request": "ตรวจพบคำขอรหัสแบบใช้ครั้งเดียว",
        "financial_action": "ตรวจพบการดำเนินการทางการเงิน",
        "urgency": "ตรวจพบความเร่งด่วนหรือแรงกดดัน",
        "verify_destination": "ตรวจสอบปลายทางและลิงก์ก่อนดำเนินการต่อ",
        "protect_credentials": "อย่าป้อนรหัสผ่านจนกว่าจะตรวจสอบผู้รับ",
        "protect_otp": "อย่าแชร์รหัสยืนยันแบบใช้ครั้งเดียวกับผู้อื่น",
        "verify_financial": "ตรวจสอบผู้รับ จำนวนเงิน และรายละเอียดธุรกรรมก่อนดำเนินการ",
        "avoid_pressure": "อย่าตัดสินใจเรื่องสำคัญภายใต้แรงกดดัน",
        "review_sequence": "ตรวจสอบลำดับการดำเนินการทั้งหมดก่อนดำเนินการต่อ",
        "unknown_event": "เหตุการณ์ด้านความปลอดภัยที่ไม่รู้จัก",
        "mitre_phishing": "ฟิชชิง",
        "mitre_input": "การดักจับข้อมูลนำเข้า",
        "mitre_execution": "การดำเนินการโดยผู้ใช้",
        "analysis_failed": "ไม่สามารถวิเคราะห์ให้เสร็จสมบูรณ์ได้",
        "date": "วันที่",
        "time": "เวลา",
        "footer": "Decision Guardian — ผู้พิทักษ์ความปลอดภัยดิจิทัล"
    },

    "bn": {
        "name": "বাংলা",
        "dir": "ltr",
        "brand_subtitle": "নিরাপত্তা সিদ্ধান্ত বুদ্ধিমত্তা",
        "badge": "সিদ্ধান্ত বুদ্ধিমত্তা",
        "hero_title_1": "আপনার",
        "hero_title_2": "সিদ্ধান্ত",
        "hero_title_3": " রক্ষা করুন, শুধু ডিভাইস নয়।",
        "hero_description": "সংবেদনশীল কাজ সম্পন্ন হওয়ার আগে ঝুঁকিপূর্ণ সিদ্ধান্ত পরিবর্তন শনাক্ত করুন।",
        "user_mode": "ব্যবহারকারী",
        "soc_mode": "SOC",
        "placeholder": "এখানে বার্তা, ইমেইল, SMS, URL বা সন্দেহজনক যোগাযোগ পেস্ট করুন...",
        "analyze": "বিশ্লেষণ",
        "risk_score": "ঝুঁকি স্কোর",
        "risk_level": "ঝুঁকির মাত্রা",
        "incident_id": "ঘটনার আইডি",
        "language": "ভাষা",
        "decision_transition": "সিদ্ধান্ত পরিবর্তন",
        "dangerous_transitions": "বিপজ্জনক পরিবর্তন",
        "risk_factors": "ঝুঁকির কারণ",
        "iocs": "কম্প্রোমাইজের সূচক",
        "timeline": "সময়রেখা",
        "mitre": "MITRE ATT&CK",
        "recommendations": "সুপারিশ",
        "incident_history": "ঘটনার ইতিহাস",
        "none_detected": "কিছু শনাক্ত হয়নি।",
        "no_intervention": "কোনো হস্তক্ষেপ প্রয়োজন নেই।",
        "stop": "থামুন এবং এগিয়ে যাওয়ার আগে যাচাই করুন।",
        "please_enter": "একটি বার্তা লিখুন।",
        "normal": "স্বাভাবিক",
        "low": "কম",
        "medium_level": "মাঝারি",
        "high": "উচ্চ",
        "critical": "গুরুতর",
        "external_destination": "বাহ্যিক গন্তব্য শনাক্ত হয়েছে",
        "credential_request": "প্রমাণীকরণ তথ্যের অনুরোধ শনাক্ত হয়েছে",
        "otp_request": "একবার ব্যবহারযোগ্য কোডের অনুরোধ শনাক্ত হয়েছে",
        "financial_action": "আর্থিক কার্যক্রম শনাক্ত হয়েছে",
        "urgency": "জরুরি চাপ শনাক্ত হয়েছে",
        "verify_destination": "এগিয়ে যাওয়ার আগে গন্তব্য ও লিংক যাচাই করুন।",
        "protect_credentials": "প্রাপক যাচাই না করা পর্যন্ত পাসওয়ার্ড লিখবেন না।",
        "protect_otp": "কখনো একবার ব্যবহারযোগ্য যাচাইকরণ কোড শেয়ার করবেন না।",
        "verify_financial": "এগিয়ে যাওয়ার আগে প্রাপক, পরিমাণ এবং লেনদেনের বিবরণ যাচাই করুন।",
        "avoid_pressure": "চাপের মধ্যে সংবেদনশীল সিদ্ধান্ত নেবেন না।",
        "review_sequence": "এগিয়ে যাওয়ার আগে সম্পূর্ণ কার্যক্রমের ক্রম পর্যালোচনা করুন।",
        "unknown_event": "অজানা নিরাপত্তা ঘটনা",
        "mitre_phishing": "ফিশিং",
        "mitre_input": "ইনপুট ক্যাপচার",
        "mitre_execution": "ব্যবহারকারীর মাধ্যমে কার্যকরকরণ",
        "analysis_failed": "বিশ্লেষণ সম্পন্ন করা যায়নি।",
        "date": "তারিখ",
        "time": "সময়",
        "footer": "Decision Guardian — নিরাপত্তা সিদ্ধান্ত বুদ্ধিমত্তা"
    }
}


# Merge our clean translations over the old file.
for language_code, values in UI_TRANSLATIONS.items():
    if language_code not in TRANSLATIONS:
        TRANSLATIONS[language_code] = {}

    TRANSLATIONS[language_code].update(values)


# ============================================================
# HELPERS
# ============================================================

def normalize_language(language):
    if not language:
        return "en"

    value = str(language).lower().strip()
    value = value.split("-")[0].split("_")[0]

    if value not in TRANSLATIONS:
        return "en"

    return value


def t(language, key, fallback=""):
    language = normalize_language(language)

    value = TRANSLATIONS.get(language, {}).get(key)

    if value:
        return value

    value = TRANSLATIONS.get("en", {}).get(key)

    if value:
        return value

    return fallback or key


def safe_json(data):
    return json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":")
    )


# ============================================================
# EVENT LOCALIZATION
# ============================================================

EVENT_MAP = {
    "EXTERNAL_DESTINATION": "external_destination",
    "EXTERNAL_DESTINATION_DETECTED": "external_destination",
    "CREDENTIAL_REQUEST": "credential_request",
    "CREDENTIAL_REQUEST_DETECTED": "credential_request",
    "OTP_REQUEST": "otp_request",
    "OTP_REQUEST_DETECTED": "otp_request",
    "FINANCIAL_ACTION": "financial_action",
    "FINANCIAL_ACTION_DETECTED": "financial_action",
    "URGENCY": "urgency",
    "URGENCY_DETECTED": "urgency",
    "AUTHENTICATION": "credential_request",
    "AUTHENTICATION_REQUEST": "credential_request",
}


def detect_event_key(value):
    if value is None:
        return None

    text = str(value).strip()
    upper = text.upper()

    if upper in EVENT_MAP:
        return EVENT_MAP[upper]

    if "EXTERNAL" in upper and (
        "DESTINATION" in upper or
        "LINK" in upper or
        "URL" in upper
    ):
        return "external_destination"

    if "CREDENTIAL" in upper or "PASSWORD" in upper:
        return "credential_request"

    if "OTP" in upper or "ONE-TIME" in upper:
        return "otp_request"

    if (
        "FINANCIAL" in upper or
        "TRANSFER" in upper or
        "BENEFICIARY" in upper
    ):
        return "financial_action"

    if "URGENCY" in upper or "PRESSURE" in upper:
        return "urgency"

    return None


def localize_event(value, language):
    key = detect_event_key(value)

    if key:
        return t(
            language,
            key,
            t(language, "unknown_event", "Unknown security event")
        )

    return str(value) if value else t(
        language,
        "unknown_event",
        "Unknown security event"
    )


# ============================================================
# RISK
# ============================================================

RISK_MAP = {
    "NORMAL": "normal",
    "LOW": "low",
    "MEDIUM": "medium_level",
    "HIGH": "high",
    "CRITICAL": "critical",
}


def normalize_risk(level):
    if not level:
        return "NORMAL"

    value = str(level).upper().strip()

    if value in RISK_MAP:
        return value

    return "NORMAL"


def localize_risk(level, language):
    code = normalize_risk(level)

    return t(
        language,
        RISK_MAP[code],
        code.title()
    )


# ============================================================
# TRANSITION
# ============================================================

def localize_transition(value, language):
    if not value:
        return t(
            language,
            "none_detected",
            "None detected."
        )

    if isinstance(value, list):
        parts = value
    else:
        text_value = str(value)

        for separator in ["->", "=>", "→", "»"]:
            text_value = text_value.replace(separator, "|")

        parts = [
            item.strip()
            for item in text_value.split("|")
            if item.strip()
        ]

    localized = []

    for item in parts:
        event_key = detect_event_key(item)

        if event_key:
            localized.append(
                t(language, event_key, str(item))
            )
        else:
            localized.append(str(item))

    return " → ".join(localized)


# ============================================================
# DANGEROUS TRANSITIONS
# ============================================================

def localize_dangerous(value, language):
    if not value:
        return []

    if not isinstance(value, list):
        value = [value]

    output = []

    for item in value:
        if isinstance(item, dict):
            source = (
                item.get("source")
                or item.get("from")
                or item.get("first")
            )

            target = (
                item.get("target")
                or item.get("to")
                or item.get("second")
            )

            if source and target:
                output.append(
                    localize_event(source, language)
                    + " → "
                    + localize_event(target, language)
                )
        else:
            output.append(
                localize_transition(item, language)
            )

    return output


# ============================================================
# RISK FACTORS
# ============================================================

def localize_risk_factors(value, language):
    if not value:
        return []

    if not isinstance(value, list):
        value = [value]

    output = []

    for item in value:
        if isinstance(item, dict):
            event = (
                item.get("event")
                or item.get("type")
                or item.get("name")
            )

            if event:
                output.append(
                    localize_event(event, language)
                )
            else:
                values = [
                    str(v)
                    for v in item.values()
                    if v is not None
                ]

                if values:
                    output.append(" — ".join(values))

        else:
            localized = localize_event(item, language)

            if localized:
                output.append(localized)

    return output


# ============================================================
# IOCs
# ============================================================

def localize_iocs(value):
    if not value:
        return []

    output = []

    if isinstance(value, dict):
        for values in value.values():
            if isinstance(values, list):
                for item in values:
                    output.append({"value": str(item)})
            else:
                output.append({"value": str(values)})

        return output

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                actual = (
                    item.get("value")
                    or item.get("indicator")
                    or item.get("ioc")
                    or item.get("url")
                    or item.get("domain")
                    or item.get("email")
                    or item.get("ip")
                )

                if actual:
                    output.append({
                        "value": str(actual)
                    })

            else:
                output.append({
                    "value": str(item)
                })

        return output

    return [{"value": str(value)}]


# ============================================================
# TIMELINE
# ============================================================

def localize_timeline(value, language):
    if not value:
        return []

    if not isinstance(value, list):
        value = [value]

    output = []

    for item in value:
        if isinstance(item, dict):
            timestamp = (
                item.get("timestamp")
                or item.get("time")
                or item.get("date")
                or ""
            )

            event = (
                item.get("event")
                or item.get("type")
                or item.get("action")
                or item.get("description")
                or ""
            )

            output.append({
                "time": str(timestamp),
                "event": localize_event(
                    event,
                    language
                )
            })

        else:
            output.append({
                "time": "",
                "event": localize_event(
                    item,
                    language
                )
            })

    return output


# ============================================================
# MITRE
# ============================================================

MITRE_NAMES = {
    "T1566": "mitre_phishing",
    "T1056": "mitre_input",
    "T1204": "mitre_execution",
}


def localize_mitre(value, language):
    if not value:
        return []

    if not isinstance(value, list):
        value = [value]

    output = []

    for item in value:
        technique_id = None

        if isinstance(item, dict):
            technique_id = (
                item.get("id")
                or item.get("technique_id")
                or item.get("mitre_id")
                or item.get("attack_id")
            )

        else:
            text_value = str(item)

            for possible_id in MITRE_NAMES:
                if possible_id in text_value:
                    technique_id = possible_id
                    break

            if not technique_id:
                output.append({
                    "id": text_value
                })
                continue

        if technique_id:
            technique_id = str(
                technique_id
            ).upper()

        if technique_id in MITRE_NAMES:
            output.append({
                "id": technique_id,
                "name": t(
                    language,
                    MITRE_NAMES[technique_id],
                    technique_id
                )
            })
        else:
            output.append({
                "id": str(
                    technique_id or "MITRE"
                )
            })

    return output


# ============================================================
# RECOMMENDATIONS
# ============================================================

def build_recommendations(raw_result, language):
    events = raw_result.get("events", [])

    event_text = " ".join(
        str(event).upper()
        for event in events
    )

    recommendations = []

    if (
        "EXTERNAL" in event_text
        or "LINK" in event_text
        or "URL" in event_text
    ):
        recommendations.append(
            t(
                language,
                "verify_destination",
                "Verify the destination before continuing."
            )
        )

    if (
        "CREDENTIAL" in event_text
        or "PASSWORD" in event_text
        or "AUTHENTICATION" in event_text
    ):
        recommendations.append(
            t(
                language,
                "protect_credentials",
                "Verify the recipient before entering credentials."
            )
        )

    if "OTP" in event_text:
        recommendations.append(
            t(
                language,
                "protect_otp",
                "Never share a one-time verification code."
            )
        )

    if (
        "FINANCIAL" in event_text
        or "TRANSFER" in event_text
        or "BENEFICIARY" in event_text
    ):
        recommendations.append(
            t(
                language,
                "verify_financial",
                "Verify transaction details before proceeding."
            )
        )

    if (
        "URGENCY" in event_text
        or "PRESSURE" in event_text
    ):
        recommendations.append(
            t(
                language,
                "avoid_pressure",
                "Do not make a sensitive decision under pressure."
            )
        )

    if not recommendations:
        recommendations.append(
            t(
                language,
                "review_sequence",
                "Review the sequence before proceeding."
            )
        )

    return recommendations


# ============================================================
# LOCALIZE RESULT
# ============================================================

def localize_result(raw_result, language):
    result = copy.deepcopy(raw_result)

    language = normalize_language(language)

    original_level = (
        result.get("risk_level")
        or result.get("level")
        or "NORMAL"
    )

    risk_code = normalize_risk(original_level)

    result["risk_level_code"] = risk_code

    result["risk_level"] = localize_risk(
        risk_code,
        language
    )

    detected_language = (
        result.get("detected_language")
        or result.get("language")
        or ""
    )

    if detected_language:
        detected_code = (
            str(detected_language)
            .split("-")[0]
            .split("_")[0]
            .lower()
        )

        detected_name = (
            TRANSLATIONS.get(
                language,
                {}
            ).get(
                "name"
            )
        )

        if detected_code in TRANSLATIONS:
            result["detected_language"] = (
                TRANSLATIONS[detected_code].get(
                    "name",
                    detected_code.upper()
                )
            )
        elif detected_name:
            result["detected_language"] = detected_name
        else:
            result["detected_language"] = detected_code.upper()

    transition = (
        result.get("decision_transition")
        or result.get("transition")
    )

    result["decision_transition"] = localize_transition(
        transition,
        language
    )

    result["dangerous_transitions"] = localize_dangerous(
        result.get("dangerous_transitions"),
        language
    )

    result["risk_factors"] = localize_risk_factors(
        result.get("risk_factors"),
        language
    )

    result["iocs"] = localize_iocs(
        result.get("iocs")
    )

    result["timeline"] = localize_timeline(
        result.get("timeline"),
        language
    )

    result["mitre"] = localize_mitre(
        result.get("mitre"),
        language
    )

    result["recommendations"] = build_recommendations(
        raw_result,
        language
    )

    intervention_required = bool(
        result.get("intervention_required")
        or result.get("needs_intervention")
    )

    result["intervention_required"] = intervention_required

    if intervention_required:
        result["intervention"] = t(
            language,
            "stop",
            "Stop and verify before continuing."
        )
    else:
        result["intervention"] = t(
            language,
            "no_intervention",
            "No intervention required."
        )

    return result


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup():
    initialize_database()


# ============================================================
# HTML
# ============================================================

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Decision Guardian</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Inter, Arial, Helvetica, sans-serif;
    background:
        radial-gradient(
            circle at top,
            #18233d 0%,
            #090d18 45%,
            #05070d 100%
        );
    color: #f4f7ff;
    min-height: 100vh;
}

button,
textarea,
select {
    font: inherit;
}

button {
    cursor: pointer;
}

.container {
    width: min(1180px, calc(100% - 32px));
    margin: auto;
}

header {
    border-bottom: 1px solid rgba(255,255,255,.08);
    background: rgba(5,7,13,.78);
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 20;
}

.nav {
    min-height: 74px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
}

.brand {
    display: flex;
    flex-direction: column;
}

.brand-name {
    font-size: 20px;
    font-weight: 800;
}

.brand-subtitle {
    color: #9ca8c7;
    font-size: 12px;
    margin-top: 3px;
}

.nav-actions {
    display: flex;
    gap: 8px;
    align-items: center;
}

select,
.mode-button {
    background: #11182a;
    color: #e9edff;
    border: 1px solid #2a3552;
    border-radius: 9px;
    padding: 9px 12px;
}

.mode-button.active {
    background: #253557;
    border-color: #6174a6;
}

main {
    padding: 60px 0 80px;
}

.hero {
    text-align: center;
    max-width: 850px;
    margin: 0 auto 42px;
}

.badge {
    display: inline-flex;
    padding: 7px 13px;
    border-radius: 999px;
    background: rgba(89,119,255,.12);
    border: 1px solid rgba(89,119,255,.25);
    color: #b8c5ff;
    font-size: 13px;
    margin-bottom: 20px;
}

h1 {
    font-size: clamp(42px, 7vw, 78px);
    line-height: .98;
    letter-spacing: -3px;
    margin: 0;
}

.accent {
    color: #7e9cff;
}

.hero p {
    max-width: 680px;
    margin: 24px auto 0;
    color: #aeb8d0;
    font-size: 17px;
    line-height: 1.7;
}

.analyzer {
    max-width: 900px;
    margin: auto;
    background: rgba(13,19,34,.88);
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 25px 80px rgba(0,0,0,.25);
}

textarea {
    width: 100%;
    min-height: 180px;
    resize: vertical;
    border-radius: 13px;
    border: 1px solid #2a3552;
    background: #090e1b;
    color: #f4f7ff;
    padding: 17px;
    outline: none;
}

textarea:focus {
    border-color: #647cff;
}

.analyze-row {
    margin-top: 13px;
    display: flex;
    justify-content: flex-end;
}

.analyze-btn {
    border: 0;
    border-radius: 10px;
    padding: 12px 22px;
    background: #617cff;
    color: white;
    font-weight: 800;
}

.analyze-btn:disabled {
    opacity: .5;
    cursor: wait;
}

.results {
    display: none;
    margin-top: 32px;
}

.results.show {
    display: block;
}

.result-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}

.card {
    background: rgba(13,19,34,.88);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px;
    padding: 17px;
}

.card-label {
    color: #8f9bb8;
    font-size: 12px;
    margin-bottom: 8px;
}

.card-value {
    font-size: 17px;
    font-weight: 700;
    word-break: break-word;
}

.level-normal {
    color: #7bdc9c;
}

.level-low {
    color: #8fc8ff;
}

.level-medium {
    color: #f3ca70;
}

.level-high {
    color: #ff9d66;
}

.level-critical {
    color: #ff6878;
}

.section {
    margin-top: 14px;
}

.section-title {
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 10px;
}

.list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.list-item {
    background: #0a1020;
    border: 1px solid #202a43;
    border-radius: 9px;
    padding: 11px 13px;
    color: #d8def0;
    line-height: 1.5;
}

.intervention {
    margin-top: 15px;
    padding: 17px;
    border-radius: 12px;
    background: rgba(255,76,95,.1);
    border: 1px solid rgba(255,76,95,.35);
    color: #ff9ca7;
    font-weight: 800;
}

.safe {
    margin-top: 15px;
    padding: 17px;
    border-radius: 12px;
    background: rgba(72,197,121,.08);
    border: 1px solid rgba(72,197,121,.25);
    color: #8ce0ab;
    font-weight: 700;
}

.timeline-item {
    display: grid;
    grid-template-columns: 180px 1fr;
    gap: 12px;
}

.timeline-time {
    color: #7e8aa7;
    font-size: 13px;
}

.soc {
    display: none;
    margin-top: 40px;
}

.soc.show {
    display: block;
}

.history-table {
    width: 100%;
    border-collapse: collapse;
}

.history-table th,
.history-table td {
    padding: 12px;
    text-align: start;
    border-bottom: 1px solid #202a43;
}

.history-table th {
    color: #8793af;
    font-size: 12px;
}

@media (max-width: 800px) {
    .result-grid {
        grid-template-columns: 1fr;
    }

    .nav {
        flex-direction: column;
        align-items: flex-start;
        padding: 15px 0;
    }

    .timeline-item {
        grid-template-columns: 1fr;
        gap: 3px;
    }

    h1 {
        letter-spacing: -2px;
    }
}

footer {
    border-top: 1px solid rgba(255,255,255,.08);
    padding: 24px 0;
    color: #77839f;
    text-align: center;
    font-size: 12px;
}
</style>
</head>

<body>

<header>
<div class="container nav">

<div class="brand">
<div class="brand-name">Decision Guardian</div>

<div
    class="brand-subtitle"
    data-i18n="brand_subtitle"
>
حارس الأمن الرقمي
</div>
</div>

<div class="nav-actions">

<button
    id="userMode"
    class="mode-button active"
    onclick="setMode('user')"
    data-i18n="user_mode"
>
User
</button>

<button
    id="socMode"
    class="mode-button"
    onclick="setMode('soc')"
    data-i18n="soc_mode"
>
SOC
</button>

<select id="languageSelect"></select>

</div>
</div>
</header>


<main>
<div class="container">

<section class="hero">

<div
    class="badge"
    data-i18n="badge"
>
أمانك الرقمي يبدأ بالوعي.
</div>

<h1 data-i18n="hero_title_1">
اكتشف التهديدات الرقمية قبل أن تتحول إلى مخاطر.
</h1>

<p data-i18n="hero_description">
Detect risky decision transitions before a sensitive action is completed.
</p>

</section>


<section class="analyzer">

<textarea
    id="messageInput"
    data-i18n-placeholder="placeholder"
    placeholder="Paste a message, email, SMS, URL, or suspicious communication here..."
></textarea>

<div class="analyze-row">

<button
    id="analyzeButton"
    class="analyze-btn"
    onclick="analyzeMessage(true)"
    data-i18n="analyze"
>
Analyze
</button>

</div>
</section>


<section
    id="results"
    class="results"
>

<div class="result-grid">

<div class="card">
<div
    class="card-label"
    data-i18n="risk_score"
>
Risk Score
</div>

<div
    id="scoreValue"
    class="card-value"
>
—
</div>
</div>


<div class="card">
<div
    class="card-label"
    data-i18n="risk_level"
>
Risk Level
</div>

<div
    id="levelValue"
    class="card-value"
>
—
</div>
</div>


<div class="card">
<div
    class="card-label"
    data-i18n="incident_id"
>
Incident ID
</div>

<div
    id="incidentValue"
    class="card-value"
>
—
</div>
</div>


<div class="card">
<div
    class="card-label"
    data-i18n="language"
>
Language
</div>

<div
    id="languageValue"
    class="card-value"
>
—
</div>
</div>


<div
    class="card"
    style="grid-column: span 2;"
>

<div
    class="card-label"
    data-i18n="decision_transition"
>
Decision Transition
</div>

<div
    id="transitionValue"
    class="card-value"
>
—
</div>

</div>

</div>


<div id="interventionBox"></div>


<div class="section">
<div
    class="section-title"
    data-i18n="dangerous_transitions"
>
Dangerous Transitions
</div>

<div
    id="dangerousTransitions"
    class="list"
></div>
</div>


<div class="section">
<div
    class="section-title"
    data-i18n="risk_factors"
>
Risk Factors
</div>

<div
    id="riskFactors"
    class="list"
></div>
</div>


<div class="section">
<div
    class="section-title"
    data-i18n="iocs"
>
Indicators of Compromise
</div>

<div
    id="iocs"
    class="list"
></div>
</div>


<div class="section">
<div
    class="section-title"
    data-i18n="timeline"
>
Timeline
</div>

<div
    id="timeline"
    class="list"
></div>
</div>


<div class="section">
<div
    class="section-title"
    data-i18n="mitre"
>
MITRE ATT&CK
</div>

<div
    id="mitre"
    class="list"
></div>
</div>


<div class="section">
<div
    class="section-title"
    data-i18n="recommendations"
>
Recommendations
</div>

<div
    id="recommendations"
    class="list"
></div>
</div>

</section>


<section
    id="socSection"
    class="soc"
>

<div class="section-title">
<span data-i18n="incident_history">
Incident History
</span>
</div>

<div class="card">

<table class="history-table">

<thead>
<tr>
<th data-i18n="incident_id">Incident ID</th>
<th data-i18n="risk_level">Risk Level</th>
<th data-i18n="risk_score">Risk Score</th>
<th data-i18n="date">Date</th>
</tr>
</thead>

<tbody id="historyBody"></tbody>

</table>

</div>
</section>

</div>
</main>


<footer>
<div class="container">
<span data-i18n="footer">
Decision Guardian — Security Decision Intelligence
</span>
</div>
</footer>


<script>

const TRANSLATIONS = __TRANSLATIONS__;

let currentLanguage =
    localStorage.getItem("dg_language") ||
    navigator.language?.split("-")[0] ||
    "en";

if (!TRANSLATIONS[currentLanguage]) {
    currentLanguage = "en";
}

let currentMode =
    localStorage.getItem("dg_mode") ||
    "user";

let lastMessage = "";
let lastResult = null;


function t(key, fallback = "") {
    const language =
        TRANSLATIONS[currentLanguage] ||
        TRANSLATIONS["en"];

    return (
        language[key] ??
        TRANSLATIONS["en"]?.[key] ??
        fallback ??
        key
    );
}


function escapeHtml(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function applyLanguage() {
    const language =
        TRANSLATIONS[currentLanguage] ||
        TRANSLATIONS["en"];

    document.documentElement.lang =
        currentLanguage;

    document.documentElement.dir =
        language.dir || "ltr";

    document
        .querySelectorAll("[data-i18n]")
        .forEach(element => {
            const key =
                element.getAttribute("data-i18n");

            if (
                language[key] !== undefined
            ) {
                element.textContent =
                    language[key];
            }
        });

    document
        .querySelectorAll(
            "[data-i18n-placeholder]"
        )
        .forEach(element => {
            const key =
                element.getAttribute(
                    "data-i18n-placeholder"
                );

            if (
                language[key] !== undefined
            ) {
                element.placeholder =
                    language[key];
            }
        });

    updateLanguageSelect();

    if (
        lastMessage &&
        lastResult
    ) {
        analyzeMessage(false);
    }
}


function populateLanguageSelect() {
    const select =
        document.getElementById(
            "languageSelect"
        );

    select.innerHTML = "";

    Object.entries(TRANSLATIONS)
        .forEach(([code, data]) => {
            const option =
                document.createElement(
                    "option"
                );

            option.value = code;

            option.textContent =
                data.name ||
                code.toUpperCase();

            select.appendChild(option);
        });

    select.value =
        currentLanguage;

    select.addEventListener(
        "change",
        () => {
            currentLanguage =
                select.value;

            localStorage.setItem(
                "dg_language",
                currentLanguage
            );

            applyLanguage();
        }
    );
}


function updateLanguageSelect() {
    const select =
        document.getElementById(
            "languageSelect"
        );

    if (select) {
        select.value =
            currentLanguage;
    }
}


function setMode(mode) {
    currentMode = mode;

    localStorage.setItem(
        "dg_mode",
        mode
    );

    document
        .getElementById("userMode")
        .classList.toggle(
            "active",
            mode === "user"
        );

    document
        .getElementById("socMode")
        .classList.toggle(
            "active",
            mode === "soc"
        );

    document
        .getElementById("socSection")
        .classList.toggle(
            "show",
            mode === "soc"
        );

    if (mode === "soc") {
        loadHistory();
    }
}


function normalizeLevel(level) {
    if (!level) {
        return "NORMAL";
    }

    const value =
        String(level).toUpperCase();

    if (
        value === "CRITICAL" ||
        value.includes("CRITICAL")
    ) {
        return "CRITICAL";
    }

    if (
        value === "HIGH" ||
        value.includes("HIGH")
    ) {
        return "HIGH";
    }

    if (
        value === "MEDIUM" ||
        value.includes("MEDIUM")
    ) {
        return "MEDIUM";
    }

    if (
        value === "LOW" ||
        value.includes("LOW")
    ) {
        return "LOW";
    }

    return "NORMAL";
}


function riskClass(level) {
    return (
        "level-" +
        normalizeLevel(level)
            .toLowerCase()
    );
}


function localizedLevel(level) {
    const normalized =
        normalizeLevel(level);

    const map = {
        NORMAL: "normal",
        LOW: "low",
        MEDIUM: "medium_level",
        HIGH: "high",
        CRITICAL: "critical"
    };

    return t(
        map[normalized],
        normalized
    );
}


function renderList(
    elementId,
    items
) {
    const container =
        document.getElementById(
            elementId
        );

    container.innerHTML = "";

    if (
        !items ||
        !items.length
    ) {
        const empty =
            document.createElement(
                "div"
            );

        empty.className =
            "list-item";

        empty.textContent =
            t(
                "none_detected",
                "None detected."
            );

        container.appendChild(
            empty
        );

        return;
    }

    items.forEach(item => {
        const element =
            document.createElement(
                "div"
            );

        element.className =
            "list-item";

        if (
            elementId === "iocs" &&
            typeof item === "object" &&
            item !== null
        ) {
            element.textContent =
                item.value || "";
        }

        else if (
            elementId === "mitre" &&
            typeof item === "object" &&
            item !== null
        ) {
            const id =
                item.id || "";

            const name =
                item.name || "";

            element.textContent =
                name
                    ? id + " — " + name
                    : id;
        }

        else if (
            typeof item === "object" &&
            item !== null
        ) {
            element.textContent =
                Object.values(item)
                    .filter(
                        value =>
                            value !== null &&
                            value !== undefined &&
                            String(value).trim() !== ""
                    )
                    .join(" — ");
        }

        else {
            element.textContent =
                String(item);
        }

        container.appendChild(
            element
        );
    });
}


function renderTimeline(items) {
    const container =
        document.getElementById(
            "timeline"
        );

    container.innerHTML = "";

    if (
        !items ||
        !items.length
    ) {
        const empty =
            document.createElement(
                "div"
            );

        empty.className =
            "list-item";

        empty.textContent =
            t(
                "none_detected",
                "None detected."
            );

        container.appendChild(
            empty
        );

        return;
    }

    items.forEach(item => {
        const row =
            document.createElement(
                "div"
            );

        row.className =
            "list-item timeline-item";

        const time =
            document.createElement(
                "div"
            );

        time.className =
            "timeline-time";

        time.textContent =
            item?.time || "—";

        const event =
            document.createElement(
                "div"
            );

        event.textContent =
            item?.event ||
            String(item);

        row.appendChild(time);
        row.appendChild(event);

        container.appendChild(row);
    });
}


function renderIntervention(data) {
    const box =
        document.getElementById(
            "interventionBox"
        );

    if (
        data.intervention_required
    ) {
        box.className =
            "intervention";
    }

    else {
        box.className =
            "safe";
    }

    box.textContent =
        data.intervention ||
        (
            data.intervention_required
                ? t(
                    "stop",
                    "Stop and verify before continuing."
                )
                : t(
                    "no_intervention",
                    "No intervention required."
                )
        );
}


function renderResult(data) {
    lastResult = data;

    const score =
        data.risk_score ??
        data.score ??
        "—";

    const level =
        data.risk_level_code ||
        data.risk_level ||
        "NORMAL";

    document.getElementById(
        "scoreValue"
    ).textContent =
        score;

    const levelElement =
        document.getElementById(
            "levelValue"
        );

    levelElement.textContent =
        localizedLevel(level);

    levelElement.className =
        "card-value " +
        riskClass(level);

    document.getElementById(
        "incidentValue"
    ).textContent =
        data.incident_id ||
        data.id ||
        "—";

    document.getElementById(
        "languageValue"
    ).textContent =
        data.detected_language ||
        "—";

    document.getElementById(
        "transitionValue"
    ).textContent =
        data.decision_transition ||
        t(
            "none_detected",
            "None detected."
        );

    renderIntervention(data);

    renderList(
        "dangerousTransitions",
        data.dangerous_transitions
    );

    renderList(
        "riskFactors",
        data.risk_factors
    );

    renderList(
        "iocs",
        data.iocs
    );

    renderTimeline(
        data.timeline
    );

    renderList(
        "mitre",
        data.mitre
    );

    renderList(
        "recommendations",
        data.recommendations
    );

    document
        .getElementById("results")
        .classList.add("show");
}


async function analyzeMessage(
    persist = true
) {
    const input =
        document.getElementById(
            "messageInput"
        );

    const button =
        document.getElementById(
            "analyzeButton"
        );

    const message =
        input.value.trim();

    if (!message) {
        alert(
            t(
                "please_enter",
                "Please enter a message."
            )
        );

        return;
    }

    lastMessage =
        message;

    button.disabled =
        true;

    button.textContent =
        "...";

    try {
        const form =
            new FormData();

        form.append(
            "message",
            message
        );

        form.append(
            "language",
            currentLanguage
        );

        form.append(
            "persist",
            persist ? "1" : "0"
        );

        const response =
            await fetch(
                "/analyze",
                {
                    method: "POST",
                    body: form
                }
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.error ||
                t(
                    "analysis_failed",
                    "Analysis failed."
                )
            );
        }

        renderResult(data);

        if (
            currentMode === "soc"
        ) {
            loadHistory();
        }

    } catch (error) {
        alert(
            error.message ||
            t(
                "analysis_failed",
                "Analysis failed."
            )
        );

    } finally {
        button.disabled =
            false;

        button.textContent =
            t(
                "analyze",
                "Analyze"
            );
    }
}


async function loadHistory() {
    try {
        const response =
            await fetch(
                "/api/incidents"
            );

        const data =
            await response.json();

        const body =
            document.getElementById(
                "historyBody"
            );

        body.innerHTML = "";

        const incidents =
            Array.isArray(data)
                ? data
                : data.incidents || [];

        incidents.forEach(
            incident => {
                const row =
                    document.createElement(
                        "tr"
                    );

                const id =
                    incident.incident_id ||
                    incident.id ||
                    "—";

                const level =
                    incident.risk_level ||
                    incident.level ||
                    "NORMAL";

                const score =
                    incident.risk_score ??
                    incident.score ??
                    "—";

                const date =
                    incident.created_at ||
                    incident.timestamp ||
                    "—";

                const idCell =
                    document.createElement(
                        "td"
                    );

                idCell.textContent =
                    id;

                const levelCell =
                    document.createElement(
                        "td"
                    );

                levelCell.className =
                    riskClass(level);

                levelCell.textContent =
                    localizedLevel(level);

                const scoreCell =
                    document.createElement(
                        "td"
                    );

                scoreCell.textContent =
                    score;

                const dateCell =
                    document.createElement(
                        "td"
                    );

                dateCell.textContent =
                    date;

                row.appendChild(idCell);
                row.appendChild(levelCell);
                row.appendChild(scoreCell);
                row.appendChild(dateCell);

                body.appendChild(row);
            }
        );

    } catch (error) {
        console.error(
            "History error:",
            error
        );
    }
}


// ============================================================
// INIT
// ============================================================

populateLanguageSelect();

setMode(currentMode);

applyLanguage();

</script>

</body>
</html>
"""


# ============================================================
# HOME
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    translations_json = safe_json(
        TRANSLATIONS
    )

    page = HTML_PAGE.replace(
        "__TRANSLATIONS__",
        translations_json
    )

    return HTMLResponse(
        content=page
    )


# ============================================================
# ANALYZE
# ============================================================

@app.post("/analyze")
async def analyze_endpoint(
    message: str = Form(...),
    language: str = Form("en"),
    persist: str = Form("1")
):
    language = normalize_language(
        language
    )

    message = message.strip()

    if not message:
        return JSONResponse(
            status_code=400,
            content={
                "error": t(
                    language,
                    "please_enter",
                    "Please enter a message."
                )
            }
        )

    try:
        raw_result = analyze(
            message
        )

        if persist == "1":
            save_incident(
                raw_result
            )

        localized_result = localize_result(
            raw_result,
            language
        )

        return JSONResponse(
            content=localized_result
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "error": t(
                    language,
                    "analysis_failed",
                    "Analysis failed."
                )
            }
        )


# ============================================================
# INCIDENTS
# ============================================================

@app.get("/api/incidents")
async def incidents_endpoint():
    try:
        incidents = get_incidents()

        return JSONResponse(
            content=incidents
        )

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc)
            }
        )


# ============================================================
# STATISTICS
# ============================================================

@app.get("/api/statistics")
async def statistics_endpoint():
    try:
        statistics = get_statistics()

        return JSONResponse(
            content=statistics
        )

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc)
            }
        )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": "Decision Guardian"
    }