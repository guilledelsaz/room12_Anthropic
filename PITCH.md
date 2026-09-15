# PITCH.md

Six lines and a lever. Your words. The last two are scored.

Built: An 11-tool disruption-care agent on the Claude Messages API: a verified multi-turn loop, policy-checked decisions, and two tools served over MCP.
Does: Handles cancellations, delays, group escalations, and ambiguous connections end-to-end — no 40-minute wait, no invented facts, no irreversible action without the customer's click.
Number: 530,000 disruption chats a year at $6.90 a contact. Agent cost is under $0.05 per contact on the wire.
Guardrail: confirm_rebooking requires a token only the customer's Confirm button can mint. The agent cannot book without it — structurally, not by prompt.
Next: Bench before/after, author TONE_ADDENDUM for the abusive-message gap, write and run evals against the five shapes.
Still broken: R8KD3F (abusive message) gets a calm answer but no tone gate. That is Build 4's lane.
Lever: intelligence

## Priya asked

Costs: ~$0.05 per contact on the wire vs $6.90 human. At 530,000 contacts a year, the gap is roughly $3.6M.
Wrong: A tool failure could leave a customer without an answer. Tone on hostile contacts has no gate yet — the agent stays calm but does not enforce it.
Runs it: Guillermo Del Saz.
Left out: Refunds, hotel approvals, other-airline rebooking, group bookings, unaccompanied minors, baggage tracing — all still go to humans per the handbook.
