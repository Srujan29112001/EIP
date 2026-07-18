"use client";

/** A soft light-field that trails the cursor across every page — the whole
 * app feels lit by your attention. Pointer-fine devices only. */

import { useEffect, useRef } from "react";

export function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!window.matchMedia("(pointer: fine)").matches) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const el = ref.current;
    if (!el) return;
    let raf = 0;
    let tx = -600, ty = -600, cx = -600, cy = -600;
    const onMove = (e: PointerEvent) => { tx = e.clientX; ty = e.clientY; };
    const loop = () => {
      cx += (tx - cx) * 0.12;
      cy += (ty - cy) * 0.12;
      el.style.transform = `translate3d(${cx - 300}px, ${cy - 300}px, 0)`;
      raf = requestAnimationFrame(loop);
    };
    window.addEventListener("pointermove", onMove, { passive: true });
    raf = requestAnimationFrame(loop);
    return () => { window.removeEventListener("pointermove", onMove); cancelAnimationFrame(raf); };
  }, []);

  return (
    <div ref={ref} aria-hidden
      className="pointer-events-none fixed left-0 top-0 z-[5] h-[600px] w-[600px] rounded-full opacity-[0.07]"
      style={{
        background: "radial-gradient(circle, #67e8f9 0%, #6d64a3 38%, transparent 68%)",
        transform: "translate3d(-600px, -600px, 0)",
        mixBlendMode: "screen",
      }}
    />
  );
}
