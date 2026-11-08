"""Advisory actions only. Historical classification never authorizes closure."""
import re
RULES_VERSION='eligibility-rules-2.0.0'

def parse_triage(value):
    token=re.sub(r'[^A-Z]','',(value or '').upper())
    if token.startswith(('NONACTIONABLE','AUTOCLOSE')):return 'NON_ACTIONABLE'
    if token.startswith('ACTIONABLE'):return 'ACTIONABLE'
    return 'UNKNOWN'

def evaluate(case_id,clock,gaps,study,triage_outcome=None,regulator_reportable=None):
    status=clock['status'];triage=parse_triage(triage_outcome)
    notification='NONE'
    if status in {'NOTIFIED_LATE','OVERDUE_NOT_NOTIFIED'}:notification='ESCALATE_REGULATORY_NOTIFICATION'
    elif status in {'NOTIFICATION_STATUS_UNKNOWN','POLICY_UNKNOWN','APPLICABILITY_UNKNOWN','INPUT_CONFLICT'} and regulator_reportable is not False:notification='ESCALATE_FOR_NOTIFICATION_REVIEW'
    action=notification if notification!='NONE' else 'MANUAL_REVIEW'
    rationale='Historical triage is unverified; no automatic closure or product disposition is authorized.'
    if notification!='NONE':rationale='Notification assessment requires review independently of product evidence and source triage.'
    elif gaps:rationale='Eligibility gaps or conflicts require manual evidence resolution.'
    elif study and study.permitted_excursion_text:action='REVIEW_EXCURSION_AGAINST_PERMITTED_LIMIT';rationale='Eligible evidence may be reviewed; no product release arithmetic or signing is performed.'
    return {'case_id':case_id,'proposed_disposition':action,'action_type':'ADVISORY_REVIEW_ACTION','notification_action':notification,'triage_classification':triage,'auto_close_authorized':False,'rationale':rationale,'rules_version':RULES_VERSION,'confidence':None}
