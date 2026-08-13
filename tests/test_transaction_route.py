import unittest

from core_lite.transaction_route import ManifestRouteCarrier, RouteCarrierError, build_route_manifest, default_validation_route


class MemorySink:
    def __init__(self, fail_sequence=None):
        self.events = []
        self.fail_sequence = fail_sequence

    def __call__(self, event):
        seq = event["sequence"]
        if self.fail_sequence == seq:
            return {"custody_status": "FAILED"}
        previous = None if not self.events else self.events[-1]["event_hash"]
        recorded = dict(event)
        recorded["route_manifest_id"] = self.route_id
        recorded["previous_event_hash"] = previous
        recorded["event_hash"] = f"hash-{seq}"
        recorded["route_receipt_id"] = f"MRR-{seq}"
        self.events.append(recorded)
        return {"custody_status": "RECORDED", "event": recorded}


class TransactionRouteTests(unittest.TestCase):
    def manifest(self):
        return build_route_manifest(
            transaction_id="TX-TEST-1",
            execution_provenance={
                "lane_class": "PRODUCTION_VALIDATION",
                "routing_surface": "CANONICAL_PRODUCTION",
                "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
                "external_consequence_enabled": False,
            },
            route=default_validation_route(),
            source="StegVerse-SDK",
            purpose="evaluator-validation",
        )

    def test_production_validation_route_is_receipt_gated(self):
        manifest = self.manifest()
        sink = MemorySink(); sink.route_id = manifest["route_manifest_id"]
        carrier = ManifestRouteCarrier(manifest, sink)
        result = carrier.run({"value": 420}, {"stegcore": lambda _m, payload: {"decision": "ALLOW", "input": payload}})
        self.assertTrue(result["completed"])
        self.assertEqual(10, result["route_transition_count"])
        self.assertEqual("PRODUCTION_VALIDATION", result["route_manifest"]["execution_provenance"]["lane_class"])
        self.assertEqual("RETURNED", sink.events[-1]["event_type"])
        self.assertEqual([f"hash-{i}" if i >= 0 else None for i in range(len(sink.events) - 1)], [e["previous_event_hash"] for e in sink.events[1:]])

    def test_unrecorded_transition_blocks_route(self):
        manifest = self.manifest()
        sink = MemorySink(fail_sequence=3); sink.route_id = manifest["route_manifest_id"]
        carrier = ManifestRouteCarrier(manifest, sink)
        with self.assertRaises(RouteCarrierError):
            carrier.run({"value": 420}, {"stegcore": lambda _m, payload: payload})

    def test_manifest_identity_changes_with_lane_provenance(self):
        production = self.manifest()
        demo = build_route_manifest(
            transaction_id="TX-TEST-1",
            execution_provenance={"lane_class": "ENCLOSED_DEMO_TEST", "routing_surface": "DEMO_TEST_REPOSITORY"},
            route=default_validation_route(),
            source="StegGhost",
            purpose="demo",
        )
        self.assertNotEqual(production["route_manifest_id"], demo["route_manifest_id"])


if __name__ == "__main__": unittest.main()
