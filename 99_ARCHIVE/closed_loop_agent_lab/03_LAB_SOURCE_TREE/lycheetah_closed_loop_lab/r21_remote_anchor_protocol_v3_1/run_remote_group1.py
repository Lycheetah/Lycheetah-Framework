"""Isolated subprocess group for the v3.1 HTTP protocol tests."""
import sys, unittest
from test_remote_anchor_http import RemoteAnchorHTTPTests

NAMES = ['test_ambiguous_post_and_unavailable_lookup_remains_unknown_then_recovers', 'test_append_refuses_to_extend_tampered_existing_history', 'test_auth_request_nonce_replay_is_rejected', 'test_bad_database_id_is_refused_by_outbox', 'test_bad_service_request_auth_is_denied', 'test_changed_snapshot_cannot_be_submitted_under_existing_approval', 'test_client_does_not_follow_redirect_with_authenticated_request', 'test_client_rejects_nonpositive_timeout', 'test_committed_outbox_response_cannot_be_rewritten_in_terminal_state', 'test_committed_outbox_state_is_terminal', 'test_concurrent_competing_cas_appends_have_one_winner', 'test_conflict_outbox_state_is_terminal', 'test_database_identity_is_bound_by_approval', 'test_expired_operator_approval_is_refused']
suite = unittest.TestSuite(RemoteAnchorHTTPTests(name) for name in NAMES)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
