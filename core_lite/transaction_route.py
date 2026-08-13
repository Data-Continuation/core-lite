from __future__ import annotations

import hashlib
import json
import uuid
from copy import deepcopy
from typing import Any, Callable, Mapping


class RouteCarrierError(RuntimeError):
    pass


TransitionSink = Callable[[dict[str, Any]], Mapping[str, Any]]
ModuleHandler = Callable[[dict[str, Any], Any], Any]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def build_route_manifest(
    *,
    transaction_id: str | None = None,
    execution_provenance: Mapping[str, Any],
    route: list[Mapping[str, Any]],
    source: str,
    purpose: str,
) -> dict[str, Any]:
    if not route:
        raise RouteCarrierError("manifest route must contain at least one stop")
    tx = (transaction_id or ("TX-" + uuid.uuid4().hex.upper())).strip()
    if not tx:
        raise RouteCarrierError("transaction_id is required")
    provenance = dict(execution_provenance)
    if not provenance.get("lane_class"):
        raise RouteCarrierError("execution_provenance.lane_class is required")
    normalized_route: list[dict[str, Any]] = []
    for index, raw in enumerate(route):
        item = dict(raw)
        checkpoint_id = str(item.get("checkpoint_id") or f"route:{index}")
        module = str(item.get("module") or "").strip()
        kind = str(item.get("kind") or "module").strip().lower()
        if not module:
            raise RouteCarrierError(f"route[{index}].module is required")
        normalized_route.append(
            {
                "index": index,
                "checkpoint_id": checkpoint_id,
                "module": module,
                "kind": kind,
                "requires_receipt_from": None if index == 0 else normalized_route[index - 1]["checkpoint_id"],
            }
        )
    immutable = {
        "schema": "stegverse.manifested-route.v1",
        "transaction_id": tx,
        "source": source,
        "purpose": purpose,
        "execution_provenance": provenance,
        "route": normalized_route,
    }
    manifest_id = "MF-" + canonical_sha256(immutable).upper()
    return {
        **immutable,
        "route_manifest_id": manifest_id,
        "receipt_bindings": [],
        "receipt_chain_head": None,
        "current_route_index": -1,
        "completed": False,
    }


def default_validation_route() -> list[dict[str, Any]]:
    return [
        {"checkpoint_id": "sdk:entry", "module": "stegverse-sdk", "kind": "entry"},
        {"checkpoint_id": "cge:ingress", "module": "core-lite-ingestion-cge", "kind": "router"},
        {"checkpoint_id": "stegcore:evaluate", "module": "stegcore", "kind": "module"},
        {"checkpoint_id": "cge:return", "module": "core-lite-ingestion-cge", "kind": "router_return"},
        {"checkpoint_id": "sdk:return", "module": "stegverse-sdk", "kind": "return"},
    ]


class ManifestRouteCarrier:
    """Advance a manifested transaction only after each transition is durably receipted."""

    def __init__(self, manifest: Mapping[str, Any], transition_sink: TransitionSink) -> None:
        self.manifest = deepcopy(dict(manifest))
        self.transition_sink = transition_sink
        self.sequence = 0
        self.last_route_receipt_id: str | None = None
        self.last_event_hash: str | None = None

    def _heartbeat(self, checkpoint_id: str) -> dict[str, Any]:
        return {
            "schema": "stegverse.heartbeat-carrier-signal.v1",
            "route_manifest_id": self.manifest["route_manifest_id"],
            "transaction_id": self.manifest["transaction_id"],
            "sequence": self.sequence,
            "checkpoint_id": checkpoint_id,
            "previous_route_receipt_id": self.last_route_receipt_id,
            "previous_event_hash": self.last_event_hash,
        }

    def _record(
        self,
        event_type: str,
        checkpoint: Mapping[str, Any],
        *,
        input_value: Any = None,
        output_value: Any = None,
        details: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = {
            "transaction_id": self.manifest["transaction_id"],
            "sequence": self.sequence,
            "event_type": event_type,
            "checkpoint_id": checkpoint["checkpoint_id"],
            "module": checkpoint["module"],
            "route_index": checkpoint["index"],
            "input_sha256": canonical_sha256(input_value) if input_value is not None else None,
            "output_sha256": canonical_sha256(output_value) if output_value is not None else None,
            "execution_provenance": deepcopy(self.manifest["execution_provenance"]),
            "details": {**dict(details or {}), "heartbeat_carrier": self._heartbeat(checkpoint["checkpoint_id"])},
            "authority_granted": False,
        }
        receipt = dict(self.transition_sink(event))
        if receipt.get("custody_status") != "RECORDED":
            raise RouteCarrierError(f"transition {event_type} was not recorded")
        recorded = receipt.get("event")
        if not isinstance(recorded, Mapping):
            raise RouteCarrierError(f"transition {event_type} returned no canonical event receipt")
        route_receipt_id = str(recorded.get("route_receipt_id") or "")
        event_hash = str(recorded.get("event_hash") or "")
        if not route_receipt_id or not event_hash:
            raise RouteCarrierError(f"transition {event_type} returned incomplete receipt")
        binding = {
            "sequence": self.sequence,
            "checkpoint_id": checkpoint["checkpoint_id"],
            "event_type": event_type,
            "route_receipt_id": route_receipt_id,
            "event_hash": event_hash,
            "previous_event_hash": recorded.get("previous_event_hash"),
        }
        self.manifest["receipt_bindings"].append(binding)
        self.manifest["receipt_chain_head"] = event_hash
        self.last_route_receipt_id = route_receipt_id
        self.last_event_hash = event_hash
        self.sequence += 1
        return receipt

    def _require_previous_checkpoint_receipt(self, checkpoint: Mapping[str, Any]) -> None:
        required = checkpoint.get("requires_receipt_from")
        if required is None:
            return
        if not any(binding.get("checkpoint_id") == required for binding in self.manifest["receipt_bindings"]):
            raise RouteCarrierError(f"route checkpoint {checkpoint['checkpoint_id']} blocked: prior receipt {required} missing")

    def run(self, payload: Any, handlers: Mapping[str, ModuleHandler]) -> dict[str, Any]:
        route = self.manifest.get("route")
        if not isinstance(route, list) or not route:
            raise RouteCarrierError("manifest route is missing")
        first = route[0]
        self._record("MANIFEST_ESTABLISHED", first, input_value=self.manifest, details={"route_length": len(route)})
        current = payload
        module_results: dict[str, Any] = {}
        for checkpoint in route:
            self._require_previous_checkpoint_receipt(checkpoint)
            self.manifest["current_route_index"] = checkpoint["index"]
            kind = checkpoint["kind"]
            if kind == "entry":
                self._record("SDK_ENTERED", checkpoint, input_value=current)
            elif kind == "router":
                self._record("INGESTION_ENTERED", checkpoint, input_value=current)
                self._record("CGE_ADMITTED", checkpoint, input_value=current, details={"prior_receipt_verified": True})
                self._record("CGE_ROUTED", checkpoint, input_value=current, details={"next_route_index": checkpoint["index"] + 1})
            elif kind == "module":
                self._record("MODULE_ENTERED", checkpoint, input_value=current)
                handler = handlers.get(checkpoint["module"])
                if handler is None:
                    self._record("FAIL_CLOSED", checkpoint, input_value=current, details={"reason": "module_handler_missing"})
                    raise RouteCarrierError(f"no handler for routed module {checkpoint['module']}")
                current = handler(self.manifest, current)
                module_results[checkpoint["checkpoint_id"]] = current
                self._record("MODULE_RESULT", checkpoint, output_value=current)
            elif kind == "router_return":
                self._record("CGE_RETURN_INGESTED", checkpoint, input_value=current, details={"prior_receipt_verified": True})
                self._record("ROUTE_CLEARED", checkpoint, input_value=current, details={"next_route_index": checkpoint["index"] + 1})
            elif kind == "return":
                self._record("RETURNED", checkpoint, output_value=current)
            else:
                self._record("FAIL_CLOSED", checkpoint, input_value=current, details={"reason": "route_kind_invalid", "kind": kind})
                raise RouteCarrierError(f"unsupported route kind {kind}")
        self.manifest["completed"] = True
        return {
            "schema": "stegverse.manifested-route-result.v1",
            "route_manifest": deepcopy(self.manifest),
            "route_manifest_id": self.manifest["route_manifest_id"],
            "transaction_id": self.manifest["transaction_id"],
            "receipt_chain_head": self.manifest["receipt_chain_head"],
            "route_transition_count": len(self.manifest["receipt_bindings"]),
            "module_results": module_results,
            "result": current,
            "completed": True,
        }
