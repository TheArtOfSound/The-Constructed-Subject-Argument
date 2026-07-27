#!/usr/bin/env python3
from __future__ import annotations
import unittest

from anchor_review_generation_commitment import (
    CommitmentValidationError, build_postcommit, build_precommit,
    canonical_digest, seed_commitment, validate_postcommit, validate_precommit,
)

CODE_SHA = "a" * 40
MANIFEST_DIGEST = "b" * 64


def pre():
    return build_precommit(
        ceremony_id="EGC2-AR-20260727-01",
        repository="TheArtOfSound/The-Constructed-Subject-Argument",
        code_commit_sha=CODE_SHA,
        manifest_id="egc2-first-24-anchor-development-bank-v0.1.0",
        manifest_digest=MANIFEST_DIGEST,
        reviewer_ids=["R03", "R01", "R02"],
        seed_commitment_sha256=seed_commitment("secret", "private-nonce", "EGC2-AR-20260727-01"),
        operator_pseudonym="OP01",
        created_at_utc="2026-07-27T05:00:00Z",
    )


def post(p):
    return build_postcommit(
        precommit=p,
        public_queue_digests={"R01": "1" * 64, "R02": "2" * 64, "R03": "3" * 64},
        protected_bundle_digest="4" * 64,
        generator_version="harden-anchor-review-0.2.0",
        python_version="3.12.4",
        generated_at_utc="2026-07-27T05:05:00Z",
        witness_pseudonyms=["W02", "W01"],
    )


class CommitmentTests(unittest.TestCase):
    def test_seed_commitment_is_domain_separated_and_deterministic(self):
        x = seed_commitment("secret", "nonce", "ceremony")
        self.assertEqual(x, seed_commitment("secret", "nonce", "ceremony"))
        self.assertNotEqual(x, seed_commitment("secret", "other", "ceremony"))

    def test_precommit_sorts_reviewer_ids_and_validates(self):
        p = pre()
        self.assertEqual(p["reviewer_ids"], ["R01", "R02", "R03"])
        self.assertTrue(validate_precommit(p)["valid"])

    def test_precommit_rejects_secret_material_even_if_redigested(self):
        p = pre()
        p["secret_seed"] = "leak"
        p["precommit_digest_sha256"] = canonical_digest({k: v for k, v in p.items() if k != "precommit_digest_sha256"})
        with self.assertRaises(CommitmentValidationError):
            validate_precommit(p)

    def test_precommit_rejects_reviewer_identity_fields(self):
        p = pre()
        p["administration"] = {"reviewer_email": "person@example.com"}
        p["precommit_digest_sha256"] = canonical_digest({k: v for k, v in p.items() if k != "precommit_digest_sha256"})
        with self.assertRaises(CommitmentValidationError):
            validate_precommit(p)

    def test_postcommit_closes_exact_reviewer_set(self):
        p = pre()
        q = post(p)
        result = validate_postcommit(p, q)
        self.assertTrue(result["valid"])
        self.assertEqual(result["reviewer_count"], 3)
        self.assertEqual(len(result["review_run_commitment_sha256"]), 64)

    def test_postcommit_rejects_missing_queue_even_if_redigested(self):
        p = pre()
        q = post(p)
        q["public_queue_digests_sha256"].pop("R03")
        run_material = {
            "precommit_digest_sha256": q["precommit_digest_sha256"],
            "public_queue_digests_sha256": q["public_queue_digests_sha256"],
            "protected_bundle_digest_sha256": q["protected_bundle_digest_sha256"],
        }
        q["review_run_commitment_sha256"] = canonical_digest(run_material)
        q["postcommit_digest_sha256"] = canonical_digest({k: v for k, v in q.items() if k != "postcommit_digest_sha256"})
        with self.assertRaises(CommitmentValidationError):
            validate_postcommit(p, q)

    def test_postcommit_rejects_cross_ceremony_rebinding(self):
        p = pre()
        q = post(p)
        q["ceremony_id"] = "EGC2-AR-OTHER"
        q["postcommit_digest_sha256"] = canonical_digest({k: v for k, v in q.items() if k != "postcommit_digest_sha256"})
        with self.assertRaises(CommitmentValidationError):
            validate_postcommit(p, q)

    def test_postcommit_rejects_protected_mapping_leak(self):
        p = pre()
        q = post(p)
        q["protected_mapping"] = {"P-opaque": "A001"}
        q["postcommit_digest_sha256"] = canonical_digest({k: v for k, v in q.items() if k != "postcommit_digest_sha256"})
        with self.assertRaises(CommitmentValidationError):
            validate_postcommit(p, q)


if __name__ == "__main__":
    unittest.main(verbosity=2)
