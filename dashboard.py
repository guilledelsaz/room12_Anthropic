"""dashboard.py: cost and volume for the Larkspur agent, from runs you actually made.

NOT part of the shipped pack. Written for Priya's first question -- what it
costs per resolved contact against the $6.90 a human contact costs Larkspur --
because the overnight review scored that answer "not supported by the
repository".

Every price, the human baseline and the volume figure are imported from
bench.py rather than restated here, so this page and the bench lane can never
disagree. bench.py is GIVEN and is not modified.

    python3 dashboard.py            # reads .workshop/, writes .workshop/dashboard.html
    python3 dashboard.py --open     # and opens it

Sources, in order of preference:
  .workshop/bench-<label>.json   the bench lane's own runs, if any exist
  .workshop/last_run.json        the five Stage 1 shapes from run.py --all

The number this prints is MODEL COST ONLY. bench.py is explicit that Larkspur's
loaded cost per resolved contact was about $0.14 against a model cost of
$0.087, so roughly 40% of the real figure is infrastructure and evals rather
than inference. The page says so in the same breath as the number.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from datetime import datetime

import bench
from support import MODEL

WORKSHOP = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".workshop")
OUT = os.path.join(WORKSHOP, "dashboard.html")


def money(x: float) -> str:
    return "$%.4f" % x if x < 0.01 else "$%.2f" % x


def cost_of(tokens_in: int, tokens_out: int, cache_read: int, price: dict) -> float:
    """Fresh input, cached input and output priced separately: the cache spread is
    the whole economic argument for the cost lever, so it is not averaged away."""
    fresh = max(tokens_in - cache_read, 0)
    return (fresh * price["input"]
            + cache_read * price["cache_read"]
            + tokens_out * price["output"]) / 1_000_000


def load_last_run() -> dict | None:
    path = os.path.join(WORKSHOP, "last_run.json")
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def load_benches() -> list[tuple[str, dict]]:
    out = []
    for path in sorted(glob.glob(os.path.join(WORKSHOP, "bench-*.json"))):
        label = os.path.basename(path)[len("bench-"):-len(".json")]
        with open(path) as fh:
            out.append((label, json.load(fh)))
    return out


def rows_from_last_run(run: dict, price: dict) -> list[dict]:
    rows = []
    for s in run.get("shapes", []):
        c = cost_of(s.get("tokens_in", 0), s.get("tokens_out", 0),
                    s.get("cache_read", 0), price)
        rows.append({
            "pnr": s.get("pnr", "?"),
            "shape": s.get("shape", "?"),
            "turns": s.get("turns", 0),
            "tools": s.get("tool_calls", 0),
            "tokens_in": s.get("tokens_in", 0),
            "tokens_out": s.get("tokens_out", 0),
            "cache_read": s.get("cache_read", 0),
            "elapsed": s.get("elapsed", 0.0),
            "resolved": bool(s.get("resolved")),
            "cost": c,
        })
    return rows


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render(rows: list[dict], price: dict, benches: list[tuple[str, dict]],
           generated: str) -> str:
    n = len(rows)
    total_cost = sum(r["cost"] for r in rows)
    per_contact = (total_cost / n) if n else 0.0
    tin = sum(r["tokens_in"] for r in rows)
    tout = sum(r["tokens_out"] for r in rows)
    tcache = sum(r["cache_read"] for r in rows)
    turns = sum(r["turns"] for r in rows)
    tools = sum(r["tools"] for r in rows)
    resolved = sum(1 for r in rows if r["resolved"])

    human = bench.HUMAN_COST
    saving = human - per_contact
    weekly = bench.WEEKLY_VOLUME
    annual_contacts = weekly * 52
    annual_agent = per_contact * annual_contacts
    annual_human = human * annual_contacts
    multiple = (human / per_contact) if per_contact else 0.0
    cache_pct = (tcache / tin * 100) if tin else 0.0
    in_share = ((tin - tcache) * price["input"] / 1_000_000 / total_cost * 100) if total_cost else 0.0

    shape_rows = "\n".join(
        '<tr><td class="m">{pnr}</td><td>{shape}</td><td class="n">{turns}</td>'
        '<td class="n">{tools}</td><td class="n">{tin:,}</td><td class="n">{tout:,}</td>'
        '<td class="n">{el:.1f}s</td><td class="n money">{cost}</td>'
        '<td class="n">{ok}</td></tr>'.format(
            pnr=esc(r["pnr"]), shape=esc(r["shape"]), turns=r["turns"], tools=r["tools"],
            tin=r["tokens_in"], tout=r["tokens_out"], el=r["elapsed"],
            cost=money(r["cost"]), ok="&check;" if r["resolved"] else "&times;")
        for r in rows)

    if benches:
        bench_rows = "\n".join(
            '<tr><td class="m">{label}</td><td class="n">{shapes}</td>'
            '<td class="n">{when}</td></tr>'.format(
                label=esc(label), shapes=len(b.get("shapes", b.get("runs", [])) or []),
                when=esc(b.get("generated", "-"))[:19])
            for label, b in benches)
        bench_block = (
            '<table><thead><tr><th>label</th><th>rows</th><th>generated</th></tr></thead>'
            '<tbody>%s</tbody></table>' % bench_rows)
    else:
        bench_block = (
            '<p class="warn"><b>No bench files yet.</b> <code>.workshop/</code> holds no '
            '<code>bench-before.json</code>. Build 4\'s gate reads a before/after pair, and '
            '<b>the baseline cannot be rebuilt once the lever has moved</b> &mdash; take it '
            'before you tune anything:<br><code>python3 bench.py --label before --runs 3</code></p>')

    return """<!doctype html>
<meta charset="utf-8">
<title>Larkspur agent &middot; cost and volume</title>
<style>
 :root {{ color-scheme: light dark; }}
 body {{ font: 15px/1.55 ui-sans-serif, system-ui, -apple-system, sans-serif;
        max-width: 1000px; margin: 2.2rem auto; padding: 0 1.2rem; }}
 h1 {{ font-size: 1.45rem; margin: 0 0 .25rem; }}
 .sub {{ opacity: .65; font-size: .87rem; margin-bottom: 1.8rem; }}
 .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
           gap: .9rem; margin-bottom: 1.8rem; }}
 .card {{ border: 1px solid color-mix(in srgb, currentColor 18%, transparent);
          border-radius: 10px; padding: .85rem .95rem; }}
 .card .k {{ font-size: .73rem; text-transform: uppercase; letter-spacing: .055em;
             opacity: .6; }}
 .card .v {{ font-size: 1.6rem; font-weight: 600; margin-top: .15rem;
             font-variant-numeric: tabular-nums; }}
 .card .f {{ font-size: .78rem; opacity: .6; margin-top: .1rem; }}
 table {{ border-collapse: collapse; width: 100%; margin: .5rem 0 1.6rem;
          font-size: .88rem; }}
 th, td {{ text-align: left; padding: .42rem .6rem;
           border-bottom: 1px solid color-mix(in srgb, currentColor 13%, transparent); }}
 th {{ font-size: .73rem; text-transform: uppercase; letter-spacing: .05em; opacity: .6;
       font-weight: 600; }}
 td.n, th.n {{ text-align: right; font-variant-numeric: tabular-nums; }}
 td.m {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .85em; }}
 tfoot td {{ font-weight: 600; border-top: 2px solid color-mix(in srgb, currentColor 30%, transparent);
             border-bottom: none; }}
 h2 {{ font-size: .95rem; text-transform: uppercase; letter-spacing: .05em;
       opacity: .75; margin: 2rem 0 .3rem; }}
 .caveat, .warn {{ border-left: 3px solid color-mix(in srgb, currentColor 35%, transparent);
            padding: .6rem .9rem; margin: 1rem 0; font-size: .87rem; opacity: .9;
            background: color-mix(in srgb, currentColor 4%, transparent); }}
 code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .88em; }}
 .money {{ font-variant-numeric: tabular-nums; }}
</style>

<h1>Larkspur disruption agent &middot; cost and volume</h1>
<div class="sub">{n} resolved contacts on the wire &middot; model <code>{model}</code>
 &middot; generated {generated}</div>

<div class="cards">
  <div class="card"><div class="k">Requests processed</div><div class="v">{n}</div>
    <div class="f">{resolved} of {n} resolved</div></div>
  <div class="card"><div class="k">Model cost / contact</div><div class="v">{per_contact}</div>
    <div class="f">vs {human} human</div></div>
  <div class="card"><div class="k">Cheaper by</div><div class="v">{multiple:.0f}&times;</div>
    <div class="f">{saving} saved per contact</div></div>
  <div class="card"><div class="k">Tokens in / out</div><div class="v">{tin_k:,}k</div>
    <div class="f">{tout:,} out &middot; {in_share:.0f}% of cost is input</div></div>
  <div class="card"><div class="k">Cache utilisation</div><div class="v">{cache_pct:.0f}%</div>
    <div class="f">{tcache:,} of {tin:,} input tokens</div></div>
  <div class="card"><div class="k">Turns / tool calls</div><div class="v">{turns} / {tools}</div>
    <div class="f">{tpc:.1f} turns per contact</div></div>
</div>

<h2>Per contact</h2>
<table>
 <thead><tr><th>pnr</th><th>shape</th><th class="n">turns</th><th class="n">tools</th>
 <th class="n">in</th><th class="n">out</th><th class="n">wall</th>
 <th class="n">model cost</th><th class="n">resolved</th></tr></thead>
 <tbody>
{shape_rows}
 </tbody>
 <tfoot><tr><td colspan="2">{n} contacts</td><td class="n">{turns}</td><td class="n">{tools}</td>
 <td class="n">{tin:,}</td><td class="n">{tout:,}</td><td class="n">&mdash;</td>
 <td class="n money">{total_cost}</td><td class="n">{resolved}/{n}</td></tr></tfoot>
</table>

<h2>At Larkspur's volume</h2>
<table>
 <thead><tr><th>basis</th><th class="n">per contact</th><th class="n">per week
 ({weekly:,})</th><th class="n">per year ({annual_contacts:,})</th></tr></thead>
 <tbody>
  <tr><td>This agent (model cost)</td><td class="n money">{per_contact}</td>
   <td class="n money">{weekly_agent}</td><td class="n money">{annual_agent}</td></tr>
  <tr><td>Human contact</td><td class="n money">{human}</td>
   <td class="n money">{weekly_human}</td><td class="n money">{annual_human}</td></tr>
 </tbody>
 <tfoot><tr><td>Gap</td><td class="n money">{saving}</td>
  <td class="n money">{weekly_gap}</td><td class="n money">{annual_gap}</td></tr></tfoot>
</table>

<div class="caveat"><b>This is model cost, not loaded cost.</b> It prices what these runs
actually consumed at <code>{model}</code>'s published rates
(in {p_in}/Mtok, out {p_out}/Mtok, cache read {p_cr}/Mtok), imported from
<code>bench.py</code> so this page and the bench lane cannot disagree.
<code>bench.py</code> records that Larkspur's <i>loaded</i> cost per resolved contact was
about $0.14 against a model cost of $0.087 &mdash; roughly 40% of the real number is
infrastructure and evals rather than inference. Quote it as model cost, or say
&ldquo;loaded, estimated&rdquo;. The volume figure of {weekly:,} chats a week is
<code>bench.py</code>'s <code>WEEKLY_VOLUME</code>; swap in Larkspur's own number before
this goes in front of a sponsor.</div>

<h2>Bench pairs</h2>
{bench_block}

<div class="caveat">Cache utilisation is <b>{cache_pct:.0f}%</b> and input is
<b>{in_share:.0f}%</b> of what each contact costs. That is the cost lever, unpulled:
every turn re-sends the nine tool schemas and the system prompt at full price.</div>
""".format(
        n=n, model=esc(MODEL), generated=esc(generated), resolved=resolved,
        per_contact=money(per_contact), human=money(human), multiple=multiple,
        saving=money(saving), tin=tin, tin_k=tin // 1000, tout=tout, tcache=tcache,
        cache_pct=cache_pct, in_share=in_share, turns=turns, tools=tools,
        tpc=(turns / n if n else 0), shape_rows=shape_rows,
        total_cost=money(total_cost), weekly=weekly, annual_contacts=annual_contacts,
        weekly_agent=money(per_contact * weekly), annual_agent=money(annual_agent),
        weekly_human=money(human * weekly), annual_human=money(annual_human),
        weekly_gap=money(saving * weekly), annual_gap=money(annual_human - annual_agent),
        p_in=money(price["input"]), p_out=money(price["output"]),
        p_cr=money(price["cache_read"]), bench_block=bench_block)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--open", action="store_true", help="open the page when written")
    args = ap.parse_args()

    run = load_last_run()
    if not run:
        print("No .workshop/last_run.json. Run this first, then come back:")
        print("  python3 run.py --all")
        return 1

    price = bench.price_for(MODEL)
    rows = rows_from_last_run(run, price)
    if not rows:
        print("last_run.json has no shapes in it. Re-run: python3 run.py --all")
        return 1

    os.makedirs(WORKSHOP, exist_ok=True)
    html = render(rows, price, load_benches(), run.get("generated", str(datetime.now())[:19]))
    with open(OUT, "w") as fh:
        fh.write(html)

    total = sum(r["cost"] for r in rows)
    print("%d contacts - model cost %s total, %s per contact, vs %s human"
          % (len(rows), money(total), money(total / len(rows)), money(bench.HUMAN_COST)))
    print("  -> %s" % OUT)
    if args.open:
        subprocess.run(["open", OUT], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
