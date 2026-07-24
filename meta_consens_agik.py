import smartpy as sp

# ============================================================
# META-CONSENS AGIK
# Tezos Smart Contract — Multi-Agent Consensus for Child Safety
#
# Architecture:
#   L4  Maestru opens a consensus round
#   L1  Agents submit independent verdicts
#   L2  Concordance calculates agreement %
#   L0  Tezos seals the result immutably
#
# Mihai Rosca — BRIDGRAI · Spiru Haret, Braila
# 24 iulie 2026
# ============================================================


@sp.module
def main():

    # --- Types ---

    class Verdict(sp.Record):
        agent = sp.string
        decision = sp.string        # SAFE / CAUTION / BLOCK
        confidence = sp.nat          # 0-100
        reasoning_hash = sp.bytes    # SHA-256 of full reasoning
        timestamp = sp.timestamp

    class ConsensusRound(sp.Record):
        topic = sp.string
        opened_by = sp.address
        opened_at = sp.timestamp
        closed_at = sp.option[sp.timestamp]
        verdicts = sp.map[sp.string, Verdict]
        concordance_pct = sp.nat     # 0-100
        status = sp.string           # OPEN / CONSENSUS / DISSENT / META_VERIFIED
        safety_level = sp.string     # SAFE / CAUTION / BLOCK
        meta_hash = sp.option[sp.bytes]
        child_context = sp.string    # age group or context identifier

    # --- Contract ---

    class MetaConsensAGIK(sp.Contract):
        def __init__(self, admin):
            self.data.admin = admin
            self.data.rounds = sp.cast(
                sp.big_map(),
                sp.big_map[sp.nat, ConsensusRound]
            )
            self.data.round_count = sp.nat(0)
            self.data.agents = sp.cast(sp.set(), sp.set[sp.string])
            self.data.min_concordance = sp.nat(70)
            self.data.min_agents = sp.nat(3)
            self.data.total_consensus = sp.nat(0)
            self.data.total_dissent = sp.nat(0)
            self.data.total_blocks = sp.nat(0)
            self.data.paused = False

        # --- Admin ---

        @sp.entrypoint
        def register_agent(self, name):
            sp.cast(name, sp.string)
            assert sp.sender == self.data.admin, "ONLY_ADMIN"
            self.data.agents.add(name)

        @sp.entrypoint
        def remove_agent(self, name):
            sp.cast(name, sp.string)
            assert sp.sender == self.data.admin, "ONLY_ADMIN"
            self.data.agents.remove(name)

        @sp.entrypoint
        def set_min_concordance(self, pct):
            sp.cast(pct, sp.nat)
            assert sp.sender == self.data.admin, "ONLY_ADMIN"
            assert pct <= 100, "INVALID_PCT"
            self.data.min_concordance = pct

        @sp.entrypoint
        def set_min_agents(self, n):
            sp.cast(n, sp.nat)
            assert sp.sender == self.data.admin, "ONLY_ADMIN"
            assert n >= 2, "MIN_TWO_AGENTS"
            self.data.min_agents = n

        @sp.entrypoint
        def pause(self):
            assert sp.sender == self.data.admin, "ONLY_ADMIN"
            self.data.paused = True

        @sp.entrypoint
        def unpause(self):
            assert sp.sender == self.data.admin, "ONLY_ADMIN"
            self.data.paused = False

        # --- Consensus Flow ---

        @sp.entrypoint
        def open_round(self, params):
            topic = sp.cast(params.topic, sp.string)
            child_context = sp.cast(params.child_context, sp.string)
            assert not self.data.paused, "CONTRACT_PAUSED"

            round_id = self.data.round_count
            self.data.rounds[round_id] = sp.record(
                topic=topic,
                opened_by=sp.sender,
                opened_at=sp.now,
                closed_at=sp.cast(None, sp.option[sp.timestamp]),
                verdicts=sp.cast(sp.map(), sp.map[sp.string, Verdict]),
                concordance_pct=sp.nat(0),
                status="OPEN",
                safety_level="PENDING",
                meta_hash=sp.cast(None, sp.option[sp.bytes]),
                child_context=child_context,
            )
            self.data.round_count = round_id + 1

        @sp.entrypoint
        def submit_verdict(self, params):
            round_id = sp.cast(params.round_id, sp.nat)
            agent = sp.cast(params.agent, sp.string)
            decision = sp.cast(params.decision, sp.string)
            confidence = sp.cast(params.confidence, sp.nat)
            reasoning_hash = sp.cast(params.reasoning_hash, sp.bytes)

            assert not self.data.paused, "CONTRACT_PAUSED"
            assert self.data.agents.contains(agent), "UNREGISTERED_AGENT"
            assert self.data.rounds.contains(round_id), "ROUND_NOT_FOUND"
            assert confidence <= 100, "INVALID_CONFIDENCE"
            assert (decision == "SAFE") | (decision == "CAUTION") | (decision == "BLOCK"), "INVALID_DECISION"

            round_ = self.data.rounds[round_id]
            assert round_.status == "OPEN", "ROUND_NOT_OPEN"
            assert not round_.verdicts.contains(agent), "ALREADY_VOTED"

            round_.verdicts[agent] = sp.record(
                agent=agent,
                decision=decision,
                confidence=confidence,
                reasoning_hash=reasoning_hash,
                timestamp=sp.now,
            )
            self.data.rounds[round_id] = round_

        @sp.entrypoint
        def close_round(self, round_id):
            sp.cast(round_id, sp.nat)
            assert self.data.rounds.contains(round_id), "ROUND_NOT_FOUND"

            round_ = self.data.rounds[round_id]
            assert round_.status == "OPEN", "ROUND_NOT_OPEN"

            verdict_count = sp.len(round_.verdicts)
            assert verdict_count >= self.data.min_agents, "NOT_ENOUGH_VERDICTS"

            # Count decisions
            safe_count = sp.local("safe_count", sp.nat(0))
            caution_count = sp.local("caution_count", sp.nat(0))
            block_count = sp.local("block_count", sp.nat(0))
            total_confidence = sp.local("total_confidence", sp.nat(0))

            for agent in round_.verdicts.keys():
                v = round_.verdicts[agent]
                total_confidence.value += v.confidence
                if v.decision == "SAFE":
                    safe_count.value += 1
                if v.decision == "CAUTION":
                    caution_count.value += 1
                if v.decision == "BLOCK":
                    block_count.value += 1

            # Concordance = max(votes for any single decision) / total * 100
            max_agreement = safe_count.value
            majority_decision = sp.local("majority_decision", "SAFE")

            if caution_count.value > max_agreement:
                max_agreement = caution_count.value
                majority_decision.value = "CAUTION"
            if block_count.value > max_agreement:
                max_agreement = block_count.value
                majority_decision.value = "BLOCK"

            concordance = max_agreement * 100 // verdict_count

            # Safety override: ANY block vote forces BLOCK
            final_safety = sp.local("final_safety", majority_decision.value)
            if block_count.value > 0:
                final_safety.value = "BLOCK"

            # Status based on concordance threshold
            final_status = sp.local("final_status", "DISSENT")
            if concordance >= self.data.min_concordance:
                final_status.value = "CONSENSUS"

            # Update round
            round_.concordance_pct = concordance
            round_.status = final_status.value
            round_.safety_level = final_safety.value
            round_.closed_at = sp.Some(sp.now)
            self.data.rounds[round_id] = round_

            # Update stats
            if final_status.value == "CONSENSUS":
                self.data.total_consensus += 1
            else:
                self.data.total_dissent += 1
            if final_safety.value == "BLOCK":
                self.data.total_blocks += 1

        @sp.entrypoint
        def meta_verify(self, params):
            round_id = sp.cast(params.round_id, sp.nat)
            meta_hash = sp.cast(params.meta_hash, sp.bytes)

            assert sp.sender == self.data.admin, "ONLY_ADMIN"
            assert self.data.rounds.contains(round_id), "ROUND_NOT_FOUND"

            round_ = self.data.rounds[round_id]
            assert (round_.status == "CONSENSUS") | (round_.status == "DISSENT"), "ROUND_STILL_OPEN"

            round_.status = "META_VERIFIED"
            round_.meta_hash = sp.Some(meta_hash)
            self.data.rounds[round_id] = round_


# ============================================================
# TESTS
# ============================================================

@sp.add_test()
def test_meta_consens():
    sc = sp.test_scenario("MetaConsensAGIK", main)
    admin = sp.test_account("admin")
    user1 = sp.test_account("user1")

    c = main.MetaConsensAGIK(admin.address)
    sc += c

    # Register agents
    c.register_agent("SENS", _sender=admin)
    c.register_agent("ACR", _sender=admin)
    c.register_agent("CASP", _sender=admin)
    c.register_agent("CONCORDANCE", _sender=admin)
    c.register_agent("HASN", _sender=admin)

    # Open round
    c.open_round(
        sp.record(
            topic="Conversatie copil 7 ani — detectie manipulare",
            child_context="7-10 ani"
        ),
        _sender=admin
    )

    # Submit verdicts
    c.submit_verdict(sp.record(
        round_id=0, agent="SENS", decision="SAFE",
        confidence=85, reasoning_hash=sp.bytes("0x01")
    ), _sender=admin)

    c.submit_verdict(sp.record(
        round_id=0, agent="ACR", decision="SAFE",
        confidence=90, reasoning_hash=sp.bytes("0x02")
    ), _sender=admin)

    c.submit_verdict(sp.record(
        round_id=0, agent="CASP", decision="SAFE",
        confidence=88, reasoning_hash=sp.bytes("0x03")
    ), _sender=admin)

    c.submit_verdict(sp.record(
        round_id=0, agent="CONCORDANCE", decision="CAUTION",
        confidence=72, reasoning_hash=sp.bytes("0x04")
    ), _sender=admin)

    # Close round — 3/4 SAFE = 75% concordance > 70% threshold
    c.close_round(0, _sender=admin)

    # Verify
    sc.verify(c.data.rounds[0].concordance_pct == 75)
    sc.verify(c.data.rounds[0].status == "CONSENSUS")
    sc.verify(c.data.rounds[0].safety_level == "SAFE")
    sc.verify(c.data.total_consensus == 1)

    # Meta-verify
    c.meta_verify(sp.record(
        round_id=0, meta_hash=sp.bytes("0xABCD")
    ), _sender=admin)

    sc.verify(c.data.rounds[0].status == "META_VERIFIED")

    # --- Test BLOCK override ---
    c.open_round(
        sp.record(
            topic="Continut suspect — posibila manipulare emotionala",
            child_context="4-6 ani"
        ),
        _sender=admin
    )

    c.submit_verdict(sp.record(
        round_id=1, agent="SENS", decision="BLOCK",
        confidence=95, reasoning_hash=sp.bytes("0x10")
    ), _sender=admin)

    c.submit_verdict(sp.record(
        round_id=1, agent="ACR", decision="SAFE",
        confidence=60, reasoning_hash=sp.bytes("0x11")
    ), _sender=admin)

    c.submit_verdict(sp.record(
        round_id=1, agent="CASP", decision="CAUTION",
        confidence=78, reasoning_hash=sp.bytes("0x12")
    ), _sender=admin)

    c.close_round(1, _sender=admin)

    # Even though majority is not BLOCK, ANY block vote forces BLOCK safety
    sc.verify(c.data.rounds[1].safety_level == "BLOCK")
    sc.verify(c.data.total_blocks == 1)
