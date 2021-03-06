"""Tests for stix.ExternalReference"""

import pytest

import stix2

LMCO_RECON = """{
    "kill_chain_name": "lockheed-martin-cyber-kill-chain",
    "phase_name": "reconnaissance"
}"""


def test_lockheed_martin_cyber_kill_chain():
    recon = stix2.KillChainPhase(
        kill_chain_name="lockheed-martin-cyber-kill-chain",
        phase_name="reconnaissance",
    )

    assert str(recon) == LMCO_RECON


FOO_PRE_ATTACK = """{
    "kill_chain_name": "foo",
    "phase_name": "pre-attack"
}"""


def test_kill_chain_example():
    preattack = stix2.KillChainPhase(
        kill_chain_name="foo",
        phase_name="pre-attack",
    )

    assert str(preattack) == FOO_PRE_ATTACK


def test_kill_chain_required_fields():

    with pytest.raises(ValueError) as excinfo:
        stix2.KillChainPhase()

    assert str(excinfo.value) == "Missing required field(s) for KillChainPhase: (kill_chain_name, phase_name)."


def test_kill_chain_required_field_chain_name():

    with pytest.raises(ValueError) as excinfo:
        stix2.KillChainPhase(phase_name="weaponization")

    assert str(excinfo.value) == "Missing required field(s) for KillChainPhase: (kill_chain_name)."


def test_kill_chain_required_field_phase_name():

    with pytest.raises(ValueError) as excinfo:
        stix2.KillChainPhase(kill_chain_name="lockheed-martin-cyber-kill-chain")

    assert str(excinfo.value) == "Missing required field(s) for KillChainPhase: (phase_name)."
