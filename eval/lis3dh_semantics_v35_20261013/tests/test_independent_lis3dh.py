"""Independent source-clause tests. Candidate read consumption is not a silicon fact."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('independent_lis3dh_v35', ROOT/'lis3dh.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
Semantics, OutsideContract = runtime.Semantics, runtime.OutsideContract
sys.path.insert(0,str(ROOT))


def reject_atomic(s, operation):
    before = copy.deepcopy(vars(s))
    with pytest.raises(OutsideContract): operation()
    assert vars(s) == before


@pytest.mark.parametrize('mask',[2,4,8,16,32,64,128,0xFE])
def test_seven_documented_status_reset_rows(mask):
    s=Semantics()
    assert s.read_masked('STATUS_REG',mask)==0
    assert s.known['STATUS_REG']==0xFE


@pytest.mark.parametrize('mask',[1,3,255])
def test_missing_xda_reset_never_fabricated(mask):
    s=Semantics()
    reject_atomic(s,lambda:s.read_masked('STATUS_REG',mask))
    reject_atomic(s,lambda:s.read('STATUS_REG'))


@pytest.mark.parametrize('reg',['OUT_X_L','OUT_X_H','OUT_Y_L','OUT_Y_H','OUT_Z_L','OUT_Z_H'])
def test_cold_dynamic_outputs_unknown(reg):
    s=Semantics()
    reject_atomic(s,lambda:s.read(reg))
    reject_atomic(s,lambda:s.read_masked(reg,255))


@pytest.mark.parametrize('code',[0,1,2])
@pytest.mark.parametrize('neighbors',[0,1,8,0x10,0x20,0x48,0x80,0xF9])
def test_st_rw_legal_encoding_and_all_neighbor_bits_preserved(code,neighbors):
    s=Semantics()
    payload=(neighbors&0xF9)|(code<<1)
    s.write('CTRL_REG4',payload)
    assert s.read('CTRL_REG4')==payload
    assert s.field('CTRL_REG4','ST')==code
    # Legal rewrite must not force ST off or destroy adjacent controls.
    second=(payload&0xF9)|(((code+1)%3)<<1)
    s.write('CTRL_REG4',second)
    assert s.read('CTRL_REG4')==second


@pytest.mark.parametrize('neighbors',[0,1,8,0x10,0x20,0x48,0x80,0xF9])
def test_st_na_code_rejects_without_state_or_trace_mutation(neighbors):
    s=Semantics()
    s.write('CTRL_REG4',2)
    reject_atomic(s,lambda:s.write('CTRL_REG4',(neighbors&0xF9)|6))


@pytest.mark.parametrize('value',[-1,256,True,1.0,'1',None])
def test_malformed_write_rejects_atomically(value):
    s=Semantics()
    reject_atomic(s,lambda:s.write('CTRL_REG4',value))


@pytest.mark.parametrize('mask',[0,-1,256,True,1.0,'1',None])
def test_malformed_observation_mask_rejects_atomically(mask):
    s=Semantics()
    reject_atomic(s,lambda:s.read_masked('STATUS_REG',mask))


def active(profile='common_source',ctrl1=0x17,ctrl4=0):
    s=Semantics(profile=profile)
    s.write('CTRL_REG4',ctrl4)
    s.write('CTRL_REG1',ctrl1)
    return s


def sample(s,xyz=(0x1240,0xABC0,0xFFC0),overwritten=False):
    if s.profile=='common_source':
        s.event('qualified_sample_completed',x_word=xyz[0],y_word=xyz[1],z_word=xyz[2],overwritten=overwritten)
    else:
        s.event('sample_completed',x_word=xyz[0],y_word=xyz[1],z_word=xyz[2])


@pytest.mark.parametrize('overwritten,expected',[(False,0x0E),(True,0xFE)])
def test_external_qualified_coherent_sample_status_before_observation(overwritten,expected):
    s=active()
    if overwritten:sample(s)
    sample(s,overwritten=overwritten)
    reject_atomic(s,lambda:s.read('STATUS_REG'))
    assert s.read_masked('STATUS_REG',0xFE)==expected
    # No clear trigger is asserted after the hardware-style observation.
    assert s.known['STATUS_REG']==0
    reject_atomic(s,lambda:s.read('STATUS_REG'))


@pytest.mark.parametrize('reg,expected', [('OUT_X_L',0x40),('OUT_X_H',0x12),('OUT_Y_L',0xC0),('OUT_Y_H',0xAB),('OUT_Z_L',0xC0),('OUT_Z_H',0xFF)])
def test_qualified_word_byte_values_and_status_knowledge_invalidation(reg,expected):
    s=active()
    sample(s)
    assert s.read(reg)==expected
    reject_atomic(s,lambda:s.read_masked('STATUS_REG',0xFE))


@pytest.mark.parametrize('kind',['sample_completed','unrecognized','self_test_passed'])
def test_unqualified_or_physical_event_cannot_become_main_evidence(kind):
    s=active()
    reject_atomic(s,lambda:s.event(kind,x_word=0x1240,y_word=0xABC0,z_word=0xFFC0))


@pytest.mark.parametrize('value',[0,1,None,'false',1.0])
def test_external_overwrite_qualification_requires_actual_bool(value):
    s=active()
    reject_atomic(s,lambda:s.event('qualified_sample_completed',x_word=0x1240,y_word=0xABC0,z_word=0xFFC0,overwritten=value))


@pytest.mark.parametrize('st',[1,2])
def test_selftest_configuration_persists_but_mechanical_output_event_excluded(st):
    s=active(ctrl4=st<<1)
    assert s.read('CTRL_REG4')&6 == st<<1
    reject_atomic(s,lambda:sample(s))


@pytest.mark.parametrize('xyz',[(-1,0,0),(65536,0,0),(True,0,0),(1.0,0,0),(1,0,0),(0,1,0),(0,0,1)])
def test_malformed_or_not_leftjustified_sample_rejects_atomically(xyz):
    s=active()
    reject_atomic(s,lambda:sample(s,xyz))


@pytest.mark.parametrize('ctrl1,ctrl4,shift',[(0x17,0,6),(0x17,8,4),(0x1F,0,8)])
def test_normal_highresolution_lowpower_leftjustified_modes(ctrl1,ctrl4,shift):
    s=active(ctrl1=ctrl1,ctrl4=ctrl4)
    word=(0x1234>>shift)<<shift
    sample(s,(word,word,word))
    assert (s.read('OUT_X_H')<<8)|s.read('OUT_X_L')==word
    t=active(ctrl1=ctrl1,ctrl4=ctrl4)
    reject_atomic(t,lambda:sample(t,(word|1,word,word)))


def test_powerdown_rejects_sample():
    s=Semantics()
    reject_atomic(s,lambda:sample(s))


def test_qualified_power_on_restores_known_reset_boundary_not_dynamic_zero():
    s=active(profile='read_consumption_candidate')
    sample(s)
    sample(s)
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    s.event('power_on_completed')
    assert s.read('CTRL_REG1')==7
    assert s.read('CTRL_REG4')==0
    assert s.read_masked('STATUS_REG',0xFE)==0
    reject_atomic(s,lambda:s.read('STATUS_REG'))
    reject_atomic(s,lambda:s.read('OUT_X_H'))


@pytest.mark.parametrize('axis,ready,overrun',[('X',1,16),('Y',2,32),('Z',4,64)])
@pytest.mark.parametrize('order',[('L','H'),('H','L')])
def test_candidate_pair_consumption_requires_both_bytes_preserves_other_axes(axis,ready,overrun,order):
    s=active('read_consumption_candidate')
    sample(s)
    sample(s)
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    s.read(f'OUT_{axis}_{order[0]}')
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    s.read(f'OUT_{axis}_{order[0]}')
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    s.read(f'OUT_{axis}_{order[1]}')
    assert s.read_masked('STATUS_REG',0xFE)==(0xFE&~(ready|overrun))


@pytest.mark.parametrize('order',[('X','Y','Z'),('Z','X','Y'),('Y','Z','X')])
def test_candidate_all_pair_consumption_retires_aggregate_only_after_last_axis(order):
    s=active('read_consumption_candidate')
    sample(s)
    for i,axis in enumerate(order):
        s.read(f'OUT_{axis}_L'); s.read(f'OUT_{axis}_H')
        value=s.read_masked('STATUS_REG',0xFE)
        assert bool(value&8)==(i<2)
    assert s.read_masked('STATUS_REG',0xFE)==0


def test_candidate_read_status_is_observation_not_consumption():
    s=active('read_consumption_candidate')
    sample(s);sample(s)
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    assert s.read_masked('STATUS_REG',2)==2
    assert s.read_masked('STATUS_REG',0xFE)==0xFE


def test_candidate_interleaved_new_sample_restarts_pair_consumption():
    s=active('read_consumption_candidate')
    sample(s)
    s.read('OUT_X_L')
    sample(s,(0x2280,0x33C0,0x4400))
    assert s.read('OUT_X_H')==0x22
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    assert s.read('OUT_X_L')==0x80
    assert s.read_masked('STATUS_REG',0xFE)==0xEE


def test_candidate_bdu_unread_pending_history_excluded_atomically():
    s=active('read_consumption_candidate',ctrl4=0x80)
    sample(s)
    reject_atomic(s,lambda:sample(s))
    for axis in 'XYZ':
        s.read(f'OUT_{axis}_L');s.read(f'OUT_{axis}_H')
    sample(s)
    assert s.read_masked('STATUS_REG',0xFE)==14


def test_main_bdu_enabled_sampling_remains_excluded_even_first_capture():
    s=active(ctrl4=0x80)
    reject_atomic(s,lambda:sample(s))
    assert s.read_masked('STATUS_REG',0xFE)==0
    reject_atomic(s,lambda:s.read('OUT_X_H'))


def test_bigendian_format_only_highresolution_lower_address_is_msb():
    s=active(ctrl4=0x48)
    sample(s,(0x1230,0xABC0,0xFFD0))
    assert s.read('OUT_X_L')==0x12
    assert s.read('OUT_X_H')==0x30
    assert s.read('OUT_Y_L')==0xAB
    assert s.read('OUT_Y_H')==0xC0


def test_candidate_profile_does_not_promote_missing_xda_authority_after_samples():
    s=active('read_consumption_candidate')
    sample(s);sample(s)
    assert s.known['STATUS_REG']==0xFE
    reject_atomic(s,lambda:s.read('STATUS_REG'))
    reject_atomic(s,lambda:s.read_masked('STATUS_REG',1))


@pytest.mark.parametrize('reg',['CTRL_REG4','CTRL_REG1'])
def test_postsample_mode_change_excluded_atomically(reg):
    s=active('read_consumption_candidate')
    sample(s)
    reject_atomic(s,lambda:s.write(reg,0))


def test_masked_output_observation_still_executes_one_whole_byte_candidate_read():
    s=active('read_consumption_candidate')
    sample(s);sample(s)
    assert s.read_masked('OUT_X_L',1)==0
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    assert s.read_masked('OUT_X_H',1)==0
    assert s.read_masked('STATUS_REG',0xFE)==0xEE


@pytest.mark.parametrize('value',[0,2,4,8,16,32,64,128,255])
def test_status_readonly_write_rejected_without_mutation(value):
    s=Semantics()
    reject_atomic(s,lambda:s.write('STATUS_REG',value))


def test_main_status_qualification_cannot_invent_postread_history():
    s=active()
    sample(s)
    assert s.read_masked('STATUS_REG',0xFE)==14
    # A new explicit qualified completion can create a fresh pre-read witness;
    # previous unread/clear history is not inferred by the implementation.
    sample(s,overwritten=True)
    assert s.read_masked('STATUS_REG',0xFE)==0xFE


@pytest.mark.parametrize('ctrl1,ctrl4',[(0x1F,8),(0x17,0x40),(0x87,0)])
def test_illegal_mode_or_endian_setup_rejects_atomically(ctrl1,ctrl4):
    s=Semantics()
    if ctrl4==0x40:
        reject_atomic(s,lambda:s.write('CTRL_REG4',ctrl4))
    else:
        s.write('CTRL_REG4',ctrl4)
        reject_atomic(s,lambda:s.write('CTRL_REG1',ctrl1))


class ColdXdaInvented(Semantics):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.known['STATUS_REG']|=1


class ResetBitCorrupted(Semantics):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.values['STATUS_REG']|=0x80


class StForcedDisabled(Semantics):
    def write(self,reg,value):
        super().write(reg,value)
        if reg=='CTRL_REG4':self.values[reg]&=~6


class NeighborDestroyed(Semantics):
    def write(self,reg,value):
        super().write(reg,value)
        if reg=='CTRL_REG4':self.values[reg]&=6


class NaCodeAccepted(Semantics):
    def write(self,reg,value):
        if reg=='CTRL_REG4' and value&6==6:
            self.values[reg]=value;return
        super().write(reg,value)


class PostReadStatusRetained(Semantics):
    def read_masked(self,reg,mask,*args,**kwargs):
        known=self.known.get(reg)
        result=super().read_masked(reg,mask,*args,**kwargs)
        if reg=='STATUS_REG':self.known[reg]=known
        return result


class OneByteConsumesAxis(Semantics):
    def read_masked(self,reg,mask,*args,**kwargs):
        result=super().read_masked(reg,mask,*args,**kwargs)
        if reg.startswith('OUT_X_'):
            self.values['STATUS_REG']&=~0x11
        return result


class CandidateStatusReadClearsAll(Semantics):
    def read_masked(self,reg,mask,*args,**kwargs):
        result=super().read_masked(reg,mask,*args,**kwargs)
        if reg=='STATUS_REG':self.values[reg]=0
        return result


class MainSampleInventsXda(Semantics):
    def event(self,name,**payload):
        super().event(name,**payload)
        if name=='qualified_sample_completed':self.known['STATUS_REG']|=1


def oracle_reset(cls):
    s=cls();assert s.known['STATUS_REG']==0xFE
    assert s.read_masked('STATUS_REG',0xFE)==0


def oracle_st(cls):
    s=cls();s.write('CTRL_REG4',0x2A)
    assert s.read('CTRL_REG4')==0x2A


def oracle_na(cls):
    s=cls();rejected=False
    try:s.write('CTRL_REG4',6)
    except OutsideContract:rejected=True
    assert rejected


def oracle_main_unknown(cls):
    s=cls();s.write('CTRL_REG1',0x17);sample(s)
    assert s.known['STATUS_REG']==0xFE
    assert s.read_masked('STATUS_REG',0xFE)==0x0E
    assert s.known['STATUS_REG']==0


def oracle_candidate_pair(cls):
    s=cls(profile='read_consumption_candidate');s.write('CTRL_REG1',0x17)
    sample(s);sample(s)
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    s.read('OUT_X_L')
    assert s.read_masked('STATUS_REG',0xFE)==0xFE
    s.read('OUT_X_H')
    assert s.read_masked('STATUS_REG',0xFE)==0xEE


FAULT_ORACLES=[(ColdXdaInvented,oracle_reset),(ResetBitCorrupted,oracle_reset),
 (StForcedDisabled,oracle_st),(NeighborDestroyed,oracle_st),(NaCodeAccepted,oracle_na),
 (PostReadStatusRetained,oracle_main_unknown),(MainSampleInventsXda,oracle_main_unknown),
 (OneByteConsumesAxis,oracle_candidate_pair),(CandidateStatusReadClearsAll,oracle_candidate_pair)]


@pytest.mark.parametrize('fault,oracle',FAULT_ORACLES,ids=[f.__name__ for f,_ in FAULT_ORACLES])
def test_source_oracle_detects_synthetic_runtime_fault(fault,oracle):
    oracle(Semantics)
    with pytest.raises(AssertionError):oracle(fault)


def admission():
    import admission as result
    return result


def witnesses():
    a=admission()
    return {name:a.produce_witness(name) for name in a.SCENARIOS}


def advice():
    return json.loads((ROOT/'source_review.json').read_text(encoding='utf-8'))


def test_exact_evidence_retains_eight_fields_eight_dimensions_and_zero_promotions():
    rows=admission().build_closure(advice(),witnesses())
    assert len(rows)==8
    assert len({r['inventory_field_id'] for r in rows})==8
    assert all(r['assessment']=='BOUNDED_CLAUSES_VERIFIED' and r['source_verdict']=='REPAIR' for r in rows)
    assert all(r['whole_field_promoted'] is False and r['whole_dimension_closed'] is False for r in rows)
    assert sum(r['dimension']=='reset' for r in rows)==7
    assert sum(r['dimension']=='access' for r in rows)==1


@pytest.mark.parametrize('scenario',list(__import__('scenarios').SCENARIOS))
def test_missing_required_scenario_retains_partial_or_unaffected_not_full_admission(scenario):
    data=witnesses();del data[scenario]
    rows=admission().build_closure(advice(),data)
    # Supporting clauses not used by a particular repair field need not make
    # that row partial. No row may promote whole-field/dimension admission.
    if scenario in ('settled_default','legal_st_access','selftest_response_boundary','simultaneous_new_set',
                    'simultaneous_overwrite','common_read_boundary','power_on_defaults',
                    'source_scope_guards','nominal_odr_table'):
        assert any(r['assessment']=='PARTIAL' and r['missing_claim_ids'] for r in rows)
    assert all(r['whole_field_promoted'] is False and r['whole_dimension_closed'] is False for r in rows)


def test_exploratory_policy_cannot_be_relabelled_as_manufacturer_equivalence():
    a=admission();data={'candidate_consumption':a.produce_witness('candidate_consumption')}
    assert data['candidate_consumption']['execution_kind']=='EXPLORATORY_READ_CONSUMPTION_POLICY'
    assert all(r['assessment']=='PARTIAL' for r in a.build_closure(advice(),data))
    data['candidate_consumption']['execution_kind']='VERIFIED_MANUFACTURER_HARDWARE_FACT'
    with pytest.raises(ValueError):a.validate_execution(data)


@pytest.mark.parametrize('variant',['empty_checks','empty_trace','bool_count','float_count','count_change','fake_equal',
 'fake_clause','wrong_chip','wrong_profile','missing_trace','reverse_trace','fake_kind','extra_key',
 'unknown_scenario','wrong_scenario','failed_status','null_result'])
def test_corrupted_or_fabricated_execution_is_rejected(variant):
    data=witnesses();names=list(data);r=data[names[0]]
    if variant=='empty_checks':r['checks']=[]
    elif variant=='empty_trace':r['trace']=[]
    elif variant=='bool_count':r['check_count']=True
    elif variant=='float_count':r['check_count']=float(r['check_count'])
    elif variant=='count_change':r['check_count']+=1
    elif variant=='fake_equal':r['checks'][0]['actual']=r['checks'][0]['expected']='fabricated'
    elif variant=='fake_clause':r['checks'][0]['clause']='silicon certification'
    elif variant=='wrong_chip':r['trace'][0]['chip']='TMP126'
    elif variant=='wrong_profile':r['trace'][0]['profile']='invented'
    elif variant=='missing_trace':r['trace'].pop()
    elif variant=='reverse_trace':r['trace'].reverse()
    elif variant=='fake_kind':r['execution_kind']='PHYSICAL_CHIP_EQUIVALENCE'
    elif variant=='extra_key':r['hardware_pass']=True
    elif variant=='unknown_scenario':data['unknown']=copy.deepcopy(r)
    elif variant=='wrong_scenario':data[names[1]]=copy.deepcopy(r)
    elif variant=='failed_status':r['status']='FAIL'
    elif variant=='null_result':data[names[0]]=None
    with pytest.raises(ValueError):admission().validate_execution(data)


@pytest.mark.parametrize('variant',['foreign_project','wrong_task','fake_sha','unknown_claim','missing_field','duplicate_field','foreign_field','no_conflicts'])
def test_changed_source_identity_or_advice_rejected(variant):
    data=advice()
    if variant=='foreign_project':data['project_id']='other'
    elif variant=='wrong_task':data['task_id']='tmp117-v31/source_review'
    elif variant=='fake_sha':data['source']['sha256']='0'*64
    elif variant=='unknown_claim':data['field_closure_advice'][0]['claims']=['FAKE']
    elif variant=='missing_field':data['field_closure_advice'].pop()
    elif variant=='duplicate_field':data['field_closure_advice'][-1]=data['field_closure_advice'][0]
    elif variant=='foreign_field':data['field_closure_advice'][0]['field']='TMP126.CONFIG.ONE_SHOT'
    elif variant=='no_conflicts':data['conflicts']=[]
    with pytest.raises(ValueError):admission().build_closure(data,witnesses())


@pytest.mark.parametrize('target',['corpus/data/raw_pdf/ST/LIS3DH.pdf','eval/independent_source_admission_20261012/field_evidence.json'])
def test_primary_pdf_and_frozen_authority_are_rehashed(monkeypatch,target):
    a=admission();source=advice();execution=witnesses()
    absolute=(ROOT.parents[1]/target).resolve();original=Path.read_bytes
    def fake_read(path):
        data=original(path)
        return data+b'\nFAKE' if path.resolve()==absolute else data
    monkeypatch.setattr(Path,'read_bytes',fake_read)
    with pytest.raises(ValueError):a.build_closure(source,execution)
