"""
Smart Contract — IP Registry on Tezos
Deploy via SmartPy IDE: https://smartpy.io/ide
═══════════════════════════════════════════════
Titular: Mihai Roșca · tz1bmw3igCLN8N6CqgLBzJ9dyRb79E2Tdu5Q
═══════════════════════════════════════════════

INSTRUCȚIUNI DEPLOY:
1. Deschide https://smartpy.io/ide
2. Paste acest cod complet
3. Click "Run" (buton verde ▶) — verifică că testele trec
4. Click "Deploy Michelson Contract"
5. Selectează "Ghostnet" (testnet) ÎNTÂI pentru test
6. Conectează Temple wallet
7. Confirmă tranzacția în Temple
8. După test OK → deploy pe "Mainnet"
9. Salvează adresa contractului!
"""

import smartpy as sp


@sp.module
def main():
    class IPRegistry(sp.Contract):
        """
        Registru de proprietate intelectuală pe Tezos.
        Stochează hash-uri SHA-256 cu metadata.
        Doar owner-ul poate înregistra.
        """

        def __init__(self, owner):
            self.data.owner = owner
            # Big_map: code (string) → record
            self.data.registry = sp.big_map()
            self.data.total_entries = 0
            self.data.master_hash = sp.bytes("0x")

        @sp.entrypoint
        def register(self, params):
            """
            Înregistrează un hash pe blockchain.
            params: code (string), sha256 (bytes), description (string)
            """
            assert sp.sender == self.data.owner, "NOT_OWNER"
            assert not self.data.registry.contains(params.code), "ALREADY_REGISTERED"

            self.data.registry[params.code] = sp.record(
                sha256=params.sha256,
                description=params.description,
                timestamp=sp.now,
                block_level=sp.level,
            )
            self.data.total_entries += 1

        @sp.entrypoint
        def register_batch(self, params):
            """
            Înregistrează mai multe hash-uri într-o singură tranzacție (economie gas).
            params: list of record(code, sha256, description)
            """
            assert sp.sender == self.data.owner, "NOT_OWNER"

            for entry in params.entries:
                assert not self.data.registry.contains(entry.code), "DUPLICATE"
                self.data.registry[entry.code] = sp.record(
                    sha256=entry.sha256,
                    description=entry.description,
                    timestamp=sp.now,
                    block_level=sp.level,
                )
                self.data.total_entries += 1

        @sp.entrypoint
        def set_master_hash(self, params):
            """
            Setează master hash-ul (hash al tuturor hash-urilor).
            O singură tranzacție = proof pentru întreg portofoliul.
            """
            assert sp.sender == self.data.owner, "NOT_OWNER"
            self.data.master_hash = params.hash

        @sp.entrypoint
        def transfer_ownership(self, params):
            """Transfer proprietate (ex: Mihai → Patrick în viitor)."""
            assert sp.sender == self.data.owner, "NOT_OWNER"
            self.data.owner = params.new_owner


# ═══════════════════════════════════════════════════════════════
# TESTE (rulează automat în SmartPy IDE)
# ═══════════════════════════════════════════════════════════════

@sp.add_test()
def test():
    scenario = sp.test_scenario("IP Registry Test", main)
    scenario.h1("IP Registry — Mihai Roșca")

    # Adresa owner
    owner = sp.address("tz1bmw3igCLN8N6CqgLBzJ9dyRb79E2Tdu5Q")
    attacker = sp.address("tz1attackerXXXXXXXXXXXXXXXXXXXXXXXXX")

    # Deploy
    contract = main.IPRegistry(owner)
    scenario += contract

    # Test: register OK
    scenario.h2("Register single entry")
    contract.register(
        code="INVARIANT-FLEET",
        sha256=sp.bytes("0xaabbccdd"),  # placeholder
        description="Invariantul Flotei Ami* - pattern arhitectural",
        _sender=owner,
    )
    scenario.verify(contract.data.total_entries == 1)

    # Test: register batch
    scenario.h2("Register batch")
    contract.register_batch(
        entries=[
            sp.record(code="UKBE-CORE", sha256=sp.bytes("0x1111"), description="UKBE Core Engine"),
            sp.record(code="TVE-CORE", sha256=sp.bytes("0x2222"), description="Truth Vector Engine"),
            sp.record(code="RSI-ENGINE", sha256=sp.bytes("0x3333"), description="RSI Hybrid Engine"),
        ],
        _sender=owner,
    )
    scenario.verify(contract.data.total_entries == 4)

    # Test: attacker cannot register
    scenario.h2("Attacker blocked")
    contract.register(
        code="HACK",
        sha256=sp.bytes("0xdead"),
        description="Should fail",
        _sender=attacker,
        _valid=False,
    )

    # Test: duplicate blocked
    scenario.h2("Duplicate blocked")
    contract.register(
        code="INVARIANT-FLEET",
        sha256=sp.bytes("0xffff"),
        description="Duplicate",
        _sender=owner,
        _valid=False,
    )

    # Test: master hash
    scenario.h2("Set master hash")
    contract.set_master_hash(
        hash=sp.bytes("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"),
        _sender=owner,
    )

    # Test: transfer ownership (Mihai → Patrick)
    scenario.h2("Transfer ownership")
    patrick = sp.address("tz1PatrickFutureAddressXXXXXXXXXXXXXX")
    contract.transfer_ownership(new_owner=patrick, _sender=owner)
    scenario.verify(contract.data.owner == patrick)
