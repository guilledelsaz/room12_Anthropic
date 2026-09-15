# Overnight review: Larkspur disruption-care agent

**To:** guilledelsaz__room12_Anthropic  
**From:** Larkspur client review agent, on behalf of Priya Raghavan  
**Re:** the disruption-care agent you walked us through in our last session  
**Generated:** 2026-09-15 12:58

## Priya's note

> Our vendor says we should just be using your best model.
>
> Why aren't we?
>
> Priya Raghavan, Larkspur Airlines

She sent that before this session opened. She means it. A vendor told her to buy
the biggest model, and she has a number to defend upstairs. Her four questions from
day one are still open. Naming a model answers none of them.

## Still open from day one

| Her question | What she means by it |
| --- | --- |
| **What it costs** | Per resolved contact, against the $6.90 a human contact costs us. |
| **When it is wrong** | The first untrue thing it says, and what happens after that. |
| **Who runs it** | In June, after you have left. |
| **What you left out** | The scope you cut, and why. |

## What the review agent found

Overnight, Larkspur pointed a review agent at your repository. It read the
code. It did not run your agent, and the only file it changed is this one. Each
item below names the file and the line it is about.

**1. agent.py's search_alternatives description was rewritten from a 6-character placeholder to 316 characters of specific guidance.**

The diff replaces the bare string "search" with a description naming option_id, flight number, departure time and seat availability, and sequencing it after get_flight_status. That is a concrete, testable claim about tool-selection quality, but nothing in the repo measures whether the model actually calls it in the right order across cases.

Run python3 eval_harness.py and paste the pass rate for cases that require search_alternatives after a confirmed disruption.

**2. tool_list() in agent.py now appends mcp_client.tools() but EXTRA_TOOLS stays at 0 and LOCAL_TOOLS has no executors.**

The diff changes return build_tools() + EXTRA_TOOLS to return build_tools() + EXTRA_TOOLS + mcp_client.tools(), wiring in MCP tools alongside the nine schemas already in build_tools(). PITCH.md's Built line claims "11-tool disruption-care agent" and "two tools served over MCP", which lines up with 9 local plus 2 MCP, but the static scan shows EXTRA_TOOLS at 0 and no LOCAL_TOOLS executors, meaning every tool beyond the shipped nine and the MCP two is still unbuilt.

Run python3 run.py --show-tools and paste the full 11-entry list to confirm the MCP two match the PITCH.md count.

**3. readout-trace.json shows a 3-turn run touching lookup_booking, get_flight_status, next_available_day, no policy or voucher tools exercised.**

The last committed wire run used 11,646 input tokens and 463 output tokens across 3 tool calls, and never reached check_policy, hold_seat, confirm_rebooking, issue_voucher or escalate_to_human. PITCH.md's Does line claims the agent "handles cancellations, delays, group escalations, and ambiguous connections end-to-end," but the only trace in evidence never exercises the confirm_rebooking token gate or the escalation path.

Run python3 run.py --all --trace and paste the tool-call list for a case that reaches confirm_rebooking and escalate_to_human.

**4. MAX_TOOL_CALLS is 8 and the loop in run_agent() now appends response.content instead of text_of(response) to the message history.**

The diff changes messages.append({"role": "assistant", "content": text_of(response)}) to messages.append({"role": "assistant", "content": response.content}), which keeps tool_use blocks in the transcript Claude sees on the next turn rather than collapsing them to text. This is a structural fix to what the model can reference mid-loop, not a capability a bigger model would supply, since the prior version discarded tool_use blocks regardless of model size.

Run python3 verify.py 1.2 to confirm this gate passes with the corrected message history.

**5. TONE_ADDENDUM is still 0 characters and PITCH.md names R8KD3F as getting a calm answer with no tone gate enforced.**

The static scan confirms TONE_ADDENDUM is empty, and PITCH.md's Still broken line states R8KD3F "gets a calm answer but no tone gate," filing it under Build 4. No eval case file exists in the repo to show how many of the five booking shapes hit this gap versus just the one named PNR.

Run python3 eval_harness.py once evals/cases.json exists and paste the count of hostile-tone cases that fail without TONE_ADDENDUM.

## Your four answers

Four of the lines in your PITCH.md are answers to me rather than to your
verifier, and somebody on your side wrote them between our sessions. I read
those beside the code, not instead of it. Where an answer is carrying a number,
I have said whether the repository backs it.

| My question | Your answer | My read |
| --- | --- | --- |
| **What it costs** | ~$0.05 per contact on the wire vs $6.90 human. At 530,000 contacts a year, the gap is roughly $3.6M. | **Not supported by the repository.** The $0.05 per contact and $3.6M gap depend on the 530,000 annual contact figure and a per-contact token cost, but readout-trace.json only shows one run's tokens (11,646 in, 463 out) and no bench-after.json or cost model ties that single trace to a per-contact average or an annual projection. |
| **When it is wrong** | A tool failure could leave a customer without an answer. Tone on hostile contacts has no gate yet, the agent stays calm but does not enforce it. | **Thin.** "A tool failure could leave a customer without an answer" names no rate, no tool, and no owner, and the tone gap is confirmed by PITCH.md's own Still broken line but has no denominator: it names one PNR, R8KD3F, not a rate across cases. |
| **Who runs it** | Guillermo Del Saz. | **Answered.** Names Guillermo Del Saz directly, matching the banked-by field in readout.html's evidence block. |
| **What you left out** | Refunds, hotel approvals, other-airline rebooking, group bookings, unaccompanied minors, baggage tracing, all still go to humans per the handbook. | **Answered.** Lists six specific out-of-scope categories, refunds, hotel approvals, other-airline rebooking, group bookings, unaccompanied minors, baggage tracing, and the escalate_to_human tool schema in agent.py corroborates that groups, partner segments and unaccompanied minors are meant to route to a human. |

All four answered. Bring the artifact behind each one to our next meeting, not the sentence.

## Before our next meeting

> Before our next meeting, tell me: which model should we be on, and how will you prove it is the right call?
>
> Priya Raghavan, Larkspur Airlines

Bring two things. A recommendation, and the measurement behind it. If the model is
not the problem, say so, and bring the number that shows it.

## What this review read

- `agent.py (237 lines)`
- `PITCH.md`
- `TEAM.md (unchanged template)`
- `readout-trace.json`
- `readout.html (evidence block)`
- `PITCH.md (4 of 4 answers to Priya)`

Reviewer: `claude-sonnet-5`. Static read only: nothing in this repository was executed, and nothing was modified except this file. Larkspur Airlines is a fictional training scenario. Confidential, do not distribute.
