from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InterlockResult:
    drive_high: bool
    permit_requested: bool
    trip_latched: bool
    event: str


class DryBenchInterlock:
    """Deterministic state machine for the Phase 3 output test.

    This class does not access GPIO. Releasing the E-stop never restores a
    previous permit; the operator must reset the trip and request permit again.
    """

    def __init__(self, allow_output: bool = False) -> None:
        self.allow_output = allow_output
        self.permit_requested = False
        self.trip_latched = True
        self.estop_active = True

    @property
    def drive_high(self) -> bool:
        return bool(
            self.allow_output
            and self.permit_requested
            and not self.trip_latched
            and not self.estop_active
        )

    def result(self, event: str) -> InterlockResult:
        return InterlockResult(
            drive_high=self.drive_high,
            permit_requested=self.permit_requested,
            trip_latched=self.trip_latched,
            event=event,
        )

    def observe(self, estop_active: bool) -> InterlockResult:
        previous = self.estop_active
        self.estop_active = bool(estop_active)
        if self.estop_active:
            was_requested = self.permit_requested
            self.permit_requested = False
            self.trip_latched = True
            if not previous:
                return self.result("estop_open_forced_safe")
            if was_requested:
                return self.result("estop_active_request_cleared")
        elif previous:
            return self.result("estop_closed_reset_required")
        return self.result("")

    def command(self, command: str) -> InterlockResult:
        requested = command.strip().lower()
        if requested == "safe":
            self.permit_requested = False
            return self.result("operator_safe")
        if requested == "reset":
            self.permit_requested = False
            if self.estop_active:
                self.trip_latched = True
                return self.result("reset_rejected_estop_open")
            self.trip_latched = False
            return self.result("trip_reset_output_safe")
        if requested == "permit":
            if not self.allow_output:
                self.permit_requested = False
                return self.result("permit_rejected_monitor_only")
            if self.estop_active:
                self.permit_requested = False
                self.trip_latched = True
                return self.result("permit_rejected_estop_open")
            if self.trip_latched:
                self.permit_requested = False
                return self.result("permit_rejected_reset_required")
            self.permit_requested = True
            return self.result("permit_accepted")
        return self.result("unknown_command")
