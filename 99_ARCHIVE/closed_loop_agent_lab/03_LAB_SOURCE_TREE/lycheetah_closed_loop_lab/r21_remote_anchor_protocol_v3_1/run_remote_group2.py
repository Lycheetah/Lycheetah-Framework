"""Isolated subprocess group for the v3.1 HTTP protocol tests."""
import sys, unittest
from test_remote_anchor_http import RemoteAnchorHTTPTests

NAMES = ['test_happy_path_publishes_one_signed_record', 'test_header_authentication_is_case_insensitive_at_http_boundary', 'test_history_verification_rejects_record_body_mutation', 'test_http_loopback_must_be_explicitly_enabled', 'test_http_server_rejects_oversized_body_before_json_parse', 'test_logical_snapshot_digest_must_bind_components', 'test_lost_commit_and_unavailable_lookup_then_resend_same_key_is_idempotent', 'test_lost_response_after_commit_is_reconciled_by_request_lookup', 'test_lost_response_before_commit_retries_same_request_id', 'test_malformed_approval_signature_encoding_is_refused_as_client_error', 'test_modified_approval_signature_is_refused', 'test_no_anchor_history_is_empty_and_signed', 'test_non_loopback_plain_http_is_refused', 'test_orphaned_idempotency_index_cannot_masquerade_as_committed']
suite = unittest.TestSuite(RemoteAnchorHTTPTests(name) for name in NAMES)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
