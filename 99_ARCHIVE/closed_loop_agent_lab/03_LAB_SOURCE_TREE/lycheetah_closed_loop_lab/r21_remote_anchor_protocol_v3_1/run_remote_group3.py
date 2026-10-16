"""Isolated subprocess group for the v3.1 HTTP protocol tests."""
import sys, unittest
from test_remote_anchor_http import RemoteAnchorHTTPTests

NAMES = ['test_outbox_request_id_cannot_be_reused_with_new_content', 'test_outbox_row_tampering_is_detected', 'test_outbox_survives_reopen_and_can_resume', 'test_remote_service_restart_recovers_committed_append_from_durable_request_index', 'test_response_body_tampering_is_detected_then_resolved_by_lookup', 'test_same_request_and_same_body_replays_exact_original_record', 'test_same_request_id_with_changed_body_is_conflict', 'test_service_history_and_request_results_are_signed', 'test_service_rejects_invalid_public_key_registry', 'test_stale_parent_is_conflict_and_not_silently_rebased', 'test_unknown_resumption_queries_status_before_any_new_post', 'test_untrusted_operator_key_id_is_refused', 'test_untrusted_server_public_key_is_refused_at_client_creation']
suite = unittest.TestSuite(RemoteAnchorHTTPTests(name) for name in NAMES)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
