"""Pure policy/stimulus helpers for D2D source-contract protocol 2.0-candidate.

This protocol is a prospective register-abstraction test, not silicon validation.
Unknown bits are ignored and held at defaults; invalid input has no oracle.
"""
import copy


def number(value):
    return int(value, 0) if isinstance(value, str) else int(value)


def bounds(field):
    values = [int(v) for v in field['bits'].split(':')]
    hi, lo = values[0], values[-1]
    return hi, lo, ((1 << (hi - lo + 1)) - 1) << lo


class Contract:
    def __init__(self, ir, policies):
        self.ir = ir
        self.mask = (1 << ir.get('reg_width', 16)) - 1
        self.regs = {r['name']: r for r in ir['registers']}
        self.policy = policies.get('chips', {}).get(ir['device'], {})
        self.fields = {r['name'] + '.' + f['name']: f
                       for r in ir['registers'] for f in r.get('fields', [])}
        assert all(rn in self.regs for rn in self.policy.get('registers', {})), 'Unknown policy register'
        assert all(q in self.fields for q in self.policy.get('fields', {})), 'Unknown policy field'

    def register_policy(self, name):
        return self.policy.get('registers', {}).get(name, {})

    def field_policy(self, qualified):
        return self.policy.get('fields', {}).get(qualified, {})

    def excluded_field(self, qualified):
        f = self.fields[qualified]
        policy = self.field_policy(qualified)
        return (f['access'] == 'UNSPEC'
                or (f.get('tier') == 'UNVERIFIED' and not policy.get('verified_access'))
                or bool(policy.get('exclude')))

    def known_mask(self, name, aspect='reset'):
        r = self.regs[name]
        known = self.mask
        for f in r.get('fields', []):
            qualified = name + '.' + f['name']
            if self.excluded_field(qualified) and not (
                    aspect == 'reset' and self.field_policy(qualified).get('known_reset')):
                known &= ~bounds(f)[2]
        override = self.register_policy(name).get('known_mask')
        if override is not None:
            known &= number(override)
        if aspect == 'protection':
            override = self.register_policy(name).get('protection_known_mask')
            if override is not None:
                known &= number(override)
        return known

    def read_clear_mask(self, name):
        return sum(bounds(f)[2] for f in self.regs[name].get('fields', [])
                   if f.get('read_action') == 'clear') & self.mask

    def legal_values(self, qualified):
        f = self.fields[qualified]
        raw = self.field_policy(qualified).get('legal_values', f.get('legal_values'))
        if raw is not None:
            values = sorted(set(number(v) for v in raw))
        else:
            hi, lo, _ = bounds(f)
            # Two boundary values for unconstrained storage; no exhaustive claim.
            values = [0, (1 << (hi - lo + 1)) - 1]
        limit = 1 << (bounds(f)[0] - bounds(f)[1] + 1)
        assert values and all(0 <= v < limit for v in values), qualified
        return values

    def expected_value(self, qualified, written):
        mapping = self.field_policy(qualified).get('readback_values', {})
        return number(mapping.get(str(written), written))

    def stimulus_values(self, qualified):
        raw = self.field_policy(qualified).get('test_values')
        values = [number(v) for v in raw] if raw is not None else self.legal_values(qualified)
        assert set(values) <= set(self.legal_values(qualified)), qualified
        return values

    def assign(self, state, qualified, value):
        rn, _ = qualified.split('.', 1)
        _, lo, mask = bounds(self.fields[qualified])
        state[rn] = (state[rn] & ~mask) | (number(value) << lo)

    def field_value(self, state, qualified):
        rn, _ = qualified.split('.', 1)
        _, lo, mask = bounds(self.fields[qualified])
        return (state[rn] & mask) >> lo

    def constrained_state(self, qualified, value):
        """Plan prerequisites and one tested write from a fresh power-on state."""
        state = {rn: number(r.get('reset', '0x0')) for rn, r in self.regs.items()}
        self.assign(state, qualified, value)
        for _ in range(8):
            before = copy.copy(state)
            for rule in self.policy.get('constraints', []):
                matched = all(self.field_value(state, key) in [number(v) for v in allowed]
                              for key, allowed in rule['when'].items())
                if matched:
                    for key, val in rule['set'].items():
                        self.assign(state, key, val)
            if state == before:
                break
        else:
            raise ValueError('Constraint cycle: ' + qualified)
        # A constraint may never overwrite the requested test value.
        assert self.field_value(state, qualified) == value, qualified
        self.validate_state(state)
        return state

    def validate_state(self, state):
        for qualified, f in self.fields.items():
            policy = self.field_policy(qualified)
            raw = policy.get('legal_values', f.get('legal_values'))
            if raw is not None:
                assert self.field_value(state, qualified) in [number(v) for v in raw], qualified
            if 'fixed_write' in policy:
                assert self.field_value(state, qualified) == number(policy['fixed_write']), qualified
        for rule in self.policy.get('constraints', []):
            if all(self.field_value(state, key) in [number(v) for v in vals]
                   for key, vals in rule['when'].items()):
                assert all(self.field_value(state, key) == number(val)
                           for key, val in rule['set'].items()), rule

    def writes(self, qualified, value):
        state = self.constrained_state(qualified, value)
        target = qualified.split('.', 1)[0]
        # Apply cross-register prerequisites first; the target is always last.
        names = [rn for rn, r in self.regs.items() if rn != target
                 and state[rn] != number(r.get('reset', '0x0'))]
        names.append(target)
        return [(number(self.regs[rn].get('write_addr', self.regs[rn]['addr'])), state[rn])
                for rn in names]

    def rw_cases(self):
        cases = []
        for rn, r in self.regs.items():
            if r['access'] != 'RW' or self.register_policy(rn).get('exclude_writes'):
                continue
            for f in r.get('fields', []):
                qualified = rn + '.' + f['name']
                if self.excluded_field(qualified) or not bounds(f)[2] & self.known_mask(rn):
                    continue
                if f['access'] == 'RW' and f.get('read_as') is None:
                    values = self.stimulus_values(qualified)
                    # A mandated constant input cannot establish writability.
                    if len(values) > 1:
                        cases.extend((qualified, value) for value in values)
        return cases

    def ro_field_cases(self):
        return [(rn + '.' + f['name'], f) for rn, r in self.regs.items()
                if r['access'] == 'RW' and not self.register_policy(rn).get('exclude_writes')
                for f in r.get('fields', []) if f['access'] == 'RO'
                and f.get('read_action') != 'clear'
                and not self.excluded_field(rn + '.' + f['name'])
                and self.known_mask(rn) & bounds(f)[2]]

    def perturbation_cases(self):
        return [(q, v) for q, v in self.rw_cases()
                if self.expected_value(q, v) != self.fields[q].get('reset', 0)
                and not self.regs[q.split('.', 1)[0]].get('runtime_value')
                and bounds(self.fields[q])[2] & self.known_mask(q.split('.', 1)[0])
                & ~self.read_clear_mask(q.split('.', 1)[0])]

    def applicable(self):
        return {
            'test_reset_values': any(not r.get('runtime_value') and r['access'] != 'W'
                                     and self.known_mask(rn) for rn, r in self.regs.items()),
            'test_readonly_protection': any(r['access'] == 'RO'
                                            and self.known_mask(rn, 'protection') & ~self.read_clear_mask(rn)
                                            for rn, r in self.regs.items()),
            'test_rw_field_persistence': bool(self.rw_cases() or self.ro_field_cases()),
            'test_write_trigger_fields': any(r['access'] == 'RW'
                    and not self.register_policy(rn).get('exclude_writes')
                    and f['access'] == 'RW' and f.get('read_as') is not None
                    and not self.excluded_field(rn + '.' + f['name'])
                    and bounds(f)[2] & self.known_mask(rn)
                    and max(self.legal_values(rn + '.' + f['name'])) > 0
                    for rn, r in self.regs.items() for f in r.get('fields', [])),
            'test_single_byte_semantics': bool((self.ir.get('single_byte_semantics') or {}).get('test_register'))
                    and (self.ir.get('single_byte_semantics') or {}).get('applies_to') not in ('none', None)
                    and bool(self.known_mask(self.ir['single_byte_semantics']['test_register'])),
            'test_read_write_alias': any(self.regs[q.split('.', 1)[0]].get('write_addr')
                                         for q, _ in self.rw_cases()),
            'test_clear_on_read': any(r.get('cor_addr') and self.known_mask(rn)
                                      for rn, r in self.regs.items()),
            'test_write_only_reset_key': any(r['access'] == 'W' and r.get('write_key')
                                            for r in self.regs.values())
                    and bool(self.perturbation_cases()),
        }
