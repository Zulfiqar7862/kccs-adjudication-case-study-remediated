"""One-hop observations, never unchecked equivalence closure or calibrated confidence."""
from dataclasses import asdict

def norm(value):return (value or '').strip().casefold()

class IdentityResolver:
    def __init__(self,aliases):self.aliases=list(aliases)
    def observations(self,value,entity_type):
        return [a for a in self.aliases if (a.entity_type or 'any').lower() in {entity_type,'any'} and norm(value) in {norm(a.alias_value),norm(a.canonical_value)}]
    @staticmethod
    def provenance(observations):return [asdict(a) for a in observations]
    def resolve(self,value,entity_type,known):
        known_map={norm(k):k for k in known};obs=self.observations(value,entity_type)
        result={'source':value,'canonical':None,'method':'missing' if not value else 'unresolved','confidence':None,'candidates':[],'provenance':self.provenance(obs)}
        if not value:return result
        targets={norm(a.canonical_value) if norm(value)==norm(a.alias_value) else norm(a.alias_value) for a in obs if a.same}
        negatives={norm(a.canonical_value) if norm(value)==norm(a.alias_value) else norm(a.alias_value) for a in obs if not a.same}
        if len(targets)>1 or targets.intersection(negatives):result['method']='conflict';return result
        if norm(value) in known_map:result.update(canonical=known_map[norm(value)],method='exact_source_match');return result
        candidates=[known_map[t] for t in targets if t in known_map and t not in negatives]
        result['candidates']=candidates
        warning=any(a.comment and any(w in a.comment.casefold() for w in ('presentation','strength','disputed')) for a in obs)
        if len(candidates)==1 and not warning:result.update(canonical=candidates[0],method='observed_alias_unqualified')
        elif candidates:result['method']='candidate_requires_human_confirmation'
        return result
