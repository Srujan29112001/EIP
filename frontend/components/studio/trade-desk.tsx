"use client";

/** The Trade Desk — trading-specific results: setup quality, the backtests
 * that earned the signal the right to exist, and the position plan.
 * Language is deliberately educational: setups and probabilities, not calls.
 */

import { Activity, ShieldAlert, TestTubes } from "lucide-react";
import { useRun } from "@/lib/store";
import type { AgentOutput } from "@/lib/types";

interface BacktestRow {
  strategy: string; trades: number; hit_rate: number; strategy_return_pct: number;
  buy_hold_return_pct: number; max_drawdown_pct: number; sample_note: string; beats_buy_hold: boolean;
}

export function TradeDesk() {
  const outputs = useRun((s) => s.agentOutputs);
  const quant = outputs["quant_signals"] as AgentOutput | undefined;
  const risk = outputs["risk_manager"] as AgentOutput | undefined;
  const tech = outputs["technical_analyst"] as AgentOutput | undefined;
  const tests = (outputs["backtest_engineer"]?.results ?? []) as BacktestRow[];
  if (!quant) return null;

  const setup = String(quant.setup ?? "mixed");
  const setupCls = setup.includes("constructive") ? "text-ok border-ok/40 bg-ok/10"
    : setup === "deteriorating" ? "text-err border-err/40 bg-err/10"
    : "text-warn border-warn/40 bg-warn/10";

  return (
    <section className="glass card-in rounded-2xl p-4 transition hover:border-cyan/25">
      <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <Activity size={13} /> Trade desk — setup, proof, plan
      </h3>

      <div className="grid gap-3 md:grid-cols-3">
        {/* setup card */}
        <div className={`rounded-lg border p-3 ${setupCls}`}>
          <div className="font-mono text-[10px] uppercase tracking-widest opacity-70">setup quality</div>
          <div className="font-display text-xl font-bold uppercase">{setup}</div>
          <div className="mt-1 font-mono text-[10px] opacity-80">
            votes: trend {fmtVote(quant.votes, "trend")} · momentum {fmtVote(quant.votes, "momentum")} · history {fmtVote(quant.votes, "history")}
          </div>
          {tech && (
            <div className="mt-2 font-mono text-[10px] opacity-80">
              support ≈ {String(tech.support)} · resistance ≈ {String(tech.resistance)}
            </div>
          )}
        </div>

        {/* position plan */}
        <div className="rounded-lg border border-line bg-panel-2 p-3">
          <div className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-slate-500">
            <ShieldAlert size={11} /> if you traded it (plan, not advice)
          </div>
          {risk ? (
            <div className="mt-1 space-y-0.5 font-mono text-xs text-slate-300">
              <div>max size <span className="text-cyan">{String(risk.qty)}</span> shares (₹{Number(risk.position_value ?? 0).toLocaleString()})</div>
              <div>stop ≈ <span className="text-err">{String(risk.stop)}</span> (2×ATR)</div>
              <div>max loss ₹{Number(risk.max_loss ?? 0).toLocaleString()} = {String(risk.risk_pct)}% of capital</div>
            </div>
          ) : <div className="mt-1 text-xs text-slate-500">risk manager did not run</div>}
        </div>

        {/* honesty card */}
        <div className="rounded-lg border border-line bg-panel-2 p-3 text-[10px] leading-relaxed text-slate-500">
          <div className="mb-1 font-mono uppercase tracking-widest">the honest part</div>
          Backtests model no costs, slippage or taxes. A constructive setup is an edge, not a promise.
          EIP never executes and is not SEBI-registered advice — paper-trade first.
        </div>
      </div>

      {/* backtest table — the signal's proof of work */}
      {tests.length > 0 && (
        <div className="mt-3 overflow-x-auto">
          <div className="mb-1 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-slate-500">
            <TestTubes size={11} /> proof of work — this symbol&apos;s own history (2y)
          </div>
          <table className="w-full min-w-[560px] font-mono text-[11px]">
            <thead>
              <tr className="border-b border-line text-left text-slate-500">
                <th className="py-1.5 pr-2 font-normal">strategy</th>
                <th className="pr-2 font-normal">trades</th>
                <th className="pr-2 font-normal">hit rate</th>
                <th className="pr-2 font-normal">return</th>
                <th className="pr-2 font-normal">buy&amp;hold</th>
                <th className="pr-2 font-normal">max DD</th>
                <th className="font-normal">sample</th>
              </tr>
            </thead>
            <tbody>
              {tests.map((t, i) => (
                <tr key={i} className="border-b border-line/50 text-slate-300">
                  <td className="py-1.5 pr-2">{t.strategy}</td>
                  <td className="pr-2">{t.trades}</td>
                  <td className="pr-2">{t.hit_rate}%</td>
                  <td className={`pr-2 ${t.strategy_return_pct >= 0 ? "text-ok" : "text-err"}`}>
                    {t.strategy_return_pct >= 0 ? "+" : ""}{t.strategy_return_pct}%
                  </td>
                  <td className="pr-2">{t.buy_hold_return_pct >= 0 ? "+" : ""}{t.buy_hold_return_pct}%</td>
                  <td className="pr-2 text-err">{t.max_drawdown_pct}%</td>
                  <td className={t.trades < 5 ? "text-warn" : "text-slate-500"}>{t.sample_note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function fmtVote(votes: unknown, key: string): string {
  const v = (votes as Record<string, number> | undefined)?.[key] ?? 0;
  return v > 0 ? "+1" : v < 0 ? "−1" : "0";
}
